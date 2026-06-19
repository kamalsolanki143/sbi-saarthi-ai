"""
SAARTHI AI — Proactive Engagement Workflow Graph
==================================================

LangGraph sub-graph for the **MARGDARSHAN** agent's financial-advisory
and proactive-engagement flow.

Handles event-driven interactions:

• Salary credit detected  → investment / savings advice
• Subsidy credit          → linked product recommendations
• Idle balance            → FD / SIP / RD suggestions
• Loan / investment inquiries from the confidence engine

Pipeline
────────
1. ``analyse_financial_context`` — aggregate the customer's financial
   signals (salary patterns, balances, recent transactions).
2. ``generate_recommendations``  — produce personalised product
   recommendations via Gemini.
3. ``prepare_action``            — if a product action is surfaced
   (e.g. open FD, start SIP), prepare the human-in-the-loop payload.
4. ``finalise``                  — timestamp and log.

Routing rules:
• ``EventType.SALARY_CREDIT``        → this graph
• ``IntentCategory.LOAN_INQUIRY``    → this graph
• ``IntentCategory.INVESTMENT_INQUIRY`` → this graph
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from langgraph.graph import END, StateGraph

from backend.models.state import (
    AgentResponse,
    AgentType,
    EventResult,
    EventType,
    HumanInLoopAction,
    IntentCategory,
    MemoryContext,
    NetworkMode,
    PersonaType,
    Priority,
    SAARTHIState,
)
from backend.services.gemini_service import GeminiService, GeminiServiceError

# ─── Logger ─────────────────────────────────────────────────────────────────

logger = logging.getLogger("saarthi.workflows.engagement")

# ─── Prompt templates ───────────────────────────────────────────────────────

_ENGAGEMENT_SYSTEM_PROMPT: str = (
    "You are Margdarshan, the financial advisor for State Bank of India.  "
    "You provide personalised investment, savings, and loan guidance.  "
    "Always consider the customer's risk appetite, income level, and "
    "financial goals.\n\n"
    "Guidelines:\n"
    "• Be transparent about returns and risks\n"
    "• Compare multiple product options when possible\n"
    "• Use simple language appropriate for the customer's persona\n"
    "• Include specific SBI product names and current features\n"
    "• Never guarantee returns on market-linked products\n"
    "• Always mention that investments are subject to market risks "
    "where applicable"
)

_RECOMMENDATION_PROMPT_TEMPLATE: str = (
    "Customer query: \"{query}\"\n"
    "Language: {language}\n"
    "Persona: {persona}\n"
    "Event trigger: {event_type}\n"
    "Event priority: {priority}\n"
    "Financial context: {financial_context}\n"
    "Product interests: {interests}\n"
    "Previous context: {context}\n\n"
    "Provide personalised financial guidance and product recommendations.\n\n"
    "Return JSON:\n"
    '{{\n'
    '  "response": "<detailed conversational response>",\n'
    '  "recommendations": [\n'
    '    {{\n'
    '      "product": "<product name>",\n'
    '      "type": "<fd|sip|rd|loan|insurance|savings>",\n'
    '      "reason": "<why this suits the customer>",\n'
    '      "key_features": ["<feature 1>", "<feature 2>"]\n'
    '    }}\n'
    '  ],\n'
    '  "risk_disclosure": "<applicable risk disclosure>",\n'
    '  "action_available": <true|false>,\n'
    '  "action_type": "<open_fd|start_sip|apply_loan|none>",\n'
    '  "follow_up_questions": ["<question 1>"]\n'
    '}}'
)

# ─── Event-specific financial context builders ─────────────────────────────

_EVENT_CONTEXT_BUILDERS: dict[EventType, str] = {
    EventType.SALARY_CREDIT: (
        "Customer has received a salary credit.  Suggest ways to "
        "optimise savings: SIP, FD, RD, tax-saving instruments."
    ),
    EventType.SUBSIDY_CREDIT: (
        "Government subsidy credited.  Suggest safe savings instruments "
        "and insurance options appropriate for rural/semi-urban customers."
    ),
    EventType.IDLE_BALANCE_DETECTED: (
        "Customer has idle funds in their account.  Recommend FD, "
        "liquid funds, or sweep-in facility to earn better returns."
    ),
    EventType.FESTIVAL_SPENDING_DETECTED: (
        "Festival season spending detected.  Suggest EMI options, "
        "personal loans, or cashback offers."
    ),
    EventType.TRAVEL_SPENDING_DETECTED: (
        "Travel-related spending detected.  Suggest forex cards, "
        "travel insurance, and international debit card activation."
    ),
}


# ─── Graph node functions ──────────────────────────────────────────────────


def _analyse_context_node(state: SAARTHIState) -> SAARTHIState:
    """
    Aggregate financial context from event data and memory.
    """
    event_result: EventResult = state.get("event_result", EventResult())
    memory: MemoryContext = state.get("memory_context", MemoryContext())

    # Build financial context summary
    context_parts: list[str] = []

    # Event-specific context
    event_context = _EVENT_CONTEXT_BUILDERS.get(event_result.event_type, "")
    if event_context:
        context_parts.append(event_context)

    # Event metadata
    event_meta = event_result.metadata
    if event_meta:
        for key, value in event_meta.items():
            if key not in ("source", "matched_keyword"):
                context_parts.append(f"{key}: {value}")

    # Behavioural signals from memory
    behavioral = memory.behavioral_context
    if isinstance(behavioral, dict):
        for key in ("income_range", "risk_appetite", "savings_pattern"):
            if key in behavioral:
                context_parts.append(f"{key}: {behavioral[key]}")

    financial_context = "; ".join(context_parts) if context_parts else "none"

    # Store in behavioral_context for downstream nodes
    if hasattr(memory, "behavioral_context"):
        memory.behavioral_context["financial_context"] = financial_context
        state["memory_context"] = memory

    logger.info(
        "Financial context analysed",
        extra={
            "customer_id": state.get("customer_id"),
            "event": event_result.event_type.value,
            "context_length": len(financial_context),
        },
    )

    return state


async def _generate_recommendations_node(
    state: SAARTHIState,
    gemini_service: GeminiService,
) -> SAARTHIState:
    """Generate personalised financial recommendations via Gemini."""
    memory: MemoryContext = state.get("memory_context", MemoryContext())
    event_result: EventResult = state.get("event_result", EventResult())
    persona = state.get("persona", PersonaType.UNKNOWN)
    persona_str = persona.value if hasattr(persona, "value") else str(persona)
    intent = state.get("intent", IntentCategory.GENERAL_INQUIRY)
    intent_str = intent.value if hasattr(intent, "value") else str(intent)

    financial_context = memory.behavioral_context.get(
        "financial_context", "none"
    )

    context_parts: list[str] = []
    for turn in memory.conversation_history[-3:]:
        content = turn.get("parts", turn.get("content", ""))
        if content:
            context_parts.append(content)

    prompt = _RECOMMENDATION_PROMPT_TEMPLATE.format(
        query=state.get("query", ""),
        language=state.get("language", "en"),
        persona=persona_str,
        event_type=event_result.event_type.value,
        priority=event_result.priority.value,
        financial_context=financial_context,
        interests=", ".join(memory.product_interests) or "none",
        context="; ".join(context_parts) if context_parts else "none",
    )

    try:
        result: dict[str, Any] = await gemini_service.generate_structured(
            prompt=prompt,
            system_instruction=_ENGAGEMENT_SYSTEM_PROMPT,
            temperature=0.3,
            network_mode=state.get("network_mode", NetworkMode.TEXT_MODE),
        )

        response_text: str = result.get("response", "")
        recommendations: list[dict[str, Any]] = result.get("recommendations", [])
        risk_disclosure: str = result.get("risk_disclosure", "")
        action_available: bool = result.get("action_available", False)
        action_type: str = result.get("action_type", "none")
        follow_ups: list[str] = result.get("follow_up_questions", [])

        # Append risk disclosure if present
        if risk_disclosure and response_text:
            response_text = f"{response_text}\n\n⚠️ {risk_disclosure}"

        state["response"] = response_text

        agent_response = AgentResponse(
            agent=AgentType.MARGDARSHAN,
            response_text=response_text,
            recommendations=recommendations,
            follow_up_questions=follow_ups,
            confidence=state.get("confidence", 0.0),
            metadata={
                "event_trigger": event_result.event_type.value,
                "action_type": action_type,
            },
        )

        # Human-in-the-loop for product actions
        if action_available and action_type != "none":
            action = HumanInLoopAction(
                action_type=action_type,
                action_preview={
                    "type": action_type,
                    "recommendations": [
                        r.get("product", "") for r in recommendations[:3]
                    ],
                    "message": f"Would you like to proceed with {action_type.replace('_', ' ')}?",
                },
                requires_human_confirmation=True,
                requires_mpin=action_type in ("open_fd", "start_sip"),
            )
            agent_response.action_required = action
            state["action_required"] = action

        state["agent_response"] = agent_response

    except GeminiServiceError as exc:
        logger.error(
            "Engagement recommendation LLM call failed",
            extra={"error": str(exc)},
        )
        state["response"] = (
            "I'd love to help you with financial planning!  Based on "
            "your account activity, here are some options I can help with:\n\n"
            "💰 Fixed Deposits — safe, guaranteed returns\n"
            "📈 SBI SIP Plans — systematic investment for long-term growth\n"
            "🏦 Recurring Deposits — disciplined monthly savings\n"
            "🛡️ Insurance — protect your family's future\n\n"
            "Which option interests you?  I can provide detailed information."
        )
        state["agent_response"] = AgentResponse(
            agent=AgentType.MARGDARSHAN,
            response_text=state["response"],
            confidence=state.get("confidence", 0.0),
        )

    return state


def _should_prepare_action(state: SAARTHIState) -> str:
    """Conditional edge: check if a product action needs preparation."""
    action = state.get("action_required")
    if action is not None:
        return "prepare_action"
    return "finalise"


def _prepare_action_node(state: SAARTHIState) -> SAARTHIState:
    """
    Enrich the action payload with compliance disclosures and
    security requirements.
    """
    action = state.get("action_required")
    if action is not None:
        current_response = state.get("response", "")

        action_notice = "\n\n"
        if action.action_type in ("open_fd", "start_sip"):
            action_notice += (
                "🔐 To proceed, you'll need to verify your identity "
                "using MPIN.  The transaction will be processed through "
                "SBI's secure banking platform."
            )
        elif action.action_type == "apply_loan":
            action_notice += (
                "📋 I'll help you start the loan application.  You may "
                "need to provide income proof and address verification.  "
                "Would you like to proceed?"
            )
        else:
            action_notice += (
                "✅ Would you like me to help you get started with this?  "
                "I can guide you through the process step by step."
            )

        state["response"] = f"{current_response}{action_notice}"

        logger.info(
            "Product action prepared",
            extra={
                "customer_id": state.get("customer_id"),
                "action_type": action.action_type,
            },
        )

    return state


def _finalise_node(state: SAARTHIState) -> SAARTHIState:
    """Final state cleanup."""
    state["timestamp"] = datetime.now(timezone.utc)
    logger.info(
        "Engagement workflow completed",
        extra={
            "customer_id": state.get("customer_id"),
            "has_action": state.get("action_required") is not None,
        },
    )
    return state


# ─── Graph builder ──────────────────────────────────────────────────────────


def build_engagement_graph(
    gemini_service: GeminiService,
) -> StateGraph:
    """
    Construct the proactive-engagement LangGraph sub-graph.

    Parameters
    ----------
    gemini_service : GeminiService
        Shared Gemini API client.

    Returns
    -------
    StateGraph
        Compiled graph ready for invocation.
    """

    async def generate_recommendations(state: SAARTHIState) -> SAARTHIState:
        return await _generate_recommendations_node(state, gemini_service)

    graph = StateGraph(SAARTHIState)

    # ── Add nodes ──────────────────────────────────────────────────────
    graph.add_node("analyse_context", _analyse_context_node)
    graph.add_node("generate_recommendations", generate_recommendations)
    graph.add_node("prepare_action", _prepare_action_node)
    graph.add_node("finalise", _finalise_node)

    # ── Set entry point ────────────────────────────────────────────────
    graph.set_entry_point("analyse_context")

    # ── Add edges ──────────────────────────────────────────────────────
    graph.add_edge("analyse_context", "generate_recommendations")
    graph.add_conditional_edges(
        "generate_recommendations",
        _should_prepare_action,
        {
            "prepare_action": "prepare_action",
            "finalise": "finalise",
        },
    )
    graph.add_edge("prepare_action", "finalise")
    graph.add_edge("finalise", END)

    logger.info("Engagement graph built")
    return graph
