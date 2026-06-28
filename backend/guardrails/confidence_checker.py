"""
SAARTHI AI — Confidence Checker (Guardrail)
Hard enforcement of the 85% confidence threshold.

RULE: If confidence < 0.85, the agent flow MUST NOT proceed to a recommendation.
      Instead, a LowConfidenceError is raised which triggers fallback_graph.py.

This is a safety-critical guardrail — do NOT soften the threshold or add bypass logic.

Used by: all agents (after confidence_engine.evaluate_*), orchestrator.py
"""
from __future__ import annotations

from backend.services.confidence_engine import ConfidenceResult
from backend.utils.constants import CONFIDENCE_THRESHOLD
from backend.utils.error_handlers import LowConfidenceError
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)


def check_confidence(result: ConfidenceResult, customer_id: str, context: str = "") -> None:
    """
    Enforce the 85% confidence threshold.

    Raises:
        LowConfidenceError: If confidence < CONFIDENCE_THRESHOLD.
                            Caller MUST handle this by triggering the fallback flow.

    If confidence >= threshold: returns normally (no-op).
    """
    if result.confidence >= CONFIDENCE_THRESHOLD:
        logger.info(
            "confidence_check_passed",
            customer_id=customer_id,
            confidence=result.confidence,
            intent=result.detected_intent,
            context=context,
        )
        return

    # ⛔ HARD STOP — below threshold
    logger.warning(
        "confidence_check_failed",
        customer_id=customer_id,
        confidence=result.confidence,
        threshold=CONFIDENCE_THRESHOLD,
        intent=result.detected_intent,
        clarifying_question=result.clarifying_question,
        context=context,
    )
    raise LowConfidenceError(
        message=(
            f"Intent confidence {result.confidence:.2%} is below the required "
            f"{CONFIDENCE_THRESHOLD:.0%} threshold. Triggering clarifying question flow."
        ),
        detail=result.clarifying_question,
    )


def assert_confidence(confidence: float, customer_id: str) -> None:
    """
    Quick check for when you already have a raw float (not a ConfidenceResult).
    """
    if confidence < CONFIDENCE_THRESHOLD:
        raise LowConfidenceError(
            message=(
                f"Confidence {confidence:.2%} below {CONFIDENCE_THRESHOLD:.0%} threshold."
            )
        )
