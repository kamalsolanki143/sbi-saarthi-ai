"""
SAARTHI AI — Persona Engine
=============================

Detects the customer persona archetype from available signals:

• Transaction patterns (school fees → student, mandi payments → farmer, …)
• Account metadata (age, occupation, salary credit patterns)
• Conversation history and language cues
• Explicit profile data from the memory layer

The detected persona drives personalisation of language, tone, product
recommendations, and agent behavior across Mitra, Margdarshan, and
Saathi.

Architecture
────────────
1. **Heuristic layer** — fast, deterministic rules over structured data.
2. **LLM layer** — fallback Gemini classification when heuristics are
   inconclusive (confidence < 70).
3. Both layers produce a ``PersonaResult`` from the canonical state module.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from backend.models.state import (
    MemoryContext,
    NetworkMode,
    PersonaResult,
    PersonaType,
    SAARTHIState,
)
from backend.services.gemini_service import GeminiService, GeminiServiceError

# ─── Logger ─────────────────────────────────────────────────────────────────

logger = logging.getLogger("saarthi.services.persona_engine")


# ─── Signal keyword sets ───────────────────────────────────────────────────

_PERSONA_SIGNALS: dict[PersonaType, list[str]] = {
    PersonaType.STUDENT: [
        "school fee", "college fee", "tuition", "hostel",
        "scholarship", "student",
        "exam fee", "university", "vidyalaya",
    ],
    PersonaType.FARMER: [
        "kisan", "crop", "mandi", "fertilizer", "agriculture",
        "kcc", "kisan credit", "pm kisan",
        "subsidy", "tractor", "harvest",
    ],
    PersonaType.MERCHANT: [
        "gst", "business", "invoice", "vendor", "supplier",
        "trade", "wholesale", "retail", "shop", "dukaan",
        "udyam", "msme", "current account",
    ],
    PersonaType.SALARIED: [
        "salary", "pay slip", "pf", "provident fund",
        "gratuity", "hra", "tax saving", "form 16",
        "employer", "corporate", "naukri",
    ],
    PersonaType.SENIOR_CITIZEN: [
        "pension", "senior citizen", "retirement", "vrishti",
        "scss", "senior citizen saving", "old age",
        "medical",
    ],
}

_HEURISTIC_CONFIDENCE_FLOOR: float = 70.0


# ─── LLM Prompt ─────────────────────────────────────────────────────────────

_PERSONA_SYSTEM_PROMPT: str = (
    "You are a customer profiling engine for State Bank of India.  "
    "Based on the provided signals, classify the customer into exactly "
    "ONE persona archetype.\n\n"
    "Valid archetypes: student, farmer, merchant, salaried, "
    "senior_citizen, unknown\n\n"
    "Respond ONLY with a JSON object — no markdown, no commentary."
)

_PERSONA_USER_TEMPLATE: str = (
    "Customer query: \"{query}\"\n"
    "Language: {language}\n"
    "Profile data: {profile_data}\n"
    "Product interests: {product_interests}\n"
    "Interaction count: {interaction_count}\n\n"
    "Return JSON:\n"
    '{{\n'
    '  "persona": "<one of the valid archetypes>",\n'
    '  "confidence": <number 0-100>,\n'
    '  "signals": ["<signal 1>", "<signal 2>"]\n'
    '}}'
)


# ─── Engine ─────────────────────────────────────────────────────────────────


class PersonaEngine:
    """
    Detects the customer persona archetype from multi-modal signals.

    Parameters
    ----------
    gemini_service : GeminiService
        Shared Gemini API client for LLM-backed classification.
    """

    def __init__(self, gemini_service: GeminiService) -> None:
        self._gemini: GeminiService = gemini_service
        logger.info("PersonaEngine initialised")

    # ── Public API ──────────────────────────────────────────────────────

    async def detect(self, state: SAARTHIState) -> PersonaResult:
        """
        Detect the customer persona from current state signals.

        Strategy
        --------
        1. Run heuristic keyword scan over query + memory context.
        2. If heuristic confidence ≥ 70 → return immediately.
        3. Otherwise fall back to Gemini LLM for richer classification.

        Parameters
        ----------
        state : SAARTHIState
            Current pipeline state.

        Returns
        -------
        PersonaResult
            Detected persona, confidence, and contributing signals.
        """
        start = time.monotonic()

        query: str = state.get("query", "")
        memory: MemoryContext = state.get("memory_context", MemoryContext())

        # ── Phase 1: heuristic scan ────────────────────────────────────
        heuristic_result = self._heuristic_detect(query, memory)

        if heuristic_result.confidence >= _HEURISTIC_CONFIDENCE_FLOOR:
            elapsed = (time.monotonic() - start) * 1000
            logger.info(
                "Persona detected via heuristics",
                extra={
                    "persona": heuristic_result.persona.value,
                    "confidence": heuristic_result.confidence,
                    "signals": heuristic_result.signals,
                    "elapsed_ms": round(elapsed, 2),
                },
            )
            return heuristic_result

        # ── Phase 2: LLM classification ────────────────────────────────
        try:
            llm_result = await self._llm_detect(
                query=query,
                language=state.get("language", "en"),
                memory=memory,
                network_mode=state.get("network_mode", NetworkMode.TEXT_MODE),
            )
        except GeminiServiceError as exc:
            elapsed = (time.monotonic() - start) * 1000
            logger.error(
                "LLM persona detection failed — returning heuristic result",
                extra={"error": str(exc), "elapsed_ms": round(elapsed, 2)},
            )
            # Return whatever the heuristic found, even if low-confidence
            return heuristic_result if heuristic_result.confidence > 0 else PersonaResult()

        # ── Merge: prefer LLM if higher confidence ────────────────────
        final = self._merge_results(heuristic_result, llm_result)
        elapsed = (time.monotonic() - start) * 1000
        logger.info(
            "Persona detected (merged)",
            extra={
                "persona": final.persona.value,
                "confidence": final.confidence,
                "signals": final.signals,
                "elapsed_ms": round(elapsed, 2),
            },
        )
        return final

    # ── Heuristic layer ─────────────────────────────────────────────────

    @staticmethod
    def _heuristic_detect(
        query: str,
        memory: MemoryContext,
    ) -> PersonaResult:
        """
        Score each persona archetype by counting keyword hits across
        the query, product interests, and behavioral context.
        """
        corpus: str = _build_signal_corpus(query, memory)
        normalised: str = corpus.lower()

        best_persona: PersonaType = PersonaType.UNKNOWN
        best_score: int = 0
        matched_signals: list[str] = []

        for persona, keywords in _PERSONA_SIGNALS.items():
            hits: list[str] = [kw for kw in keywords if kw in normalised]
            score = len(hits)
            if score > best_score:
                best_score = score
                best_persona = persona
                matched_signals = hits

        # Map hit count → confidence (diminishing returns)
        if best_score == 0:
            confidence = 0.0
        elif best_score == 1:
            confidence = 55.0
        elif best_score == 2:
            confidence = 72.0
        elif best_score == 3:
            confidence = 82.0
        else:
            confidence = min(95.0, 82.0 + (best_score - 3) * 3.0)

        # Boost from explicit profile data
        profile = memory.customer_profile
        if profile.get("occupation", "").lower() in (
            best_persona.value,
            best_persona.value.replace("_", " "),
        ):
            confidence = min(100.0, confidence + 10.0)
            matched_signals.append("profile_occupation_match")

        if profile.get("age_group") == "senior" and best_persona == PersonaType.SENIOR_CITIZEN:
            confidence = min(100.0, confidence + 8.0)
            matched_signals.append("age_group_senior")

        return PersonaResult(
            persona=best_persona,
            confidence=confidence,
            signals=matched_signals,
        )

    # ── LLM layer ───────────────────────────────────────────────────────

    async def _llm_detect(
        self,
        query: str,
        language: str,
        memory: MemoryContext,
        network_mode: NetworkMode,
    ) -> PersonaResult:
        """Invoke Gemini for persona classification."""
        user_prompt: str = _PERSONA_USER_TEMPLATE.format(
            query=query,
            language=language,
            profile_data=_safe_json(memory.customer_profile),
            product_interests=", ".join(memory.product_interests) or "none",
            interaction_count=memory.interaction_count,
        )

        raw: dict[str, Any] = await self._gemini.generate_structured(
            prompt=user_prompt,
            system_instruction=_PERSONA_SYSTEM_PROMPT,
            temperature=0.1,
            network_mode=network_mode,
        )

        return _map_llm_response(raw)

    # ── Merge logic ─────────────────────────────────────────────────────

    @staticmethod
    def _merge_results(
        heuristic: PersonaResult,
        llm: PersonaResult,
    ) -> PersonaResult:
        """
        Combine heuristic and LLM results.

        When both agree on the same persona the confidences are averaged
        with a bonus.  Otherwise the higher-confidence result wins.
        """
        if heuristic.persona == llm.persona and heuristic.persona != PersonaType.UNKNOWN:
            merged_confidence = min(
                100.0,
                (heuristic.confidence + llm.confidence) / 2 + 10.0,
            )
            merged_signals = list(
                dict.fromkeys(heuristic.signals + llm.signals),
            )
            return PersonaResult(
                persona=heuristic.persona,
                confidence=merged_confidence,
                signals=merged_signals,
            )

        if llm.confidence >= heuristic.confidence:
            return llm
        return heuristic


# ─── Module-level helpers ───────────────────────────────────────────────────


def _build_signal_corpus(query: str, memory: MemoryContext) -> str:
    """Concatenate all textual signals into a single searchable string."""
    parts: list[str] = [query]
    parts.extend(memory.product_interests)

    for turn in memory.conversation_history[-5:]:
        content = turn.get("parts", turn.get("content", ""))
        if content:
            parts.append(content)

    behavioral = memory.behavioral_context
    if isinstance(behavioral, dict):
        for value in behavioral.values():
            if isinstance(value, str):
                parts.append(value)

    return " ".join(parts)


def _map_llm_response(raw: dict[str, Any]) -> PersonaResult:
    """Convert raw LLM JSON to a ``PersonaResult``."""
    persona_str: str = raw.get("persona", "unknown")
    confidence_val: float = float(raw.get("confidence", 0.0))
    signals_raw: list[Any] = raw.get("signals", [])

    try:
        persona = PersonaType(persona_str)
    except ValueError:
        logger.warning(
            "LLM returned unknown persona — mapping to UNKNOWN",
            extra={"raw_persona": persona_str},
        )
        persona = PersonaType.UNKNOWN
        confidence_val = min(confidence_val, 40.0)

    confidence_val = max(0.0, min(100.0, confidence_val))

    return PersonaResult(
        persona=persona,
        confidence=confidence_val,
        signals=[str(s) for s in signals_raw],
    )


def _safe_json(data: dict[str, Any]) -> str:
    """Stringify a dict for prompt injection, truncated for safety."""
    import json

    try:
        serialised = json.dumps(data, default=str, ensure_ascii=False)
        if len(serialised) > 500:
            return serialised[:500] + "…"
        return serialised
    except (TypeError, ValueError):
        return "{}"
