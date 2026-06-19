"""
SAARTHI AI — Confidence Engine
===============================

Classifies customer intent from natural-language queries and produces a
confidence score (0–100).  The score drives the routing decision:

• confidence ≥ 85  →  route to the recommended specialist agent
• confidence < 85  →  route to the fallback workflow

The engine delegates to ``GeminiService.generate_structured`` and maps
the JSON output onto the ``ConfidenceResult`` Pydantic model defined in
the canonical state module.

Design notes
────────────
• A deterministic rule layer runs **before** the LLM to catch obvious
  keyword patterns (fast-path), saving API calls and latency.
• The LLM prompt is carefully structured to return a constrained JSON
  schema so parsing is reliable even on edge-case inputs.
• All results are logged with structured fields for downstream analytics.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from backend.models.state import (
    AgentType,
    ConfidenceResult,
    IntentCategory,
    NetworkMode,
    SAARTHIState,
)
from backend.services.gemini_service import GeminiService, GeminiServiceError

# ─── Logger ─────────────────────────────────────────────────────────────────

logger = logging.getLogger("saarthi.services.confidence_engine")


# ─── Intent → Agent mapping ────────────────────────────────────────────────

_INTENT_AGENT_MAP: dict[IntentCategory, AgentType] = {
    # MITRA — Customer Acquisition
    IntentCategory.ACCOUNT_OPENING: AgentType.MITRA,
    IntentCategory.BALANCE_INQUIRY: AgentType.MITRA,
    IntentCategory.FUND_TRANSFER: AgentType.MITRA,
    IntentCategory.CARD_SERVICES: AgentType.MITRA,
    # MARGDARSHAN — Digital Adoption
    IntentCategory.DIGITAL_ADOPTION: AgentType.MARGDARSHAN,
    IntentCategory.BILL_PAYMENT: AgentType.MARGDARSHAN,
    IntentCategory.FD_RECOMMENDATION: AgentType.MARGDARSHAN,
    IntentCategory.ACCOUNT_SERVICES: AgentType.MARGDARSHAN,
    IntentCategory.PRODUCT_RECOMMENDATION: AgentType.MARGDARSHAN,
    # SAATHI — Customer Engagement
    IntentCategory.SAVINGS_AWARENESS: AgentType.SAATHI,
    IntentCategory.CUSTOMER_ENGAGEMENT: AgentType.SAATHI,
    IntentCategory.COMPLAINT: AgentType.SAATHI,
    IntentCategory.GENERAL_INQUIRY: AgentType.SAATHI,
    # Fallback
    IntentCategory.UNKNOWN: AgentType.FALLBACK,
}

_CONFIDENCE_THRESHOLD: float = 85.0

# ─── Keyword fast-path rules ───────────────────────────────────────────────

_KEYWORD_RULES: list[tuple[list[str], IntentCategory, float]] = [
    (
        ["open account", "new account", "account opening", "khata kholna"],
        IntentCategory.ACCOUNT_OPENING,
        92.0,
    ),
    (
        ["balance", "check balance", "balance inquiry", "kitna paisa"],
        IntentCategory.BALANCE_INQUIRY,
        90.0,
    ),
    (
        ["transfer", "send money", "bhej do", "fund transfer", "neft", "imps"],
        IntentCategory.FUND_TRANSFER,
        90.0,
    ),
    (
        ["fd", "fixed deposit", "fd recommendation", "fd kholna"],
        IntentCategory.FD_RECOMMENDATION,
        88.0,
    ),
    (
        ["bill pay", "electricity bill", "recharge", "bill payment"],
        IntentCategory.BILL_PAYMENT,
        90.0,
    ),
    (
        ["credit card", "debit card", "card block", "new card", "atm card"],
        IntentCategory.CARD_SERVICES,
        89.0,
    ),
    (
        ["upi", "upi activate", "upi setup", "upi pin"],
        IntentCategory.DIGITAL_ADOPTION,
        90.0,
    ),
    (
        ["yono", "app", "internet banking", "online banking", "digital"],
        IntentCategory.DIGITAL_ADOPTION,
        87.0,
    ),
    (
        ["account service", "passbook", "cheque book", "statement", "nomination"],
        IntentCategory.ACCOUNT_SERVICES,
        88.0,
    ),
    (
        ["saving", "bachat", "savings account", "savings awareness"],
        IntentCategory.SAVINGS_AWARENESS,
        87.0,
    ),
    (
        ["complaint", "issue", "problem", "not working", "shikayat"],
        IntentCategory.COMPLAINT,
        87.0,
    ),
]


# ─── Classification prompt ─────────────────────────────────────────────────

_CLASSIFICATION_SYSTEM_PROMPT: str = (
    "You are an expert intent classifier for State Bank of India's AI "
    "banking assistant.  Analyse the customer query and classify it into "
    "exactly ONE intent category.\n\n"
    "Valid intent categories:\n"
    "  account_opening, balance_inquiry, fund_transfer, bill_payment,\n"
    "  card_services, fd_recommendation, digital_adoption, account_services,\n"
    "  savings_awareness, customer_engagement, complaint,\n"
    "  product_recommendation, general_inquiry, unknown\n\n"
    "Respond ONLY with a JSON object — no markdown, no commentary."
)

_CLASSIFICATION_USER_TEMPLATE: str = (
    "Customer query: \"{query}\"\n"
    "Customer language: {language}\n"
    "Previous interactions count: {interaction_count}\n\n"
    "Return JSON:\n"
    '{{\n'
    '  "intent": "<one of the valid categories>",\n'
    '  "confidence": <number 0-100>,\n'
    '  "reasoning": "<one sentence explaining the classification>"\n'
    '}}'
)


# ─── Engine ─────────────────────────────────────────────────────────────────


class ConfidenceEngine:
    """
    Classifies customer intent and produces a confidence-scored routing
    recommendation.

    Parameters
    ----------
    gemini_service : GeminiService
        Shared Gemini API client.
    confidence_threshold : float
        Minimum confidence to route to a specialist agent (default 85).
    """

    def __init__(
        self,
        gemini_service: GeminiService,
        confidence_threshold: float = _CONFIDENCE_THRESHOLD,
    ) -> None:
        self._gemini: GeminiService = gemini_service
        self._threshold: float = confidence_threshold
        logger.info(
            "ConfidenceEngine initialised",
            extra={"threshold": confidence_threshold},
        )

    # ── Public API ──────────────────────────────────────────────────────

    async def classify(
        self,
        state: SAARTHIState,
    ) -> ConfidenceResult:
        """
        Classify the customer query and return a ``ConfidenceResult``.

        The method first tries a fast keyword-matching pass.  If no
        keyword rule triggers, it falls through to the Gemini LLM.

        Parameters
        ----------
        state : SAARTHIState
            Current pipeline state.  Reads ``query``, ``language``, and
            ``memory_context.interaction_count``.

        Returns
        -------
        ConfidenceResult
            Populated intent, confidence, recommended_agent, and reasoning.
        """
        start = time.monotonic()
        query: str = state.get("query", "")
        language: str = state.get("language", "en")
        network_mode: NetworkMode = state.get("network_mode", NetworkMode.TEXT_MODE)

        if not query.strip():
            logger.warning("Empty query received — returning UNKNOWN intent")
            return ConfidenceResult(
                intent=IntentCategory.UNKNOWN,
                confidence=0.0,
                recommended_agent=AgentType.FALLBACK,
                reasoning="Empty query provided.",
            )

        # Fast-path: keyword rules
        keyword_result = self._keyword_match(query)
        if keyword_result is not None:
            elapsed = (time.monotonic() - start) * 1000
            logger.info(
                "Intent classified via keyword fast-path",
                extra={
                    "intent": keyword_result.intent.value,
                    "confidence": keyword_result.confidence,
                    "agent": keyword_result.recommended_agent.value,
                    "elapsed_ms": round(elapsed, 2),
                },
            )
            return keyword_result

        # Slow-path: LLM classification
        try:
            result = await self._llm_classify(
                query=query,
                language=language,
                interaction_count=self._get_interaction_count(state),
                network_mode=network_mode,
            )
        except GeminiServiceError as exc:
            elapsed = (time.monotonic() - start) * 1000
            logger.error(
                "LLM classification failed — falling back to UNKNOWN",
                extra={"error": str(exc), "elapsed_ms": round(elapsed, 2)},
            )
            result = ConfidenceResult(
                intent=IntentCategory.UNKNOWN,
                confidence=0.0,
                recommended_agent=AgentType.FALLBACK,
                reasoning=f"Classification failed: {exc}",
            )

        elapsed = (time.monotonic() - start) * 1000
        logger.info(
            "Intent classified via LLM",
            extra={
                "intent": result.intent.value,
                "confidence": result.confidence,
                "agent": result.recommended_agent.value,
                "elapsed_ms": round(elapsed, 2),
            },
        )
        return result

    # ── Keyword fast-path ───────────────────────────────────────────────

    @staticmethod
    def _keyword_match(query: str) -> ConfidenceResult | None:
        """
        Attempt deterministic intent classification via keyword rules.

        Returns ``None`` when no rule fires.
        """
        normalised: str = query.lower().strip()

        for keywords, intent, confidence in _KEYWORD_RULES:
            for kw in keywords:
                if kw in normalised:
                    agent = _INTENT_AGENT_MAP.get(intent, AgentType.FALLBACK)
                    if confidence < _CONFIDENCE_THRESHOLD:
                        agent = AgentType.FALLBACK

                    return ConfidenceResult(
                        intent=intent,
                        confidence=confidence,
                        recommended_agent=agent,
                        reasoning=f"Keyword match on '{kw}'.",
                    )

        return None

    # ── LLM classification ──────────────────────────────────────────────

    async def _llm_classify(
        self,
        query: str,
        language: str,
        interaction_count: int,
        network_mode: NetworkMode,
    ) -> ConfidenceResult:
        """Call Gemini for intent classification and map the response."""
        user_prompt: str = _CLASSIFICATION_USER_TEMPLATE.format(
            query=query,
            language=language,
            interaction_count=interaction_count,
        )

        raw: dict[str, Any] = await self._gemini.generate_structured(
            prompt=user_prompt,
            system_instruction=_CLASSIFICATION_SYSTEM_PROMPT,
            temperature=0.1,
            network_mode=network_mode,
        )

        return self._map_llm_response(raw)

    def _map_llm_response(self, raw: dict[str, Any]) -> ConfidenceResult:
        """Convert the LLM JSON output to a validated ``ConfidenceResult``."""
        intent_str: str = raw.get("intent", "unknown")
        confidence_val: float = float(raw.get("confidence", 0.0))
        reasoning_str: str = raw.get("reasoning", "")

        # Resolve intent enum (safe fallback)
        try:
            intent = IntentCategory(intent_str)
        except ValueError:
            logger.warning(
                "LLM returned unknown intent value — mapping to UNKNOWN",
                extra={"raw_intent": intent_str},
            )
            intent = IntentCategory.UNKNOWN
            confidence_val = min(confidence_val, 50.0)

        # Clamp confidence
        confidence_val = max(0.0, min(100.0, confidence_val))

        # Determine agent
        if confidence_val >= self._threshold:
            agent = _INTENT_AGENT_MAP.get(intent, AgentType.FALLBACK)
        else:
            agent = AgentType.FALLBACK

        return ConfidenceResult(
            intent=intent,
            confidence=confidence_val,
            recommended_agent=agent,
            reasoning=reasoning_str,
        )

    # ── Helpers ─────────────────────────────────────────────────────────

    @staticmethod
    def _get_interaction_count(state: SAARTHIState) -> int:
        """Safely extract interaction count from memory context."""
        memory = state.get("memory_context")
        if memory is not None and hasattr(memory, "interaction_count"):
            return memory.interaction_count
        return 0
