"""
SAARTHI AI — Consent Service
Business logic for managing DPDP-compliant customer consent.
All consent reads/writes go through this service.

Used by: routes/consent.py, consent_validator.py (guardrail),
         customer_memory.py (blocks writes if memory_storage=False)
Maps to: database/consent_records.json
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from backend.models.consent import ConsentGrantRequest, ConsentRecord, ConsentResponse, ConsentRevokeRequest
from backend.utils import json_repository as repo
from backend.utils.error_handlers import CustomerNotFoundError
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)

COLLECTION = "consent_records"


class ConsentService:
    """Manages customer consent state."""

    def get_consent(self, customer_id: str) -> Optional[ConsentRecord]:
        """Retrieve current consent state for a customer. Returns None if no record exists."""
        record = repo.find_one_by_field(COLLECTION, "customer_id", customer_id)
        if record is None:
            return None
        return ConsentRecord(**record)

    def get_or_create_consent(self, customer_id: str) -> ConsentRecord:
        """
        Get consent for a customer, creating a default (all-False) record if none exists.
        New customers start with all permissions off — explicit opt-in required (DPDP).
        """
        existing = self.get_consent(customer_id)
        if existing:
            return existing

        consent_id = repo.generate_id("CON-")
        new_record = ConsentRecord(
            consent_id=consent_id,
            customer_id=customer_id,
            voice_processing=False,
            memory_storage=False,
            personalized_recommendations=False,
        )
        repo.insert(COLLECTION, new_record.model_dump(mode="json"))
        logger.info("consent_record_created", customer_id=customer_id, consent_id=consent_id)
        return new_record

    def grant_consent(
        self, customer_id: str, request: ConsentGrantRequest
    ) -> ConsentRecord:
        """Update consent permissions — only sets permissions to True if explicitly set."""
        record = self.get_or_create_consent(customer_id)

        updates: dict = {"updated_at": datetime.now(timezone.utc).isoformat()}
        if request.voice_processing is not None:
            updates["voice_processing"] = request.voice_processing
        if request.memory_storage is not None:
            updates["memory_storage"] = request.memory_storage
        if request.personalized_recommendations is not None:
            updates["personalized_recommendations"] = request.personalized_recommendations

        repo.upsert(COLLECTION, "customer_id", customer_id, updates)

        updated = self.get_consent(customer_id)
        logger.info(
            "consent_granted",
            customer_id=customer_id,
            updates=updates,
        )
        return updated

    def revoke_consent(
        self, customer_id: str, request: ConsentRevokeRequest
    ) -> ConsentRecord:
        """Revoke specific consent permissions."""
        record = self.get_or_create_consent(customer_id)

        updates: dict = {"updated_at": datetime.now(timezone.utc).isoformat()}
        if request.voice_processing is not None and request.voice_processing:
            updates["voice_processing"] = False
        if request.memory_storage is not None and request.memory_storage:
            updates["memory_storage"] = False
        if request.personalized_recommendations is not None and request.personalized_recommendations:
            updates["personalized_recommendations"] = False

        repo.upsert(COLLECTION, "customer_id", customer_id, updates)

        updated = self.get_consent(customer_id)
        logger.info("consent_revoked", customer_id=customer_id, updates=updates)
        return updated

    def can_process_voice(self, customer_id: str) -> bool:
        record = self.get_consent(customer_id)
        return record.can_process_voice() if record else False

    def can_store_memory(self, customer_id: str) -> bool:
        record = self.get_consent(customer_id)
        return record.can_store_memory() if record else False

    def can_personalise(self, customer_id: str) -> bool:
        record = self.get_consent(customer_id)
        return record.can_personalise() if record else False


# ── Singleton ───────────────────────────────────────────────────────────────
consent_service = ConsentService()
