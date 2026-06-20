"""
SAARTHI AI — MITRA Agent (Customer Acquisition)
Handles: account_opened, kyc_incomplete events.
Guides new customers through onboarding, KYC, and product discovery.

Follows the same 10-step pipeline as margdarshan_agent.py (reference implementation).
"""
from __future__ import annotations

from backend.guardrails.consent_validator import get_safe_consent, require_personalisation_consent
from backend.memory.customer_memory import customer_memory
from backend.models.audit_log import AuditStatus, AuditStep
from backend.models.event import Event, EventType
from backend.models.recommendation import (
    ActionPreview,
    FallbackResponse,
    ProductType,
    Recommendation,
    RecommendationStatus,
)
from backend.security.human_in_loop import human_in_loop_gate
from backend.services.audit_service import audit_service
from backend.services.confidence_engine import confidence_engine
from backend.services.recommendation_engine import recommendation_engine
from backend.utils import json_repository as repo
from backend.utils.constants import AGENT_MITRA
from backend.utils.error_handlers import CustomerNotFoundError
from backend.utils.logging_config import get_logger
from datetime import datetime, timedelta, timezone

logger = get_logger(__name__)
AGENT_NAME = AGENT_MITRA


async def run_mitra(customer_id: str, event: Event) -> Recommendation | FallbackResponse:
    """MITRA agent entrypoint — mirrors margdarshan pipeline structure."""

    logger.info("mitra_started", customer_id=customer_id, event_type=event.event_type)

    audit_service.log_step(
        customer_id=customer_id, step=AuditStep.WEBHOOK_TRIGGER,
        agent=AGENT_NAME, event_id=event.event_id,
    )

    customer_record = repo.find_by_id("customers", "customer_id", customer_id)
    if not customer_record:
        raise CustomerNotFoundError(message=f"Customer '{customer_id}' not found")

    with audit_service.timed_step(customer_id, AuditStep.MEMORY_EVALUATION, AGENT_NAME, event.event_id):
        customer_memory.set_last_agent(customer_id, AGENT_NAME)

    with audit_service.timed_step(customer_id, AuditStep.CONFIDENCE_CHECK, AGENT_NAME, event.event_id):
        confidence_result = await confidence_engine.evaluate_event(event.event_type, event.source)

    if not confidence_result.should_proceed:
        audit_service.log_step(customer_id, AuditStep.FALLBACK_TRIGGERED, AGENT_NAME, event.event_id,
                               metadata={"confidence": confidence_result.confidence})
        return recommendation_engine.build_fallback_response(customer_id, AGENT_NAME, confidence_result, event.event_id)

    audit_service.log_step(customer_id, AuditStep.AGENT_ACTIVATED, AGENT_NAME, event.event_id,
                           metadata={"event_type": event.event_type})

    consent = get_safe_consent(customer_id)
    require_personalisation_consent(consent, customer_id)

    recommendation = _build_kyc_recommendation(customer_record, event)

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
        metadata={"product_type": recommendation.product_type},
    )

    return recommendation


def _build_kyc_recommendation(customer: dict, event: Event) -> Recommendation:
    from backend.utils import json_repository as repo
    rec_id = repo.generate_id("REC-")
    return Recommendation(
        recommendation_id=rec_id,
        customer_id=customer["customer_id"],
        agent_source=AGENT_NAME,
        event_id=event.event_id,
        product_type=ProductType.KYC_COMPLETION,
        title="Complete Your KYC to Unlock All Banking Features",
        description="Your KYC is incomplete. Complete it now to enable UPI, YONO, FDs, and all digital banking features.",
        why_explanation="Your account was recently opened but KYC verification is still pending. KYC completion unlocks your full banking experience.",
        action_preview=ActionPreview(
            product="SBI KYC Completion",
            product_type=ProductType.KYC_COMPLETION,
            action_label="Complete KYC Now",
            action_details={"documents_needed": ["Aadhaar", "PAN"], "time_required": "10 minutes"},
        ),
        confidence_score=0.94,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=72),
    )
