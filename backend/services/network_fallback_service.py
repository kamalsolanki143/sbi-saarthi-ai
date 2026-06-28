"""
SAARTHI AI — Network Fallback Service
Detects network quality and determines the appropriate interaction mode.

Degradation chain (Bharat Connectivity feature):
  Voice Mode → Compressed Text Mode → Basic Interaction Mode

Used by: routes/voice.py
"""
from __future__ import annotations

from backend.utils.constants import (
    NETWORK_MODE_BASIC,
    NETWORK_MODE_COMPRESSED_TEXT,
    NETWORK_MODE_VOICE,
)
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)


class NetworkFallbackService:
    """
    Determines interaction mode based on network quality signal.
    The frontend passes a network_quality hint (0.0–1.0) with each request.
    """

    VOICE_THRESHOLD: float = 0.70      # quality >= 0.70 → voice mode
    TEXT_THRESHOLD: float = 0.30       # quality >= 0.30 → compressed text
    # quality < 0.30 → basic mode

    def get_mode(self, network_quality: float) -> str:
        """
        Returns the appropriate interaction mode string.

        Args:
            network_quality: 0.0 (no connection) to 1.0 (excellent)
        """
        if network_quality >= self.VOICE_THRESHOLD:
            mode = NETWORK_MODE_VOICE
        elif network_quality >= self.TEXT_THRESHOLD:
            mode = NETWORK_MODE_COMPRESSED_TEXT
        else:
            mode = NETWORK_MODE_BASIC

        logger.debug("network_mode_determined", quality=network_quality, mode=mode)
        return mode

    def get_mode_config(self, mode: str) -> dict:
        """Return frontend configuration for a given mode."""
        configs = {
            NETWORK_MODE_VOICE: {
                "mode": NETWORK_MODE_VOICE,
                "enable_voice": True,
                "enable_rich_text": True,
                "max_message_length": 500,
                "description": "Full voice + text experience",
            },
            NETWORK_MODE_COMPRESSED_TEXT: {
                "mode": NETWORK_MODE_COMPRESSED_TEXT,
                "enable_voice": False,
                "enable_rich_text": True,
                "max_message_length": 200,
                "description": "Text only, compressed responses",
            },
            NETWORK_MODE_BASIC: {
                "mode": NETWORK_MODE_BASIC,
                "enable_voice": False,
                "enable_rich_text": False,
                "max_message_length": 80,
                "description": "Basic text mode for low connectivity",
            },
        }
        return configs.get(mode, configs[NETWORK_MODE_BASIC])


# ── Singleton ───────────────────────────────────────────────────────────────
network_fallback_service = NetworkFallbackService()
