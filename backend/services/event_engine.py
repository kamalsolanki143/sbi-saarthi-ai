"""
SAARTHI AI — Event Detection Engine
=====================================

Detects banking events embedded in customer queries, transaction
patterns, and memory context.  Events drive **proactive engagement**:

• ``SALARY_CREDIT``        → SAATHI (savings awareness / FD advice)
• ``SCHOOL_FEE_DETECTED``  → SAATHI (scholarship / financial inclusion)
• ``SUBSIDY_CREDIT``       → SAATHI (savings-linked products)
• ``IDLE_BALANCE_DETECTED``→ SAATHI (FD / RD / savings recommendations)
• ``FESTIVAL_SPENDING``    → SAATHI (offers, cashback, digital payments)

Detection follows a two-tier strategy identical to the other engines:

1. **Keyword heuristics** for high-certainty patterns.
2. **Gemini LLM** fallback for ambiguous or multilingual inputs.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from backend.models.state import (
    AgentType,
    EventResult,
    EventType,
    MemoryContext,
    NetworkMode,
    Priority,
    SAARTHIState,
)
from backend.services.gemini_service import GeminiService, GeminiServiceError

# ─── Logger ─────────────────────────────────────────────────────────────────

logger = logging.getLogger("saarthi.services.event_engine")


# ─── Event → Agent / Priority routing table ────────────────────────────────

_EVENT_ROUTING: dict[EventType, tuple[AgentType, Priority]] = {
    EventType.SALARY_CREDIT:             (AgentType.SAATHI,      Priority.MEDIUM),
    EventType.SUBSIDY_CREDIT:            (AgentType.SAATHI,      Priority.MEDIUM),
    EventType.IDLE_BALANCE_DETECTED:     (AgentType.SAATHI,      Priority.LOW),
    EventType.SCHOOL_FEE_DETECTED:       (AgentType.SAATHI,      Priority.MEDIUM),
    EventType.FESTIVAL_SPENDING_DETECTED:(AgentType.SAATHI,       Priority.LOW),
    EventType.NONE:                      (AgentType.FALLBACK,     Priority.LOW),
}


_EVENT_CONTEXT_BUILDERS: dict[EventType, str] = {
    EventType.SALARY_CREDIT: (
        "Customer has received a salary credit.  Suggest ways to "
        "optimise savings: Fixed Deposits, Recurring Deposits, "
        "savings products."
    ),
    EventType.SUBSIDY_CREDIT: (
        "Government subsidy credited.  Suggest safe savings instruments "
        "and digital banking adoption appropriate for rural/semi-urban "
        "customers."
    ),
    EventType.IDLE_BALANCE_DETECTED: (
        "Customer has idle funds in their account.  Recommend Fixed "
        "Deposits, Recurring Deposits, or sweep-in facility to earn "
        "better returns."
    ),
    EventType.FESTIVAL_SPENDING_DETECTED: (
        "Festival season spending detected.  Suggest digital payment "
        "options, cashback offers, and savings tips."
    ),
}


# ─── Keyword rules ──────────────────────────────────────────────────────────

_EVENT_KEYWORDS: list[tuple[list[str], EventType, dict[str, Any]]] = [
    (
        ["salary credit", "salary received", "vetan", "pay credited", "salary aa gaya"],
        EventType.SALARY_CREDIT,
        {"source": "keyword_match"},
    ),
    (
        ["school fee", "tuition fee", "college fee", "vidyalaya shulk", "exam fee"],
        EventType.SCHOOL_FEE_DETECTED,
        {"source": "keyword_match"},
    ),
    (
        ["subsidy", "pm kisan", "dbt", "government credit", "sarkari paisa"],
        EventType.SUBSIDY_CREDIT,
        {"source": "keyword_match"},
    ),
    (
        ["idle balance", "unused balance", "paisa pada hua", "balance not used"],
        EventType.IDLE_BALANCE_DETECTED,
        {"source": "keyword_match"},
    ),
    (
        ["festival", "diwali", "holi", "eid", "navratri", "christmas", "tyohaar"],
        EventType.FESTIVAL_SPENDING_DETECTED,
        {"source": "keyword_match"},
    ),
]

# ─── LLM prompt ─────────────────────────────────────────────────────────────

_EVENT_SYSTEM_PROMPT: str = (
    "You are a banking-event detection engine for State Bank of India.  "
    "Analyse the customer query and any provided context to determine if "
    "a specific banking event is occurring or being referenced.\n\n"
    "Valid events:\n"
    "  salary_credit, subsidy_credit, idle_balance_detected,\n"
    "  school_fee_detected, festival_spending_detected, none\n\n"
    "Respond ONLY with a JSON object — no markdown, no commentary."
)

_EVENT_USER_TEMPLATE: str = (
    "Customer query: \"{query}\"\n"
    "Language: {language}\n"
    "Recent context: {context}\n\n"
    "Return JSON:\n"
    '{{\n'
    '  "event_type": "<one of the valid events>",\n'
    '  "priority": "<low|medium|high|critical>",\n'
    '  "metadata": {{"reason": "<brief explanation>"}}\n'
    '}}'
)


# ─── Engine ─────────────────────────────────────────────────────────────────


class EventEngine:
    """
    Detects banking events from customer interactions.

    Parameters
    ----------
    gemini_service : GeminiService
        Shared Gemini API client.
    """

    def __init__(self, gemini_service: GeminiService) -> None:
        self._gemini: GeminiService = gemini_service
        logger.info("EventEngine initialised")

    # ── Public API ──────────────────────────────────────────────────────

    async def detect(self, state: SAARTHIState) -> EventResult:
        """
        Detect banking events from the current pipeline state.

        Strategy
        --------
        1. Keyword scan over query + memory context.
        2. If no keyword match → Gemini LLM classification.
        3. Map detected event to agent + priority via the routing table.

        Parameters
        ----------
        state : SAARTHIState
            Current pipeline state.

        Returns
        -------
        EventResult
            Detected event type, recommended agent, priority, and metadata.
        """
        start = time.monotonic()
        query: str = state.get("query", "")
        memory: MemoryContext = state.get("memory_context", MemoryContext())
        network_mode: NetworkMode = state.get("network_mode", NetworkMode.TEXT_MODE)

        if not query.strip():
            return EventResult()

        # ── Phase 1: keyword scan ──────────────────────────────────────
        keyword_result = self._keyword_detect(query, memory)
        if keyword_result.event_type != EventType.NONE:
            elapsed = (time.monotonic() - start) * 1000
            logger.info(
                "Event detected via keywords",
                extra={
                    "event": keyword_result.event_type.value,
                    "agent": keyword_result.recommended_agent.value,
                    "priority": keyword_result.priority.value,
                    "elapsed_ms": round(elapsed, 2),
                },
            )
            return keyword_result

        # ── Phase 2: LLM detection ────────────────────────────────────
        try:
            llm_result = await self._llm_detect(
                query=query,
                language=state.get("language", "en"),
                memory=memory,
                network_mode=network_mode,
            )
        except GeminiServiceError as exc:
            elapsed = (time.monotonic() - start) * 1000
            logger.error(
                "LLM event detection failed — returning NONE",
                extra={"error": str(exc), "elapsed_ms": round(elapsed, 2)},
            )
            return EventResult()

        elapsed = (time.monotonic() - start) * 1000
        logger.info(
            "Event detection complete",
            extra={
                "event": llm_result.event_type.value,
                "agent": llm_result.recommended_agent.value,
                "priority": llm_result.priority.value,
                "elapsed_ms": round(elapsed, 2),
            },
        )
        return llm_result

    # ── Keyword layer ───────────────────────────────────────────────────

    @staticmethod
    def _keyword_detect(
        query: str,
        memory: MemoryContext,
    ) -> EventResult:
        """
        Deterministic keyword scan for event detection.

        Checks the query and the last few conversation turns.
        """
        corpus = query.lower()

        # Add recent conversation context
        for turn in memory.conversation_history[-3:]:
            content = turn.get("parts", turn.get("content", ""))
            if content:
                corpus += " " + content.lower()

        for keywords, event_type, extra_meta in _EVENT_KEYWORDS:
            for kw in keywords:
                if kw in corpus:
                    agent, priority = _EVENT_ROUTING.get(
                        event_type, (AgentType.FALLBACK, Priority.LOW)
                    )
                    return EventResult(
                        event_type=event_type,
                        recommended_agent=agent,
                        priority=priority,
                        metadata={**extra_meta, "matched_keyword": kw},
                    )

        return EventResult()

    # ── LLM layer ───────────────────────────────────────────────────────

    async def _llm_detect(
        self,
        query: str,
        language: str,
        memory: MemoryContext,
        network_mode: NetworkMode,
    ) -> EventResult:
        """Invoke Gemini for event classification."""
        context_parts: list[str] = []
        for turn in memory.conversation_history[-3:]:
            content = turn.get("parts", turn.get("content", ""))
            if content:
                context_parts.append(content)

        context_str = "; ".join(context_parts) if context_parts else "none"

        user_prompt = _EVENT_USER_TEMPLATE.format(
            query=query,
            language=language,
            context=context_str[:500],
        )

        raw: dict[str, Any] = await self._gemini.generate_structured(
            prompt=user_prompt,
            system_instruction=_EVENT_SYSTEM_PROMPT,
            temperature=0.1,
            network_mode=network_mode,
        )

        return self._map_llm_response(raw)

    @staticmethod
    def _map_llm_response(raw: dict[str, Any]) -> EventResult:
        """Convert LLM JSON to an ``EventResult``."""
        event_str: str = raw.get("event_type", "none")
        priority_str: str = raw.get("priority", "low")
        metadata: dict[str, Any] = raw.get("metadata", {})

        # Resolve event enum
        try:
            event_type = EventType(event_str)
        except ValueError:
            logger.warning(
                "LLM returned unknown event type",
                extra={"raw_event": event_str},
            )
            event_type = EventType.NONE

        # Resolve priority enum
        try:
            priority = Priority(priority_str)
        except ValueError:
            priority = Priority.LOW

        # Look up routing
        agent, default_priority = _EVENT_ROUTING.get(
            event_type, (AgentType.FALLBACK, Priority.LOW)
        )

        # Use LLM priority if it's higher than default
        final_priority = (
            priority
            if _priority_rank(priority) >= _priority_rank(default_priority)
            else default_priority
        )

        metadata["source"] = "llm_classification"

        return EventResult(
            event_type=event_type,
            recommended_agent=agent,
            priority=final_priority,
            metadata=metadata,
        )


# ─── Module helpers ─────────────────────────────────────────────────────────

_PRIORITY_ORDER: dict[Priority, int] = {
    Priority.LOW: 0,
    Priority.MEDIUM: 1,
    Priority.HIGH: 2,
    Priority.CRITICAL: 3,
}


def _priority_rank(p: Priority) -> int:
    """Return a numeric rank for priority comparison."""
    return _PRIORITY_ORDER.get(p, 0)
