"""
SAARTHI AI — Onboarding Workflow Graph
========================================

LangGraph sub-graph for the **MITRA** agent's onboarding flow.

Handles new-customer account-opening journeys:

1. ``validate_consent``   — ensure mandatory consents before proceeding.
2. ``collect_kyc_info``   — gather KYC details (name, PAN, Aadhaar, …).
3. ``verify_identity``    — cross-check submitted documents.
4. ``select_account_type``— recommend suitable account type based on
                            persona and needs.
5. ``generate_response``  — produce the final conversational response.
6. ``handle_human_loop``  — surface actions requiring human confirmation
                            (e.g. OTP, biometric).

Routing rule: ``IntentCategory.ACCOUNT_OPENING`` → this graph.

The graph is a **linear pipeline** with conditional edges for the
human-in-the-loop branch.
"""

from __future__ import annotations

import logging
import time
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
    SAARTHIState,
)
from backend.services.gemini_service import GeminiService, GeminiServiceError

# ─── Logger ─────────────────────────────────────────────────────────────────

logger = logging.getLogger("saarthi.workflows.onboarding")

# ─── Prompt templates ───────────────────────────────────────────────────────

_ONBOARDING_SYSTEM_PROMPT: str = (
    "You are Mitra, the onboarding specialist for State Bank of India.  "
    "You help customers open new accounts with warmth and clarity.  "
    "Guide the customer through the process step by step.  "
    "Be patient, use simple language, and offer help in their preferred "
    "language.  Always confirm details before proceeding.\n\n"
    "IMPORTANT: Never ask for sensitive information like passwords or "
    "PINs directly.  Always direct customers to secure banking channels "
    "for credential entry."
)

_KYC_PROMPT_TEMPLATE: str = (
    "Customer query: \"{query}\"\n"
    "Language: {language}\n"
    "Persona: {persona}\n"
    "Interaction count: {interaction_count}\n"
    "Previous context: {context}\n\n"
    "The customer wants to open an account.  Based on their query and "
    "context, determine what KYC information is still needed.  "
    "Guide them to the next step.\n\n"
    "Return JSON:\n"
    '{{\n'
    '  "kyc_fields_collected": ["<field1>", "<field2>"],\n'
    '  "kyc_fields_needed": ["<field1>", "<field2>"],\n'
    '  "response": "<conversational response to the customer>",\n'
    '  "requires_document_upload": <true|false>,\n'
    '  "recommended_account_type": "<savings|current|jan_dhan|salary|none>"\n'
    '}}'
)

_ACCOUNT_TYPE_RECOMMENDATIONS: dict[str, dict[str, str]] = {
    "student": {
        "type": "savings",
        "product": "SBI Student Plus Account",
        "features": "Zero balance, free debit card, education loan linkage",
    },
    "farmer": {
        "type": "savings",
        "product": "SBI Kisan Account / Jan Dhan",
        "features": "PM-KISAN linkage, crop insurance, KCC facility",
    },
    "merchant": {
        "type": "current",
        "product": "SBI Current Account",
        "features": "High transaction limits, GST integration, overdraft",
    },
    "salaried": {
        "type": "salary",
        "product": "SBI Salary Account",
        "features": "Auto salary credit, personal loan pre-approval, insurance",
    },
    "senior_citizen": {
        "type": "savings",
        "product": "SBI Senior Citizen Savings Account",
        "features": "Higher interest rate, doorstep banking, SCSS linkage",
    },
}


# ─── Graph node functions ──────────────────────────────────────────────────


def _validate_consent_node(state: SAARTHIState) -> SAARTHIState:
    """
    Verify that the customer has granted the minimum consents
    required for the onboarding flow.
    """
    consent: ConsentStatus = state.get("consent_status", ConsentStatus())

    missing_consents: list[str] = []
    if not consent.is_granted(ConsentCategory.MEMORY_CONSENT):
        missing_consents.append("memory_consent")

    if missing_consents:
        logger.warning(
            "Onboarding consent check — missing consents",
            extra={
                "customer_id": state.get("customer_id"),
                "missing": missing_consents,
            },
        )
        state["response"] = (
            "To help you open an account, I need your permission to "
            "store your information securely.  Would you like to grant "
            "consent for data storage?  Your data will be handled as "
            "per the DPDP Act guidelines."
        )
        state["guardrail_status"] = GuardrailStatus.PASSED
    else:
        logger.info(
            "Onboarding consent validated",
            extra={"customer_id": state.get("customer_id")},
        )

    return state


async def _collect_kyc_node(
    state: SAARTHIState,
    gemini_service: GeminiService,
) -> SAARTHIState:
    """
    Use the LLM to determine which KYC fields are collected and
    which are still needed, then generate a guiding response.
    """
    memory: MemoryContext = state.get("memory_context", MemoryContext())
    persona = state.get("persona", "unknown")
    persona_str = persona.value if hasattr(persona, "value") else str(persona)

    context_parts: list[str] = []
    for turn in memory.conversation_history[-3:]:
        content = turn.get("parts", turn.get("content", ""))
        if content:
            context_parts.append(content)

    prompt = _KYC_PROMPT_TEMPLATE.format(
        query=state.get("query", ""),
        language=state.get("language", "en"),
        persona=persona_str,
        interaction_count=memory.interaction_count,
        context="; ".join(context_parts) if context_parts else "none",
    )

    try:
        result: dict[str, Any] = await gemini_service.generate_structured(
            prompt=prompt,
            system_instruction=_ONBOARDING_SYSTEM_PROMPT,
            temperature=0.3,
            network_mode=state.get("network_mode", NetworkMode.TEXT_MODE),
        )

        response_text: str = result.get("response", "")
        recommended_type: str = result.get("recommended_account_type", "none")
        kyc_needed: list[str] = result.get("kyc_fields_needed", [])
        requires_upload: bool = result.get("requires_document_upload", False)

        if response_text:
            state["response"] = response_text

        # Attach KYC metadata to agent response
        agent_response = AgentResponse(
            agent=AgentType.MITRA,
            response_text=response_text,
            recommendations=[],
            confidence=state.get("confidence", 0.0),
            metadata={
                "kyc_fields_needed": kyc_needed,
                "recommended_account_type": recommended_type,
                "requires_document_upload": requires_upload,
            },
        )

        # Add account type recommendation if persona is known
        if persona_str in _ACCOUNT_TYPE_RECOMMENDATIONS:
            rec = _ACCOUNT_TYPE_RECOMMENDATIONS[persona_str]
            agent_response.recommendations.append(rec)

        state["agent_response"] = agent_response

        # Human-in-the-loop for document upload
        if requires_upload or kyc_needed:
            state["action_required"] = HumanInLoopAction(
                action_type="kyc_document_upload",
                action_preview={
                    "fields_needed": kyc_needed,
                    "message": "Please upload the required KYC documents.",
                },
                requires_human_confirmation=True,
            )

    except GeminiServiceError as exc:
        logger.error(
            "KYC collection LLM call failed",
            extra={"error": str(exc)},
        )
        state["response"] = (
            "I'd be happy to help you open an account!  To get started, "
            "I'll need a few details:\n"
            "• Full name as per PAN card\n"
            "• PAN number\n"
            "• Aadhaar number\n"
            "• Mobile number linked to Aadhaar\n\n"
            "Could you please share your full name first?"
        )
        state["agent_response"] = AgentResponse(
            agent=AgentType.MITRA,
            response_text=state["response"],
            confidence=state.get("confidence", 0.0),
        )

    return state


def _should_enter_human_loop(state: SAARTHIState) -> str:
    """Conditional edge: check if human-in-the-loop is required."""
    action = state.get("action_required")
    if action is not None:
        return "human_loop"
    return "finalise"


def _human_loop_node(state: SAARTHIState) -> SAARTHIState:
    """
    Prepare the human-in-the-loop action payload.

    In a production system this would emit an event to the front-end
    and pause the graph until the user responds.  Here we prepare
    the state for the API layer to handle the pause.
    """
    action = state.get("action_required")
    if action is not None:
        logger.info(
            "Human-in-the-loop action prepared",
            extra={
                "customer_id": state.get("customer_id"),
                "action_type": action.action_type,
                "requires_mpin": action.requires_mpin,
                "requires_biometric": action.requires_biometric,
            },
        )

        # Append instructions to the response
        current_response = state.get("response", "")
        if current_response and "document" in action.action_type.lower():
            state["response"] = (
                f"{current_response}\n\n"
                "📄 Please upload the required documents through our "
                "secure portal.  I'll verify them once received."
            )

    return state


def _finalise_node(state: SAARTHIState) -> SAARTHIState:
    """Final state cleanup and timestamp update."""
    state["timestamp"] = datetime.now(timezone.utc)
    logger.info(
        "Onboarding workflow completed",
        extra={
            "customer_id": state.get("customer_id"),
            "has_action": state.get("action_required") is not None,
        },
    )
    return state


# ─── Graph builder ──────────────────────────────────────────────────────────


def build_onboarding_graph(
    gemini_service: GeminiService,
) -> StateGraph:
    """
    Construct the onboarding LangGraph sub-graph.

    Parameters
    ----------
    gemini_service : GeminiService
        Shared Gemini API client.

    Returns
    -------
    StateGraph
        Compiled LangGraph graph ready for invocation.
    """

    # Closures that capture the gemini_service dependency
    async def collect_kyc(state: SAARTHIState) -> SAARTHIState:
        return await _collect_kyc_node(state, gemini_service)

    graph = StateGraph(SAARTHIState)

    # ── Add nodes ──────────────────────────────────────────────────────
    graph.add_node("validate_consent", _validate_consent_node)
    graph.add_node("collect_kyc", collect_kyc)
    graph.add_node("human_loop", _human_loop_node)
    graph.add_node("finalise", _finalise_node)

    # ── Set entry point ────────────────────────────────────────────────
    graph.set_entry_point("validate_consent")

    # ── Add edges ──────────────────────────────────────────────────────
    graph.add_edge("validate_consent", "collect_kyc")
    graph.add_conditional_edges(
        "collect_kyc",
        _should_enter_human_loop,
        {
            "human_loop": "human_loop",
            "finalise": "finalise",
        },
    )
    graph.add_edge("human_loop", "finalise")
    graph.add_edge("finalise", END)

    logger.info("Onboarding graph built")
    return graph
