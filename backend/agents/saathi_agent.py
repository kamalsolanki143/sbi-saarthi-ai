"""
SAARTHI AI — SAATHI Agent (Customer Engagement)
Handles: life_event, education_expense, festival_period, travel_spending, spending_anomaly.

Follows the same 10-step pipeline as margdarshan_agent.py (reference implementation).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from backend.guardrails.consent_validator import get_safe_consent, require_personalisation_consent
from backend.memory.customer_memory import customer_memory
from backend.models.audit_log import AuditStep
from backend.models.event import Event, EventType
from backend.models.recommendation import (
    ActionPreview,
    FallbackResponse,
    ProductType,
    Recommendation,
)
from backend.security.human_in_loop import human_in_loop_gate
from backend.services.audit_service import audit_service
from backend.services.confidence_engine import confidence_engine
from backend.services.recommendation_engine import recommendation_engine
from backend.utils import json_repository as repo
from backend.utils.constants import AGENT_SAATHI
from backend.utils.error_handlers import CustomerNotFoundError
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)
AGENT_NAME = AGENT_SAATHI


async def run_saathi(customer_id: str, event: Event) -> Recommendation | FallbackResponse:
    """SAATHI agent entrypoint — mirrors margdarshan pipeline structure."""

    logger.info("saathi_started", customer_id=customer_id, event_type=event.event_type)

    audit_service.log_step(customer_id, AuditStep.WEBHOOK_TRIGGER, AGENT_NAME, event_id=event.event_id)

    customer_record = repo.find_by_id("customers", "customer_id", customer_id)
    if not customer_record:
        raise CustomerNotFoundError(message=f"Customer '{customer_id}' not found")

    with audit_service.timed_step(customer_id, AuditStep.MEMORY_EVALUATION, AGENT_NAME, event.event_id):
        memory_context = customer_memory.get_customer_context(customer_id)
        customer_memory.set_last_agent(customer_id, AGENT_NAME)

    with audit_service.timed_step(customer_id, AuditStep.CONFIDENCE_CHECK, AGENT_NAME, event.event_id):
        confidence_result = await confidence_engine.evaluate_event(event.event_type, event.source)

    if not confidence_result.should_proceed:
        audit_service.log_step(customer_id, AuditStep.FALLBACK_TRIGGERED, AGENT_NAME, event_id=event.event_id,
                               metadata={"confidence": confidence_result.confidence})
        return recommendation_engine.build_fallback_response(customer_id, AGENT_NAME, confidence_result, event.event_id)

    audit_service.log_step(customer_id, AuditStep.AGENT_ACTIVATED, AGENT_NAME, event_id=event.event_id,
                           metadata={"event_type": event.event_type})

    consent = get_safe_consent(customer_id)
    require_personalisation_consent(consent, customer_id)

    recommendation = _handle_event(customer_record, event)

    from backend.guardrails.action_validator import validate_action
    with audit_service.timed_step(customer_id, AuditStep.PYDANTIC_VALIDATION, AGENT_NAME, event.event_id):
        validate_action(recommendation.action_preview, customer_id)

    human_in_loop_gate.register_recommendation(recommendation.recommendation_id, customer_id)
    from backend.routes.recommendation import store_recommendation
    store_recommendation(recommendation.model_dump(mode="json"))

    audit_service.log_step(
        customer_id=customer_id, step=AuditStep.RECOMMENDATION_GENERATED,
        agent=AGENT_NAME, event_id=event.event_id,
        recommendation_id=recommendation.recommendation_id,
    )

    return recommendation


def _handle_event(customer: dict, event: Event) -> Recommendation:
    rec_id = repo.generate_id("REC-")
    customer_id = customer["customer_id"]

    if event.event_type == EventType.EDUCATION_EXPENSE:
        return Recommendation(
            recommendation_id=rec_id, customer_id=customer_id, agent_source=AGENT_NAME,
            event_id=event.event_id, product_type=ProductType.RECURRING_DEPOSIT,
            title="Start a Recurring Deposit for Education Goals",
            description="Save consistently for your education expenses with an SBI Recurring Deposit.",
            why_explanation="We noticed education-related expenses in your account. A Recurring Deposit helps you save systematically for future education costs.",
            action_preview=ActionPreview(
                product="SBI Recurring Deposit", product_type=ProductType.RECURRING_DEPOSIT,
                amount=2000.0, tenure="2 Years", interest_rate=6.50,
                action_label="Start Recurring Deposit",
            ),
            confidence_score=0.88,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=72),
        )

    # Default: digital banking awareness
    return Recommendation(
        recommendation_id=rec_id, customer_id=customer_id, agent_source=AGENT_NAME,
        event_id=event.event_id, product_type=ProductType.DIGITAL_LITERACY,
        title="Make the Most of Your SBI Account",
        description="Explore digital banking features tailored to your spending patterns.",
        why_explanation="Based on your recent activity, we have personalised recommendations for you.",
        action_preview=ActionPreview(
            product="YONO SBI", product_type=ProductType.YONO_ADOPTION,
            action_label="Explore YONO Features",
        ),
        confidence_score=0.86,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=72),
    )
