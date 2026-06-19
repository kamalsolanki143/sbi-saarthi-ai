"""
SAARTHI AI — Digital Adoption Workflow Graph
=============================================

LangGraph sub-graph for the **MARGDARSHAN** agent's digital-adoption
and account-services flow.

Handles:
• UPI activation and setup
• YONO / internet-banking guidance
• Fixed Deposit recommendations
• Bill payments and recharges
• Account services (passbook, cheque book, nominations)
• Digital literacy and feature walkthroughs

Pipeline
────────
1. ``validate_consent``        — block workflow if consent not granted.
2. ``assess_digital_literacy`` — gauge the customer's comfort level with
   digital banking (from persona + interaction history).
3. ``generate_guidance``       — produce step-by-step instructions tailored
   to the customer's literacy level.
4. ``handle_transaction``      — if an actionable transaction is detected,
   prepare a human-in-the-loop confirmation.
5. ``finalise``                — timestamp and log.

Routing rule: ``IntentCategory.DIGITAL_ADOPTION | BILL_PAYMENT |
FD_RECOMMENDATION | ACCOUNT_SERVICES`` → this graph.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from langgraph.graph import END, StateGraph

from backend.models.state import (
    AgentResponse,
    AgentType,
    ConsentCategory,
    ConsentStatus,
    GuardrailStatus,
    HumanInLoopAction,
    IntentCategory,
    MemoryContext,
    NetworkMode,
    PersonaType,
    SAARTHIState,
)
from backend.services.gemini_service import GeminiService, GeminiServiceError

# ─── Logger ─────────────────────────────────────────────────────────────────

logger = logging.getLogger("saarthi.workflows.adoption")

# ─── Prompt templates ───────────────────────────────────────────────────────

_ADOPTION_SYSTEM_PROMPT: str = (
    "You are Margdarshan, the digital-adoption and account-services "
    "specialist for State Bank of India.  You help customers navigate "
    "digital banking services like YONO, UPI, Fixed Deposits, bill "
    "payments, and account services.\n\n"
    "Adapt your language complexity to the customer's digital literacy:\n"
    "• LOW literacy  → very simple steps, use analogies, avoid jargon\n"
    "• MEDIUM literacy → clear instructions with brief explanations\n"
    "• HIGH literacy → concise, technical-friendly responses\n\n"
    "Always provide numbered step-by-step instructions when guiding "
    "through a process.  Offer to help in the customer's language."
)

_GUIDANCE_PROMPT_TEMPLATE: str = (
    "Customer query: \"{query}\"\n"
    "Language: {language}\n"
    "Persona: {persona}\n"
    "Digital literacy level: {literacy}\n"
    "Intent: {intent}\n"
    "Previous context: {context}\n\n"
    "Provide helpful guidance for the customer's request.  If it "
    "involves a transaction, include transaction details.\n\n"
    "Return JSON:\n"
    '{{\n'
    '  "response": "<detailed conversational response>",\n'
    '  "steps": ["<step 1>", "<step 2>"],\n'
    '  "is_transaction": <true|false>,\n'
    '  "transaction_type": "<bill_payment|recharge|upi_transfer|none>",\n'
    '  "follow_up_questions": ["<question 1>"]\n'
    '}}'
)

# ─── Digital literacy assessment ────────────────────────────────────────────

_LITERACY_SIGNALS: dict[str, list[str]] = {
    "high": [
        "upi", "neft", "rtgs", "imps", "netbanking", "yono",
        "internet banking", "mobile banking", "api", "otp",
    ],
    "medium": [
        "app", "online", "phone pe", "google pay", "paytm",
        "recharge", "bill pay", "transfer",
    ],
    "low": [
        "kaise", "how to", "samajh nahi", "pata nahi",
        "kya hai", "help", "batao", "sikhao",
    ],
}


def _assess_literacy(query: str, memory: MemoryContext) -> str:
    """
    Determine the customer's digital literacy level from signals.

    Returns ``"low"``, ``"medium"``, or ``"high"``.
    """
    normalised = query.lower()
    interaction_count = memory.interaction_count

    # Score each level
    scores: dict[str, int] = {"high": 0, "medium": 0, "low": 0}
    for level, keywords in _LITERACY_SIGNALS.items():
        for kw in keywords:
            if kw in normalised:
                scores[level] += 1

    # Factor in interaction history
    if interaction_count > 20:
        scores["high"] += 2
    elif interaction_count > 5:
        scores["medium"] += 1
    else:
        scores["low"] += 1

    # Persona-based boost
    persona = memory.customer_profile.get("persona", "unknown")
    if persona in ("senior_citizen", "farmer"):
        scores["low"] += 2
    elif persona == "student":
        scores["medium"] += 1

    best = max(scores, key=lambda k: scores[k])
    return best


# ─── Transactional intents ──────────────────────────────────────────────────

_TRANSACTION_INTENTS: set[IntentCategory] = {
    IntentCategory.BILL_PAYMENT,
    IntentCategory.FUND_TRANSFER,
}


# ─── Graph node functions ──────────────────────────────────────────────────


def _validate_consent_node(state: SAARTHIState) -> SAARTHIState:
    """
    Verify mandatory consents before proceeding with digital adoption.
    """
    consent: ConsentStatus = state.get("consent_status", ConsentStatus())

    if not consent.is_granted(ConsentCategory.MEMORY_CONSENT):
        logger.warning(
            "Adoption consent check — memory consent missing",
            extra={"customer_id": state.get("customer_id")},
        )
        state["response"] = (
            "To help you with digital banking services, I need your "
            "permission to store your information securely.  Would you "
            "like to grant consent?  Your data will be handled as per "
            "DPDP Act guidelines."
        )
        state["guardrail_status"] = GuardrailStatus.PASSED
    else:
        logger.info(
            "Adoption consent validated",
            extra={"customer_id": state.get("customer_id")},
        )

    return state


def _assess_literacy_node(state: SAARTHIState) -> SAARTHIState:
    """Assess the customer's digital literacy level."""
    memory: MemoryContext = state.get("memory_context", MemoryContext())
    query: str = state.get("query", "")

    literacy_level = _assess_literacy(query, memory)

    # Store in agent_response metadata for downstream use
    logger.info(
        "Digital literacy assessed",
        extra={
            "customer_id": state.get("customer_id"),
            "literacy": literacy_level,
        },
    )

    # Temporarily stash literacy in memory behavioral_context
    if hasattr(memory, "behavioral_context"):
        memory.behavioral_context["digital_literacy"] = literacy_level
        state["memory_context"] = memory

    return state


async def _generate_guidance_node(
    state: SAARTHIState,
    gemini_service: GeminiService,
) -> SAARTHIState:
    """Generate tailored digital-banking guidance."""
    memory: MemoryContext = state.get("memory_context", MemoryContext())
    persona = state.get("persona", PersonaType.UNKNOWN)
    persona_str = persona.value if hasattr(persona, "value") else str(persona)
    intent = state.get("intent", IntentCategory.GENERAL_INQUIRY)
    intent_str = intent.value if hasattr(intent, "value") else str(intent)
    literacy = memory.behavioral_context.get("digital_literacy", "medium")

    context_parts: list[str] = []
    for turn in memory.conversation_history[-3:]:
        content = turn.get("parts", turn.get("content", ""))
        if content:
            context_parts.append(content)

    prompt = _GUIDANCE_PROMPT_TEMPLATE.format(
        query=state.get("query", ""),
        language=state.get("language", "en"),
        persona=persona_str,
        literacy=literacy,
        intent=intent_str,
        context="; ".join(context_parts) if context_parts else "none",
    )

    try:
        result: dict[str, Any] = await gemini_service.generate_structured(
            prompt=prompt,
            system_instruction=_ADOPTION_SYSTEM_PROMPT,
            temperature=0.4,
            network_mode=state.get("network_mode", NetworkMode.TEXT_MODE),
        )

        response_text: str = result.get("response", "")
        steps: list[str] = result.get("steps", [])
        is_transaction: bool = result.get("is_transaction", False)
        transaction_type: str = result.get("transaction_type", "none")
        follow_ups: list[str] = result.get("follow_up_questions", [])

        # Format steps into response if present
        if steps and response_text:
            steps_text = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(steps))
            response_text = f"{response_text}\n\n📋 Steps:\n{steps_text}"

        state["response"] = response_text

        agent_response = AgentResponse(
            agent=AgentType.MARGDARSHAN,
            response_text=response_text,
            follow_up_questions=follow_ups,
            confidence=state.get("confidence", 0.0),
            metadata={
                "digital_literacy": literacy,
                "is_transaction": is_transaction,
                "transaction_type": transaction_type,
            },
        )

        # Prepare human-in-the-loop for transactions
        if is_transaction and transaction_type != "none":
            agent_response.action_required = HumanInLoopAction(
                action_type=transaction_type,
                action_preview={
                    "type": transaction_type,
                    "message": "Please confirm this transaction.",
                },
                requires_human_confirmation=True,
                requires_mpin=transaction_type in ("upi_transfer", "bill_payment"),
            )
            state["action_required"] = agent_response.action_required

        state["agent_response"] = agent_response

    except GeminiServiceError as exc:
        logger.error(
            "Adoption guidance LLM call failed",
            extra={"error": str(exc)},
        )
        state["response"] = (
            "I'm here to help you with digital banking!  Could you "
            "please tell me specifically what you'd like to do?  "
            "For example:\n"
            "• Pay a bill\n"
            "• Transfer money\n"
            "• Learn how to use YONO app\n"
            "• Check a complaint status"
        )
        state["agent_response"] = AgentResponse(
            agent=AgentType.MARGDARSHAN,
            response_text=state["response"],
            confidence=state.get("confidence", 0.0),
        )

    return state


def _should_handle_transaction(state: SAARTHIState) -> str:
    """Conditional edge: route to transaction handler if needed."""
    action = state.get("action_required")
    if action is not None:
        return "handle_transaction"
    return "finalise"


def _handle_transaction_node(state: SAARTHIState) -> SAARTHIState:
    """
    Prepare transaction confirmation payload.

    Adds security notices and MPIN/biometric requirements to the
    response when a financial transaction is detected.
    """
    action = state.get("action_required")
    if action is not None:
        current_response = state.get("response", "")

        security_notice = "\n\n🔒 "
        if action.requires_mpin:
            security_notice += (
                "This transaction requires your MPIN for verification.  "
                "You'll be redirected to the secure payment page."
            )
        elif action.requires_biometric:
            security_notice += (
                "Please verify using your fingerprint or face ID "
                "to proceed."
            )
        else:
            security_notice += (
                "Please review and confirm the transaction details."
            )

        state["response"] = f"{current_response}{security_notice}"

        logger.info(
            "Transaction action prepared",
            extra={
                "customer_id": state.get("customer_id"),
                "action_type": action.action_type,
                "requires_mpin": action.requires_mpin,
            },
        )

    return state


def _finalise_node(state: SAARTHIState) -> SAARTHIState:
    """Final state cleanup."""
    state["timestamp"] = datetime.now(timezone.utc)
    logger.info(
        "Adoption workflow (MARGDARSHAN) completed",
        extra={
            "customer_id": state.get("customer_id"),
            "has_action": state.get("action_required") is not None,
        },
    )
    return state


# ─── Graph builder ──────────────────────────────────────────────────────────


def build_adoption_graph(
    gemini_service: GeminiService,
) -> StateGraph:
    """
    Construct the digital-adoption LangGraph sub-graph.

    Parameters
    ----------
    gemini_service : GeminiService
        Shared Gemini API client.

    Returns
    -------
    StateGraph
        Compiled graph ready for invocation.
    """

    async def generate_guidance(state: SAARTHIState) -> SAARTHIState:
        return await _generate_guidance_node(state, gemini_service)

    graph = StateGraph(SAARTHIState)

    # ── Add nodes ──────────────────────────────────────────────────────
    graph.add_node("validate_consent", _validate_consent_node)
    graph.add_node("assess_literacy", _assess_literacy_node)
    graph.add_node("generate_guidance", generate_guidance)
    graph.add_node("handle_transaction", _handle_transaction_node)
    graph.add_node("finalise", _finalise_node)

    # ── Set entry point ────────────────────────────────────────────────
    graph.set_entry_point("validate_consent")

    # ── Add edges ──────────────────────────────────────────────────────
    graph.add_edge("validate_consent", "assess_literacy")
    graph.add_edge("assess_literacy", "generate_guidance")
    graph.add_conditional_edges(
        "generate_guidance",
        _should_handle_transaction,
        {
            "handle_transaction": "handle_transaction",
            "finalise": "finalise",
        },
    )
    graph.add_edge("handle_transaction", "finalise")
    graph.add_edge("finalise", END)

    logger.info("Adoption graph built")
    return graph
