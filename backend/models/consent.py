"""
SAARTHI AI — Consent Model
DPDP (Digital Personal Data Protection Act) compliant consent management.

Maps to: database/consent_records.json
Used by: consent_service.py, consent_validator.py (guardrail),
         customer_memory.py (blocks writes if memory_storage=False),
         routes/consent.py

The three consent permissions:
  1. voice_processing — required for Sarvam AI voice features
  2. memory_storage — required for personalization across sessions
  3. personalized_recommendations — required for agent-generated recs
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ── Core Model ─────────────────────────────────────────────────────────────

class ConsentRecord(BaseModel):
    """
    DPDP-compliant consent state for a customer.
    Stored in database/consent_records.json.

    consent_validator.py enforces these hard rules:
      - voice_processing=False → block all Sarvam AI voice calls
      - memory_storage=False → block all writes to customer_memory.py
      - personalized_recommendations=False → block Recommendation creation
    """
    model_config = ConfigDict(use_enum_values=True)

    consent_id: str = Field(..., description="Unique consent record ID")
    customer_id: str = Field(..., description="Customer this consent belongs to")

    # The three DPDP permission flags
    voice_processing: bool = Field(
        False,
        description="Customer consents to voice data being processed via Sarvam AI",
    )
    memory_storage: bool = Field(
        False,
        description="Customer consents to interaction history being stored for personalization",
    )
    personalized_recommendations: bool = Field(
        False,
        description="Customer consents to receiving AI-personalized banking recommendations",
    )

    granted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    dpdp_version: str = Field("1.0", description="DPDP regulation version this consent was collected under")

    def can_process_voice(self) -> bool:
        return self.voice_processing

    def can_store_memory(self) -> bool:
        return self.memory_storage

    def can_personalise(self) -> bool:
        return self.personalized_recommendations

    def all_granted(self) -> bool:
        return all([
            self.voice_processing,
            self.memory_storage,
            self.personalized_recommendations,
        ])

    def any_granted(self) -> bool:
        return any([
            self.voice_processing,
            self.memory_storage,
            self.personalized_recommendations,
        ])


# ── Request / Response ──────────────────────────────────────────────────────

class ConsentGrantRequest(BaseModel):
    """Request body for POST /consent/{customer_id}/grant."""
    voice_processing: Optional[bool] = None
    memory_storage: Optional[bool] = None
    personalized_recommendations: Optional[bool] = None


class ConsentRevokeRequest(BaseModel):
    """Request body for POST /consent/{customer_id}/revoke."""
    voice_processing: Optional[bool] = None
    memory_storage: Optional[bool] = None
    personalized_recommendations: Optional[bool] = None


class ConsentResponse(BaseModel):
    """Response for GET /consent/{customer_id}."""
    customer_id: str
    voice_processing: bool
    memory_storage: bool
    personalized_recommendations: bool
    updated_at: datetime
    message: str

    @classmethod
    def from_record(cls, record: ConsentRecord, message: str = "Consent state retrieved") -> "ConsentResponse":
        return cls(
            customer_id=record.customer_id,
            voice_processing=record.voice_processing,
            memory_storage=record.memory_storage,
            personalized_recommendations=record.personalized_recommendations,
            updated_at=record.updated_at,
            message=message,
        )
