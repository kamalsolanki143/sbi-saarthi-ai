"""
SAARTHI AI — Consent Routes
Grant/revoke/check DPDP consent permissions.
"""
from __future__ import annotations

from fastapi import APIRouter

from backend.models.consent import ConsentGrantRequest, ConsentResponse, ConsentRevokeRequest
from backend.services.consent_service import consent_service
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/{customer_id}", response_model=ConsentResponse)
async def get_consent(customer_id: str):
    """Get the current consent state for a customer."""
    record = consent_service.get_or_create_consent(customer_id.upper())
    return ConsentResponse.from_record(record)


@router.post("/{customer_id}/grant", response_model=ConsentResponse)
async def grant_consent(customer_id: str, request: ConsentGrantRequest):
    """
    Grant one or more consent permissions.
    Explicit opt-in required for each permission (DPDP compliance).
    """
    record = consent_service.grant_consent(customer_id.upper(), request)
    return ConsentResponse.from_record(record, message="Consent updated successfully")


@router.post("/{customer_id}/revoke", response_model=ConsentResponse)
async def revoke_consent(customer_id: str, request: ConsentRevokeRequest):
    """
    Revoke one or more consent permissions.
    Revoking memory_storage will stop all future personalisation.
    """
    record = consent_service.revoke_consent(customer_id.upper(), request)
    return ConsentResponse.from_record(record, message="Consent revoked successfully")
