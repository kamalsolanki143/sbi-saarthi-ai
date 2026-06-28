"""
SAARTHI AI — Confidence Engine
Computes intent confidence scores and enforces the 85% threshold rule.

Used by: confidence_checker.py (guardrail), all three agents,
         orchestrator.py (routing decisions)

The 85% rule:
  confidence >= 0.85 → proceed with recommendation flow
  confidence < 0.85 → trigger fallback_graph.py (clarifying question)
  confidence < 0.50 → do not log a recommendation attempt at all
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from backend.utils.constants import CONFIDENCE_THRESHOLD, MIN_CONFIDENCE_TO_LOG
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ConfidenceResult:
    """
    Result of intent confidence evaluation.

    Attributes:
        detected_intent: The intent string detected (e.g. 'fd_enquiry')
        confidence: Score 0.0–1.0
        should_proceed: True if confidence >= CONFIDENCE_THRESHOLD (0.85)
        should_log: True if confidence >= MIN_CONFIDENCE_TO_LOG (0.50)
        clarifying_question: Non-None if should_proceed=False
        quick_reply_options: Suggested quick-reply buttons for clarifying question
    """
    detected_intent: str
    confidence: float
    should_proceed: bool
    should_log: bool
    clarifying_question: Optional[str] = None
    quick_reply_options: list[str] = None

    def __post_init__(self):
        if self.quick_reply_options is None:
            self.quick_reply_options = []


class ConfidenceEngine:
    """
    Evaluates confidence of a detected intent.
    Integrates with GeminiService for LLM-based scoring,
    with rule-based overrides for high-certainty event types.
    """

    # Rule-based confidence for system-generated events
    # (these come from CBS/banking system, not from customer speech — always high confidence)
    SYSTEM_EVENT_CONFIDENCE: dict[str, float] = {
        "salary_credit": 0.97,
        "subsidy_credit": 0.96,
        "idle_balance": 0.90,
        "upi_not_activated": 0.93,
        "yono_not_adopted": 0.91,
        "fd_eligible": 0.92,
        "account_opened": 0.95,
        "kyc_incomplete": 0.94,
    }

    async def evaluate_event(
        self, event_type: str, source: str = "webhook"
    ) -> ConfidenceResult:
        """
        Evaluate confidence for a system/webhook event.
        System events always have high confidence — no LLM call needed.
        """
        confidence = self.SYSTEM_EVENT_CONFIDENCE.get(event_type, 0.80)

        logger.info(
            "confidence_evaluated_event",
            event_type=event_type,
            source=source,
            confidence=confidence,
        )

        return ConfidenceResult(
            detected_intent=event_type,
            confidence=confidence,
            should_proceed=confidence >= CONFIDENCE_THRESHOLD,
            should_log=confidence >= MIN_CONFIDENCE_TO_LOG,
            clarifying_question=None,
        )

    async def evaluate_text_input(
        self,
        customer_input: str,
        customer_id: str,
        context: str = "",
    ) -> ConfidenceResult:
        """
        Evaluate confidence for a free-text customer input.
        Calls GeminiService for LLM-based intent detection.
        """
        from backend.services.gemini_service import gemini_service

        logger.info(
            "confidence_evaluating_text",
            customer_id=customer_id,
            input_preview=customer_input[:50],
        )

        try:
            result = await gemini_service.detect_intent_confidence(
                customer_input=customer_input, context=context
            )
        except Exception as e:
            logger.error("confidence_llm_error", error=str(e), customer_id=customer_id)
            # Safe fallback: low confidence → clarifying question
            return ConfidenceResult(
                detected_intent="unknown",
                confidence=0.40,
                should_proceed=False,
                should_log=False,
                clarifying_question="Maaf kijiye, kya aap thoda aur bata sakte hain aap kya karna chahte hain?",
                quick_reply_options=["Balance check", "FD khulwana hai", "UPI activate karna hai", "Help chahiye"],
            )

        confidence = float(result.get("confidence", 0.0))
        detected_intent = result.get("detected_intent", "unknown")
        clarifying_question = result.get("clarifying_question")
        quick_reply_options = result.get("quick_reply_options", [])

        should_proceed = confidence >= CONFIDENCE_THRESHOLD
        should_log = confidence >= MIN_CONFIDENCE_TO_LOG

        if not should_proceed and not clarifying_question:
            # Generate a generic fallback question
            clarifying_question = self._generic_clarifying_question(detected_intent)

        logger.info(
            "confidence_evaluated_text",
            customer_id=customer_id,
            intent=detected_intent,
            confidence=confidence,
            should_proceed=should_proceed,
        )

        return ConfidenceResult(
            detected_intent=detected_intent,
            confidence=confidence,
            should_proceed=should_proceed,
            should_log=should_log,
            clarifying_question=clarifying_question if not should_proceed else None,
            quick_reply_options=quick_reply_options if not should_proceed else [],
        )

    def _generic_clarifying_question(self, detected_intent: str) -> str:
        """Generate a contextual clarifying question based on partial intent detection."""
        question_map = {
            "fd": "Kya aap Fixed Deposit banana chahte hain ya FD ke baare mein janna chahte hain?",
            "upi": "Kya aap UPI activate karna chahte hain ya UPI se payment karna chahte hain?",
            "balance": "Kya aap apna balance check karna chahte hain ya kuch aur?",
            "yono": "Kya aap YONO app ke baare mein jaanna chahte hain?",
        }
        for key, question in question_map.items():
            if key in detected_intent.lower():
                return question
        return (
            "Maaf kijiye, main samajh nahi paaya. Kya aap thoda aur clearly bata sakte hain?"
        )


# ── Singleton ───────────────────────────────────────────────────────────────
confidence_engine = ConfidenceEngine()
