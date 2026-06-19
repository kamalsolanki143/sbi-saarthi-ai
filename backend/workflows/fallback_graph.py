"""
SAARTHI AI — Fallback Workflow Graph
======================================

LangGraph sub-graph that activates when no specialist agent can
confidently handle the customer's request (confidence < 85%).

Responsibilities
────────────────
1. **Disambiguate intent** — ask clarifying questions to narrow down
   the customer's need.
2. **Suggest options** — present a menu of services the customer
   might be looking for.
3. **Escalate to human** — if after clarification the system still
   cannot resolve, prepare a human-agent hand-off.
4. **Network fallback** — if the customer is in LOW_BANDWIDTH_MODE,
   provide minimal but actionable guidance.

The fallback graph is intentionally conservative: it never executes
financial transactions and always prefers to clarify rather than
guess.

Pipeline
────────
1. ``assess_situation``    — evaluate why the request landed here
                             (low confidence, unknown intent, error).
2. ``generate_clarification`` — produce a helpful clarifying response.
3. ``check_escalation``    — decide if human escalation is needed.
4. ``escalate`` (optional) — prepare the hand-off payload.
5. ``finalise``            — timestamp and log.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from langgraph.graph import END, StateGraph

from backend.models.state import (
    AgentResponse,
    AgentType,
    ConfidenceResult,
    GuardrailStatus,
    HumanInLoopAction,
    IntentCategory,
    MemoryContext,
    NetworkMode,
    SAARTHIState,
)
from backend.services.gemini_service import GeminiService, GeminiServiceError

# ─── Logger ─────────────────────────────────────────────────────────────────

logger = logging.getLogger("saarthi.workflows.fallback")

# ─── Thresholds ─────────────────────────────────────────────────────────────

_ESCALATION_CONFIDENCE_FLOOR: float = 40.0
_MAX_FALLBACK_TURNS: int = 3

# ─── Prompt templates ───────────────────────────────────────────────────────

_FALLBACK_SYSTEM_PROMPT: str = (
    "You are the fallback assistant for State Bank of India's AI system.  "
    "The customer's request could not be confidently classified.  Your "
    "goal is to:\n"
    "1. Politely acknowledge the customer's query\n"
    "2. Ask ONE clear clarifying question to understand their need\n"
    "3. Suggest 2-3 relevant service categories they might be looking for\n"
    "4. Offer to connect them with a human agent if preferred\n\n"
    "Be warm, patient, and never make the customer feel their question "
    "was wrong.  Use simple language appropriate for all literacy levels."
)

_CLARIFICATION_PROMPT_TEMPLATE: str = (
    "Customer query: \"{query}\"\n"
    "Language: {language}\n"
    "Detected intent (low confidence): {intent} ({confidence}%)\n"
    "Fallback reason: {reason}\n"
    "Interaction count in this session: {interaction_count}\n"
    "Previous context: {context}\n"
    "Network mode: {network_mode}\n\n"
    "Generate a helpful clarifying response.\n\n"
    "Return JSON:\n"
    '{{\n'
    '  "response": "<warm, clarifying response>",\n'
    '  "suggested_services": ["<service 1>", "<service 2>", "<service 3>"],\n'
    '  "clarifying_question": "<one clear question>",\n'
    '  "should_escalate": <true|false>,\n'
    '  "escalation_reason": "<reason if escalating>"\n'
    '}}'
)

_LOW_BANDWIDTH_FALLBACK: str = (
    "I didn't fully understand your request.  "
    "Reply with a number:\n"
    "1. Account help\n"
    "2. Money transfer\n"
    "3. Loan info\n"
    "4. Bill payment\n"
    "5. Talk to agent\n"
)


# ─── Fallback reason determination ─────────────────────────────────────────


def _determine_fallback_reason(state: SAARTHIState) -> str:
    """Determine why the request fell through to fallback."""
    confidence: float = state.get("confidence", 0.0)
    intent = state.get("intent", IntentCategory.UNKNOWN)
    error: str | None = state.get("error")

    if error:
        return f"Pipeline error: {error}"
    if intent == IntentCategory.UNKNOWN:
        return "Intent could not be determined"
    if confidence < _ESCALATION_CONFIDENCE_FLOOR:
        return f"Very low confidence ({confidence:.1f}%)"
    return f"Confidence below threshold ({confidence:.1f}% < 85%)"


# ─── Graph node functions ──────────────────────────────────────────────────


def _assess_situation_node(state: SAARTHIState) -> SAARTHIState:
    """
    Evaluate the fallback situation and determine the approach.
    """
    reason = _determine_fallback_reason(state)
    memory: MemoryContext = state.get("memory_context", MemoryContext())
    network_mode: NetworkMode = state.get("network_mode", NetworkMode.TEXT_MODE)

    # Count how many fallback turns have occurred this session
    fallback_count = memory.behavioral_context.get("fallback_count", 0) + 1
    if hasattr(memory, "behavioral_context"):
        memory.behavioral_context["fallback_count"] = fallback_count
        memory.behavioral_context["fallback_reason"] = reason
        state["memory_context"] = memory

    logger.info(
        "Fallback situation assessed",
        extra={
            "customer_id": state.get("customer_id"),
            "reason": reason,
            "fallback_count": fallback_count,
            "network_mode": network_mode.value,
            "confidence": state.get("confidence", 0.0),
        },
    )

    return state


async def _generate_clarification_node(
    state: SAARTHIState,
    gemini_service: GeminiService,
) -> SAARTHIState:
    """
    Generate a clarifying response to help narrow down the customer's
    intent.
    """
    memory: MemoryContext = state.get("memory_context", MemoryContext())
    network_mode: NetworkMode = state.get("network_mode", NetworkMode.TEXT_MODE)
    confidence: float = state.get("confidence", 0.0)
    intent = state.get("intent", IntentCategory.UNKNOWN)
    intent_str = intent.value if hasattr(intent, "value") else str(intent)
    reason = memory.behavioral_context.get("fallback_reason", "unknown")
    fallback_count = memory.behavioral_context.get("fallback_count", 1)

    # ── Low-bandwidth fast path ────────────────────────────────────────
    if network_mode == NetworkMode.LOW_BANDWIDTH_MODE:
        state["response"] = _LOW_BANDWIDTH_FALLBACK
        state["agent_response"] = AgentResponse(
            agent=AgentType.FALLBACK,
            response_text=_LOW_BANDWIDTH_FALLBACK,
            confidence=confidence,
            metadata={"mode": "low_bandwidth_fallback"},
        )
        logger.info("Low-bandwidth fallback response generated")
        return state

    # ── Repeated fallback → auto-escalate ─────────────────────────────
    if fallback_count >= _MAX_FALLBACK_TURNS:
        state["response"] = (
            "I apologize for the difficulty.  Let me connect you with "
            "one of our banking specialists who can help you right away.  "
            "Please hold on — a human agent will be with you shortly."
        )
        state["agent_response"] = AgentResponse(
            agent=AgentType.FALLBACK,
            response_text=state["response"],
            confidence=confidence,
            metadata={"auto_escalated": True, "fallback_count": fallback_count},
        )
        state["action_required"] = HumanInLoopAction(
            action_type="human_escalation",
            action_preview={
                "reason": f"Customer reached {fallback_count} fallback turns",
                "original_query": state.get("query", ""),
            },
            requires_human_confirmation=False,
        )
        state["guardrail_status"] = GuardrailStatus.ESCALATED
        logger.warning(
            "Auto-escalating after repeated fallbacks",
            extra={
                "customer_id": state.get("customer_id"),
                "fallback_count": fallback_count,
            },
        )
        return state

    # ── LLM clarification ─────────────────────────────────────────────
    context_parts: list[str] = []
    for turn in memory.conversation_history[-3:]:
        content = turn.get("parts", turn.get("content", ""))
        if content:
            context_parts.append(content)

    prompt = _CLARIFICATION_PROMPT_TEMPLATE.format(
        query=state.get("query", ""),
        language=state.get("language", "en"),
        intent=intent_str,
        confidence=confidence,
        reason=reason,
        interaction_count=memory.interaction_count,
        context="; ".join(context_parts) if context_parts else "none",
        network_mode=network_mode.value,
    )

    try:
        result: dict[str, Any] = await gemini_service.generate_structured(
            prompt=prompt,
            system_instruction=_FALLBACK_SYSTEM_PROMPT,
            temperature=0.5,
            network_mode=network_mode,
        )

        response_text: str = result.get("response", "")
        suggested_services: list[str] = result.get("suggested_services", [])
        clarifying_question: str = result.get("clarifying_question", "")
        should_escalate: bool = result.get("should_escalate", False)
        escalation_reason: str = result.get("escalation_reason", "")

        # Append clarifying question if not already in response
        if clarifying_question and clarifying_question not in response_text:
            response_text = f"{response_text}\n\n❓ {clarifying_question}"

        state["response"] = response_text

        agent_response = AgentResponse(
            agent=AgentType.FALLBACK,
            response_text=response_text,
            follow_up_questions=[clarifying_question] if clarifying_question else [],
            confidence=confidence,
            metadata={
                "suggested_services": suggested_services,
                "fallback_reason": reason,
                "fallback_count": fallback_count,
            },
        )

        # Handle escalation recommendation from LLM
        if should_escalate:
            action = HumanInLoopAction(
                action_type="human_escalation",
                action_preview={
                    "reason": escalation_reason or reason,
                    "original_query": state.get("query", ""),
                    "suggested_services": suggested_services,
                },
                requires_human_confirmation=False,
            )
            agent_response.action_required = action
            state["action_required"] = action
            state["guardrail_status"] = GuardrailStatus.ESCALATED

        state["agent_response"] = agent_response

    except GeminiServiceError as exc:
        logger.error(
            "Fallback clarification LLM call failed",
            extra={"error": str(exc)},
        )
        state["response"] = (
            "I'm sorry, I didn't quite understand your request.  "
            "Could you please tell me what you need help with?\n\n"
            "I can assist you with:\n"
            "🏦 Account services (opening, balance, statements)\n"
            "💸 Money transfers (UPI, NEFT, IMPS)\n"
            "📱 Digital banking (YONO, internet banking)\n"
            "💰 Loans and investments\n"
            "📞 Or I can connect you with a human agent\n\n"
            "Just type what you need!"
        )
        state["agent_response"] = AgentResponse(
            agent=AgentType.FALLBACK,
            response_text=state["response"],
            confidence=confidence,
        )

    return state


def _should_escalate(state: SAARTHIState) -> str:
    """Conditional edge: check if escalation is needed."""
    guardrail = state.get("guardrail_status", GuardrailStatus.PASSED)
    action = state.get("action_required")

    if guardrail == GuardrailStatus.ESCALATED or (
        action is not None and action.action_type == "human_escalation"
    ):
        return "escalate"
    return "finalise"


def _escalate_node(state: SAARTHIState) -> SAARTHIState:
    """
    Prepare the human-agent escalation payload.

    Collects all relevant context so the human agent can pick up
    the conversation seamlessly.
    """
    memory: MemoryContext = state.get("memory_context", MemoryContext())

    escalation_context: dict[str, Any] = {
        "customer_id": state.get("customer_id", ""),
        "session_id": state.get("session_id", ""),
        "original_query": state.get("query", ""),
        "detected_intent": (
            state.get("intent", IntentCategory.UNKNOWN).value
            if hasattr(state.get("intent", IntentCategory.UNKNOWN), "value")
            else str(state.get("intent", "unknown"))
        ),
        "confidence": state.get("confidence", 0.0),
        "language": state.get("language", "en"),
        "fallback_count": memory.behavioral_context.get("fallback_count", 0),
        "conversation_summary": _summarise_history(memory.conversation_history),
    }

    # Update action with full context
    action = state.get("action_required")
    if action is not None:
        action.action_preview["escalation_context"] = escalation_context

    current_response = state.get("response", "")
    if "human agent" not in current_response.lower():
        state["response"] = (
            f"{current_response}\n\n"
            "👤 I'm connecting you with a human agent now.  They'll "
            "have the full context of our conversation.  Please stay "
            "on the line."
        )

    logger.info(
        "Escalation prepared",
        extra={
            "customer_id": state.get("customer_id"),
            "session_id": state.get("session_id"),
            "fallback_count": escalation_context["fallback_count"],
        },
    )

    return state


def _finalise_node(state: SAARTHIState) -> SAARTHIState:
    """Final state cleanup."""
    state["timestamp"] = datetime.now(timezone.utc)
    logger.info(
        "Fallback workflow completed",
        extra={
            "customer_id": state.get("customer_id"),
            "escalated": state.get("guardrail_status") == GuardrailStatus.ESCALATED,
        },
    )
    return state


# ─── Helpers ────────────────────────────────────────────────────────────────


def _summarise_history(history: list[dict[str, str]]) -> str:
    """Create a brief summary of conversation history for escalation."""
    if not history:
        return "No prior conversation"

    recent = history[-5:]
    lines: list[str] = []
    for turn in recent:
        role = turn.get("role", "unknown")
        content = turn.get("content", turn.get("parts", ""))
        if content:
            truncated = content[:100] + "..." if len(content) > 100 else content
            lines.append(f"{role}: {truncated}")

    return " | ".join(lines)


# ─── Graph builder ──────────────────────────────────────────────────────────


def build_fallback_graph(
    gemini_service: GeminiService,
) -> StateGraph:
    """
    Construct the fallback LangGraph sub-graph.

    Parameters
    ----------
    gemini_service : GeminiService
        Shared Gemini API client.

    Returns
    -------
    StateGraph
        Compiled graph ready for invocation.
    """

    async def generate_clarification(state: SAARTHIState) -> SAARTHIState:
        return await _generate_clarification_node(state, gemini_service)

    graph = StateGraph(SAARTHIState)

    # ── Add nodes ──────────────────────────────────────────────────────
    graph.add_node("assess_situation", _assess_situation_node)
    graph.add_node("generate_clarification", generate_clarification)
    graph.add_node("escalate", _escalate_node)
    graph.add_node("finalise", _finalise_node)

    # ── Set entry point ────────────────────────────────────────────────
    graph.set_entry_point("assess_situation")

    # ── Add edges ──────────────────────────────────────────────────────
    graph.add_edge("assess_situation", "generate_clarification")
    graph.add_conditional_edges(
        "generate_clarification",
        _should_escalate,
        {
            "escalate": "escalate",
            "finalise": "finalise",
        },
    )
    graph.add_edge("escalate", "finalise")
    graph.add_edge("finalise", END)

    logger.info("Fallback graph built")
    return graph
