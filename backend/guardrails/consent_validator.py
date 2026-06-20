"""
SAARTHI AI — Consent Validator (Guardrail)
Hard enforcement of DPDP consent requirements.

RULES:
  - voice_processing=False  → BLOCK all Sarvam AI voice calls
  - memory_storage=False    → BLOCK all customer_memory.py writes
  - personalized_recommendations=False → BLOCK Recommendation creation

These are hard blocks — no workarounds allowed.
Raises ConsentRequiredError which returns HTTP 403 to the client.

Used by: customer_memory.py, routes/voice.py, agents (before building recs),
         recommendation_engine.py
"""
from __future__ import annotations

from backend.models.consent import ConsentRecord
from backend.utils.error_handlers import ConsentRequiredError
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)


def require_voice_consent(consent: ConsentRecord | None, customer_id: str) -> None:
    """
    Enforce voice processing consent.
    Call before any Sarvam AI API call.

    Raises:
        ConsentRequiredError: If voice_processing consent is not granted.
    """
    if consent is None or not consent.voice_processing:
        logger.warning(
            "consent_blocked_voice",
            customer_id=customer_id,
            has_consent_record=consent is not None,
        )
        raise ConsentRequiredError(
            message="Voice processing consent required",
            detail=(
                "Please grant voice processing consent to use voice features. "
                "You can do this in the Consent Settings section of the app."
            ),
        )


def require_memory_consent(consent: ConsentRecord | None, customer_id: str) -> None:
    """
    Enforce memory storage consent.
    Call before writing anything to customer_memory.py.

    Raises:
        ConsentRequiredError: If memory_storage consent is not granted.
    """
    if consent is None or not consent.memory_storage:
        logger.warning(
            "consent_blocked_memory",
            customer_id=customer_id,
        )
        raise ConsentRequiredError(
            message="Memory storage consent required",
            detail=(
                "Personalized features require memory storage consent. "
                "Grant this permission to enable a more tailored experience."
            ),
        )


def require_personalisation_consent(
    consent: ConsentRecord | None, customer_id: str
) -> None:
    """
    Enforce personalized recommendation consent.
    Call before building or returning any Recommendation.

    Raises:
        ConsentRequiredError: If personalized_recommendations consent is not granted.
    """
    if consent is None or not consent.personalized_recommendations:
        logger.warning(
            "consent_blocked_personalisation",
            customer_id=customer_id,
        )
        raise ConsentRequiredError(
            message="Personalised recommendations consent required",
            detail=(
                "To receive AI-powered banking recommendations, please grant "
                "personalised recommendations consent in Settings."
            ),
        )


def check_all_consents(
    consent: ConsentRecord | None,
    customer_id: str,
    require_voice: bool = False,
    require_memory: bool = False,
    require_personalisation: bool = False,
) -> None:
    """
    Batch consent check — call with booleans for what this operation needs.
    Raises ConsentRequiredError on first missing consent.
    """
    if require_voice:
        require_voice_consent(consent, customer_id)
    if require_memory:
        require_memory_consent(consent, customer_id)
    if require_personalisation:
        require_personalisation_consent(consent, customer_id)


def get_safe_consent(customer_id: str) -> ConsentRecord | None:
    """
    Helper to fetch consent record for a customer without raising on missing.
    Returns None if no consent record exists.
    """
    from backend.services.consent_service import consent_service
    return consent_service.get_consent(customer_id)
