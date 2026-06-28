"""
SAARTHI AI — MARGDARSHAN Agent (MVP Priority)
Digital Adoption Agent — helps existing customers get the most from SBI digital banking.

Handles events:
  - salary_credit → detect idle balance → recommend FD
  - idle_balance → recommend FD
  - upi_not_activated → recommend UPI activation
  - yono_not_adopted → recommend YONO
  - subsidy_credit → guide subsidy optimisation (FD if eligible)
  - fd_eligible → direct FD recommendation

Pipeline (reference implementation for MITRA and SAATHI):
  1. Pull customer context from customer_memory.py
  2. Run confidence check via confidence_engine.py
  3. Check personalization consent via consent_validator.py
  4. Run domain-specific logic (fd_engine, etc.)
  5. Build validated Recommendation via recommendation_engine.py
  6. Register with human_in_loop_gate
  7. Log every step to audit_service.py

This agent is the reference implementation — MITRA and SAATHI follow the same pattern.
"""
from __future__ import annotations

from typing import Optional

from backend.guardrails.confidence_checker import check_confidence
from backend.guardrails.consent_validator import require_personalisation_consent, get_safe_consent
from backend.memory.customer_memory import customer_memory
from backend.models.audit_log import AuditStatus, AuditStep
from backend.models.event import Event, EventType
from backend.models.recommendation import FallbackResponse, Recommendation
from backend.security.human_in_loop import human_in_loop_gate
from backend.services.audit_service import audit_service
from backend.services.confidence_engine import confidence_engine
from backend.services.fd_engine import fd_engine
from backend.services.recommendation_engine import recommendation_engine
from backend.utils import json_repository as repo
from backend.utils.constants import AGENT_MARGDARSHAN
from backend.utils.error_handlers import (
    CustomerNotFoundError,
    LowConfidenceError,
)
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)

AGENT_NAME = AGENT_MARGDARSHAN


async def run_margdarshan(
    customer_id: str,
    event: Event,
) -> Recommendation | FallbackResponse:
    """
    Main entrypoint for the MARGDARSHAN agent.
    Called by the orchestrator when a Margdarshan-assigned event is received.

    Args:
        customer_id: The customer to process.
        event: The triggering event.

    Returns:
        Recommendation — if confidence ≥ 0.85 and all guardrails pass.
        FallbackResponse — if confidence < 0.85 (clarifying question).

    Raises:
        CustomerNotFoundError: If customer does not exist.
    """
    logger.info(
        "margdarshan_started",
        customer_id=customer_id,
        event_id=event.event_id,
        event_type=event.event_type,
    )

    # ── Step 1: Webhook trigger logged ────────────────────────────────────
    audit_service.log_step(
        customer_id=customer_id,
        step=AuditStep.WEBHOOK_TRIGGER,
        agent=AGENT_NAME,
        event_id=event.event_id,
        metadata={"event_type": event.event_type, "amount": event.amount},
    )

    # ── Step 2: Load customer from DB ─────────────────────────────────────
    customer_record = repo.find_by_id("customers", "customer_id", customer_id)
    if not customer_record:
        audit_service.log_step(
            customer_id=customer_id,
            step=AuditStep.MEMORY_EVALUATION,
            agent=AGENT_NAME,
            event_id=event.event_id,
            status=AuditStatus.FAILED,
            error_message="Customer not found",
        )
        raise CustomerNotFoundError(message=f"Customer '{customer_id}' not found")

    # ── Step 3: Memory evaluation ─────────────────────────────────────────
    with audit_service.timed_step(
        customer_id=customer_id,
        step=AuditStep.MEMORY_EVALUATION,
        agent=AGENT_NAME,
        event_id=event.event_id,
    ):
        memory_context = customer_memory.get_customer_context(customer_id)
        customer_memory.set_last_agent(customer_id, AGENT_NAME)

    # ── Step 4: Confidence check ──────────────────────────────────────────
    with audit_service.timed_step(
        customer_id=customer_id,
        step=AuditStep.CONFIDENCE_CHECK,
        agent=AGENT_NAME,
        event_id=event.event_id,
    ):
        confidence_result = await confidence_engine.evaluate_event(
            event_type=event.event_type,
            source=event.source,
        )

    # If confidence too low, return fallback (do NOT proceed)
    if not confidence_result.should_proceed:
        audit_service.log_step(
            customer_id=customer_id,
            step=AuditStep.FALLBACK_TRIGGERED,
            agent=AGENT_NAME,
            event_id=event.event_id,
            metadata={"confidence": confidence_result.confidence},
        )
        return recommendation_engine.build_fallback_response(
            customer_id=customer_id,
            agent=AGENT_NAME,
            confidence_result=confidence_result,
            session_id=event.event_id,
        )

    # ── Step 5: Agent logic activated ─────────────────────────────────────
    audit_service.log_step(
        customer_id=customer_id,
        step=AuditStep.AGENT_ACTIVATED,
        agent=AGENT_NAME,
        event_id=event.event_id,
        metadata={
            "event_type": event.event_type,
            "confidence": confidence_result.confidence,
        },
    )

    # ── Step 6: Consent check ─────────────────────────────────────────────
    audit_service.log_step(
        customer_id=customer_id,
        step=AuditStep.CONSENT_CHECK,
        agent=AGENT_NAME,
        event_id=event.event_id,
    )
    consent = get_safe_consent(customer_id)
    try:
        require_personalisation_consent(consent, customer_id)
    except Exception as e:
        # No personalisation consent — return generic guidance
        audit_service.log_step(
            customer_id=customer_id,
            step=AuditStep.CONSENT_CHECK,
            agent=AGENT_NAME,
            event_id=event.event_id,
            status=AuditStatus.FAILED,
            error_message=str(e),
        )
        raise

    # ── Step 7: Domain-specific logic ─────────────────────────────────────
    recommendation = await _handle_event(customer_record, event, memory_context)

    # ── Step 8: Pydantic validation ───────────────────────────────────────
    with audit_service.timed_step(
        customer_id=customer_id,
        step=AuditStep.PYDANTIC_VALIDATION,
        agent=AGENT_NAME,
        event_id=event.event_id,
    ):
        # Validate action preview (the action_validator guardrail)
        from backend.guardrails.action_validator import validate_action
        validate_action(recommendation.action_preview, customer_id)

    # ── Step 9: Register with human-in-the-loop gate ──────────────────────
    human_in_loop_gate.register_recommendation(
        recommendation_id=recommendation.recommendation_id,
        customer_id=customer_id,
    )
    from backend.routes.recommendation import store_recommendation
    store_recommendation(recommendation.model_dump(mode="json"))

    # ── Step 10: Recommendation generated ────────────────────────────────
    audit_service.log_step(
        customer_id=customer_id,
        step=AuditStep.RECOMMENDATION_GENERATED,
        agent=AGENT_NAME,
        event_id=event.event_id,
        recommendation_id=recommendation.recommendation_id,
        metadata={
            "product_type": recommendation.product_type,
            "title": recommendation.title,
            "confidence": recommendation.confidence_score,
        },
    )

    # Update memory with this interaction
    customer_memory.log_interaction(
        customer_id=customer_id,
        agent=AGENT_NAME,
        interaction_type=f"recommendation_{recommendation.product_type}",
        details={"recommendation_id": recommendation.recommendation_id},
    )

    logger.info(
        "margdarshan_completed",
        customer_id=customer_id,
        event_id=event.event_id,
        recommendation_id=recommendation.recommendation_id,
    )
    return recommendation


async def _handle_event(
    customer: dict, event: Event, context: dict
) -> Recommendation:
    """Dispatch to the appropriate handler based on event type."""
    event_type = event.event_type

    if event_type in (EventType.SALARY_CREDIT, EventType.IDLE_BALANCE, EventType.FD_ELIGIBLE):
        return await _handle_fd_opportunity(customer, event)

    if event_type == EventType.SUBSIDY_CREDIT:
        return await _handle_subsidy(customer, event)

    if event_type == EventType.UPI_NOT_ACTIVATED:
        return _handle_upi_activation(customer, event)

    if event_type == EventType.YONO_NOT_ADOPTED:
        return _handle_yono_adoption(customer, event)

    # Fallback: FD recommendation (most common Margdarshan action)
    return await _handle_fd_opportunity(customer, event)


async def _handle_fd_opportunity(customer: dict, event: Event) -> Recommendation:
    """Salary credit or idle balance → FD recommendation."""
    balance = customer.get("current_balance", 0.0)
    persona = customer.get("persona", "unknown")
    dob = customer.get("date_of_birth")
    customer_id = customer.get("customer_id")

    fd_result = fd_engine.calculate(
        current_balance=balance,
        persona=persona,
        customer_id=customer_id,
        date_of_birth=dob,
    )

    if not fd_result.eligible:
        # UPI recommendation as fallback if FD not eligible
        return recommendation_engine.build_upi_recommendation(
            customer_id=customer_id,
            agent_source=AGENT_NAME,
            event_id=event.event_id,
        )

    return recommendation_engine.build_fd_recommendation(
        customer_id=customer_id,
        agent_source=AGENT_NAME,
        fd_result=fd_result,
        event_id=event.event_id,
        persona=persona,
    )


async def _handle_subsidy(customer: dict, event: Event) -> Recommendation:
    """Subsidy credit → check if FD eligible, otherwise guide on subsidy usage."""
    return await _handle_fd_opportunity(customer, event)


def _handle_upi_activation(customer: dict, event: Event) -> Recommendation:
    return recommendation_engine.build_upi_recommendation(
        customer_id=customer["customer_id"],
        agent_source=AGENT_NAME,
        event_id=event.event_id,
    )


def _handle_yono_adoption(customer: dict, event: Event) -> Recommendation:
    return recommendation_engine.build_yono_recommendation(
        customer_id=customer["customer_id"],
        agent_source=AGENT_NAME,
        event_id=event.event_id,
    )
