"""
SAARTHI AI — Auth Routes
Session management and MPIN verification.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.security.biometric_gate import biometric_gate
from backend.security.mpin_gate import mpin_gate
from backend.utils import json_repository as repo
from backend.utils.error_handlers import CustomerNotFoundError
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()


class SessionCreateRequest(BaseModel):
    customer_id: str
    device_id: str = Field(default="", description="Device identifier for session binding")


class MPINVerifyRequest(BaseModel):
    customer_id: str
    mpin: str = Field(..., min_length=4, max_length=6)
    recommendation_id: str = Field(..., description="Recommendation to verify MPIN for")


class BiometricVerifyRequest(BaseModel):
    customer_id: str
    biometric_token: str
    biometric_type: str = "fingerprint"
    recommendation_id: str


@router.post("/session")
async def create_session(request: SessionCreateRequest):
    """Create a new session for a customer."""
    customer = repo.find_by_id("customers", "customer_id", request.customer_id.upper())
    if not customer:
        raise CustomerNotFoundError(message=f"Customer '{request.customer_id}' not found")

    session_id = f"SES-{uuid.uuid4().hex[:12].upper()}"
    logger.info("session_created", session_id=session_id, customer_id=request.customer_id)

    return {
        "session_id": session_id,
        "customer_id": request.customer_id.upper(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "message": "Session created successfully",
    }


@router.post("/mpin/verify")
async def verify_mpin(request: MPINVerifyRequest):
    """Verify MPIN for a specific recommendation. Part of human-in-the-loop chain."""
    mpin_gate.verify(request.customer_id.upper(), request.mpin)
    return {
        "verified": True,
        "customer_id": request.customer_id.upper(),
        "recommendation_id": request.recommendation_id,
        "message": "MPIN verified successfully",
    }


@router.post("/biometric/verify")
async def verify_biometric(request: BiometricVerifyRequest):
    """Verify biometric authentication (demo: always passes)."""
    result = biometric_gate.verify(
        customer_id=request.customer_id.upper(),
        biometric_token=request.biometric_token,
        biometric_type=request.biometric_type,
    )
    return {
        "verified": result,
        "customer_id": request.customer_id.upper(),
        "recommendation_id": request.recommendation_id,
        "biometric_type": request.biometric_type,
        "message": "Biometric verified successfully",
    }
