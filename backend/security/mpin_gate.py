"""
SAARTHI AI — MPIN Gate
Verifies a customer's MPIN before allowing execution.

Demo scope: Plain-text MPIN comparison against customers.json.
Production scope: This would hash the input and compare against a PBKDF2/bcrypt hash,
                  with rate limiting, lockout, and HSM integration.

Used by: routes/auth.py, human_in_loop.py (MPIN_VERIFIED stage)
"""
from __future__ import annotations

import os
from typing import Optional

from backend.utils import json_repository as repo
from backend.utils.constants import DEFAULT_DEMO_MPIN, MPIN_MAX_ATTEMPTS
from backend.utils.error_handlers import CustomerNotFoundError, MPINVerificationError
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)

# Track failed attempts in-memory (production: Redis with TTL)
_failed_attempts: dict[str, int] = {}


class MPINGate:
    """
    MPIN verification gate.

    Verify → returns True if correct.
    Raises MPINVerificationError on incorrect MPIN.
    Raises MPINVerificationError with lockout message after MAX_ATTEMPTS.
    """

    def verify(self, customer_id: str, mpin: str) -> bool:
        """
        Verify the MPIN for a customer.

        Args:
            customer_id: Customer identifier.
            mpin: The MPIN submitted by the customer.

        Returns:
            True if MPIN is correct.

        Raises:
            MPINVerificationError: If MPIN is incorrect or customer is locked out.
            CustomerNotFoundError: If customer does not exist.
        """
        # Check lockout
        attempts = _failed_attempts.get(customer_id, 0)
        if attempts >= MPIN_MAX_ATTEMPTS:
            logger.warning("mpin_account_locked", customer_id=customer_id, attempts=attempts)
            raise MPINVerificationError(
                message="Account locked due to too many incorrect MPIN attempts",
                detail=f"Contact SBI support to unlock. Maximum {MPIN_MAX_ATTEMPTS} attempts exceeded.",
            )

        # Fetch customer record
        customer = repo.find_by_id("customers", "customer_id", customer_id)
        if customer is None:
            raise CustomerNotFoundError(
                message=f"Customer '{customer_id}' not found",
            )

        # Get stored MPIN (demo: plain text; production: hashed)
        stored_mpin = customer.get("mpin_hash", DEFAULT_DEMO_MPIN)

        if not self._verify_mpin(mpin, stored_mpin):
            _failed_attempts[customer_id] = attempts + 1
            remaining = MPIN_MAX_ATTEMPTS - _failed_attempts[customer_id]
            logger.warning(
                "mpin_verification_failed",
                customer_id=customer_id,
                attempts=_failed_attempts[customer_id],
                remaining=remaining,
            )
            raise MPINVerificationError(
                message="Incorrect MPIN",
                detail=(
                    f"You have {remaining} attempt{'s' if remaining != 1 else ''} remaining "
                    f"before the account is temporarily locked."
                ),
            )

        # Success — reset attempt counter
        _failed_attempts.pop(customer_id, None)
        logger.info("mpin_verified_success", customer_id=customer_id)
        return True

    def reset_attempts(self, customer_id: str) -> None:
        """Reset failed attempt counter (call after successful MPIN or admin reset)."""
        _failed_attempts.pop(customer_id, None)

    @staticmethod
    def _verify_mpin(submitted: str, stored: str) -> bool:
        """
        Compare MPINs.
        Demo: direct string comparison.
        Production: would use hmac.compare_digest on hashed values.
        """
        import hmac
        # Using hmac.compare_digest even for plain text to avoid timing attacks
        return hmac.compare_digest(submitted.strip(), stored.strip())


# ── Singleton ───────────────────────────────────────────────────────────────
mpin_gate = MPINGate()
