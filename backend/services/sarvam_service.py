"""
SAARTHI AI — Sarvam AI Service
Indian language voice support via the Sarvam AI SDK (sarvamai).

Models used:
  - Speech-to-Text:  Saaras v3
  - Text-to-Speech:  Bulbul v3
  - Translation:     Mayura

Previously: Sarvam AI replaced the prior voice service (removed).
Used by:  backend/routes/voice.py

Consent gate: voice_processing consent MUST be checked before calling this service.
              That check lives in consent_validator.py → called from routes/voice.py.
"""
from __future__ import annotations

import os
from typing import Any, Optional

from backend.utils.error_handlers import ExternalServiceError
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)

_API_KEY = os.getenv("SARVAM_API_KEY", "")


# ── Custom exception ────────────────────────────────────────────────────────

class SarvamServiceError(ExternalServiceError):
    """Raised when a Sarvam AI API call fails."""
    error_code = "SARVAM_SERVICE_ERROR"


# ── Client init ─────────────────────────────────────────────────────────────

def _get_client():
    """Lazily instantiate SarvamAI client so import errors surface cleanly."""
    try:
        from sarvamai import SarvamAI
        return SarvamAI(api_subscription_key=_API_KEY)
    except ImportError as e:
        raise SarvamServiceError(
            message="sarvamai package not installed",
            detail="Run: pip install sarvamai",
        ) from e


# ── Public API (same signatures expected by routes/voice.py) ───────────────

def transcribe(audio_file: Any, language_code: Optional[str] = None) -> str:
    """
    Speech-to-Text via Sarvam Saaras v3.

    Args:
        audio_file: File-like object or path accepted by the Sarvam SDK.
        language_code: Optional ISO 639-1 code (e.g. "hi-IN").
                       None → Sarvam auto-detects language.

    Returns:
        Transcribed text string.

    Raises:
        SarvamServiceError: On any API or SDK failure.
    """
    if not _API_KEY:
        logger.warning("sarvam_no_api_key", note="Returning mock transcript")
        return "[MOCK ASR] Sarvam API key not configured."

    try:
        client = _get_client()
        response = client.speech_to_text.transcribe(
            audio_file,
            model="saaras:v3",
            language_code=language_code,
        )
        transcript = response.transcript
        logger.info("sarvam_transcribe_ok", chars=len(transcript or ""))
        return transcript or ""
    except SarvamServiceError:
        raise
    except Exception as e:
        logger.error("sarvam_transcribe_error", error=str(e))
        raise SarvamServiceError(
            message="Sarvam speech-to-text failed",
            detail=str(e),
        ) from e


def synthesize(
    text: str,
    target_language_code: str = "hi-IN",
    speaker: str = "anushka",
) -> Any:
    """
    Text-to-Speech via Sarvam Bulbul v3.

    Args:
        text: Input text to convert to speech.
        target_language_code: BCP-47 language tag (e.g. "hi-IN", "ta-IN").
        speaker: Voice ID supported by Bulbul (default: "anushka").

    Returns:
        Sarvam audio response object (caller can use sarvamai.play.save() on it).

    Raises:
        SarvamServiceError: On any API or SDK failure.
    """
    if not _API_KEY:
        logger.warning("sarvam_no_api_key", note="TTS skipped — no API key")
        return None

    try:
        client = _get_client()
        response = client.text_to_speech.convert(
            text=text,
            target_language_code=target_language_code,
            model="bulbul:v3",
            speaker=speaker,
        )
        logger.info("sarvam_synthesize_ok", language=target_language_code, speaker=speaker)
        return response
    except SarvamServiceError:
        raise
    except Exception as e:
        logger.error("sarvam_synthesize_error", error=str(e))
        raise SarvamServiceError(
            message="Sarvam text-to-speech failed",
            detail=str(e),
        ) from e


def translate(
    text: str,
    source_language_code: str,
    target_language_code: str,
) -> str:
    """
    Translation via Sarvam Mayura model.

    Args:
        text: Text to translate.
        source_language_code: BCP-47 source language (e.g. "en-IN").
        target_language_code: BCP-47 target language (e.g. "hi-IN").

    Returns:
        Translated text string.

    Raises:
        SarvamServiceError: On any API or SDK failure.
    """
    if not _API_KEY:
        logger.warning("sarvam_no_api_key", note="Translation skipped — no API key")
        return text  # Return original on no-key graceful degradation

    if source_language_code == target_language_code:
        return text

    try:
        client = _get_client()
        response = client.text.translate(
            input=text,
            source_language_code=source_language_code,
            target_language_code=target_language_code,
        )
        translated = response.translated_text
        logger.info(
            "sarvam_translate_ok",
            source=source_language_code,
            target=target_language_code,
            chars_in=len(text),
            chars_out=len(translated or ""),
        )
        return translated or text
    except SarvamServiceError:
        raise
    except Exception as e:
        logger.error("sarvam_translate_error", error=str(e))
        raise SarvamServiceError(
            message="Sarvam translation failed",
            detail=str(e),
        ) from e
