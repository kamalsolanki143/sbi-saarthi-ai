"""
SAARTHI AI — Biometric Gate
Stub biometric verification for demo scope.

In production, this would integrate with:
  - Device biometric SDK (face/fingerprint)
  - SBI's biometric authentication service
  - UIDAI Aadhaar biometric verification

For the hackathon demo, this always returns True (simulated success)
but is structured as a real gate so the architecture is production-ready.

Used by: routes/auth.py, human_in_loop.py (as an alternative to MPIN)
"""
from __future__ import annotations

from backend.utils.logging_config import get_logger

logger = get_logger(__name__)


class BiometricGate:
    """
    Biometric verification gate.
    Demo: always passes. Structured for real integration.
    """

    def verify(
        self,
        customer_id: str,
        biometric_token: str,
        biometric_type: str = "fingerprint",
    ) -> bool:
        """
        Verify biometric authentication.

        Args:
            customer_id: Customer identifier.
            biometric_token: Biometric verification token from the device SDK.
            biometric_type: "fingerprint" | "face" | "iris"

        Returns:
            True if biometric is verified (demo: always True).
        """
        # DEMO SCOPE: Simulate biometric verification
        # In production: call SBI biometric service / UIDAI API
        logger.info(
            "biometric_verification_simulated",
            customer_id=customer_id,
            biometric_type=biometric_type,
            note="Demo mode — real biometric integration required for production",
        )
        return True


# ── Singleton ───────────────────────────────────────────────────────────────
biometric_gate = BiometricGate()
