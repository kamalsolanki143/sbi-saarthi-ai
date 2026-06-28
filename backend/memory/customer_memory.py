"""
SAARTHI AI — Customer Memory
Shared memory abstraction used by ALL THREE agents (MITRA, MARGDARSHAN, SAATHI).

This is the single source of truth for "what do we know about this customer."
Memory reads/writes are consent-gated:
  - Any write is blocked if memory_storage consent is off (DPDP compliance)
  - Reads always succeed (agents may need context even without personalization)

Storage layers:
  - Redis: Short-term session context (TTL 1 hour)
  - ChromaDB (vector_memory.py): Long-term semantic memory

Used by: margdarshan_agent.py, mitra_agent.py, saathi_agent.py
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from backend.guardrails.consent_validator import require_memory_consent
from backend.memory.redis_memory import redis_memory
from backend.services.consent_service import consent_service
from backend.utils.constants import (
    REDIS_KEY_PREFIX_CUSTOMER,
    REDIS_KEY_PREFIX_INTERACTION,
)
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)


class CustomerMemory:
    """
    Cross-agent shared customer memory.

    All agents call this instead of touching Redis or ChromaDB directly.
    Memory writes are gated on consent. Reads are always allowed.
    """

    def get_customer_context(self, customer_id: str) -> dict[str, Any]:
        """
        Retrieve the full customer context from memory.
        Returns empty dict if no context exists.
        """
        key = f"{REDIS_KEY_PREFIX_CUSTOMER}{customer_id}"
        context = redis_memory.get_json(key) or {}
        logger.debug("customer_context_read", customer_id=customer_id, has_context=bool(context))
        return context

    def update_customer_context(
        self,
        customer_id: str,
        updates: dict[str, Any],
    ) -> None:
        """
        Write/merge customer context into memory.
        BLOCKED if memory_storage consent is off.
        """
        consent = consent_service.get_consent(customer_id)
        try:
            require_memory_consent(consent, customer_id)
        except Exception as e:
            logger.info(
                "memory_write_blocked_no_consent",
                customer_id=customer_id,
                updates_keys=list(updates.keys()),
            )
            return  # Silently skip (don't raise — agents should degrade gracefully)

        key = f"{REDIS_KEY_PREFIX_CUSTOMER}{customer_id}"
        existing = redis_memory.get_json(key) or {}
        merged = {
            **existing,
            **updates,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
        redis_memory.set_json(key, merged)
        logger.info(
            "customer_context_updated",
            customer_id=customer_id,
            updated_keys=list(updates.keys()),
        )

    def log_interaction(
        self,
        customer_id: str,
        agent: str,
        interaction_type: str,
        details: dict[str, Any],
    ) -> None:
        """
        Log an interaction to the customer's history.
        BLOCKED if memory_storage consent is off.
        """
        consent = consent_service.get_consent(customer_id)
        try:
            require_memory_consent(consent, customer_id)
        except Exception:
            logger.debug("interaction_log_skipped_no_consent", customer_id=customer_id)
            return

        history_key = f"{REDIS_KEY_PREFIX_INTERACTION}{customer_id}"
        existing_history = redis_memory.get_json(history_key) or {"interactions": []}

        interaction = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": agent,
            "type": interaction_type,
            "details": details,
        }
        existing_history["interactions"].append(interaction)

        # Keep last 50 interactions in session memory
        existing_history["interactions"] = existing_history["interactions"][-50:]
        redis_memory.set_json(history_key, existing_history)

    def get_interaction_history(self, customer_id: str) -> list[dict[str, Any]]:
        """Retrieve interaction history for a customer (read — no consent gate)."""
        history_key = f"{REDIS_KEY_PREFIX_INTERACTION}{customer_id}"
        data = redis_memory.get_json(history_key)
        return data.get("interactions", []) if data else []

    def clear_session(self, customer_id: str) -> None:
        """Clear all session memory for a customer (e.g., on logout)."""
        redis_memory.delete(f"{REDIS_KEY_PREFIX_CUSTOMER}{customer_id}")
        redis_memory.delete(f"{REDIS_KEY_PREFIX_INTERACTION}{customer_id}")
        logger.info("session_cleared", customer_id=customer_id)

    def get_last_agent(self, customer_id: str) -> Optional[str]:
        """Which agent last interacted with this customer?"""
        context = self.get_customer_context(customer_id)
        return context.get("last_agent")

    def set_last_agent(self, customer_id: str, agent: str) -> None:
        self.update_customer_context(customer_id, {"last_agent": agent})


# ── Singleton ───────────────────────────────────────────────────────────────
customer_memory = CustomerMemory()
