"""
SAARTHI AI — Voice Routes
Voice input/output via Sarvam AI. Includes network quality → degradation mode.
Blocked by consent_validator if voice_processing consent is off.
"""
from __future__ import annotations

import base64
import io

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from backend.guardrails.consent_validator import get_safe_consent, require_voice_consent
from backend.services.sarvam_service import SarvamServiceError, synthesize, transcribe, translate
from backend.services.network_fallback_service import network_fallback_service
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()


class VoiceProcessRequest(BaseModel):
    customer_id: str
    audio_base64: str = Field(default="", description="Base64-encoded audio (empty = text mode)")
    text_input: str = Field(default="", description="Text input (fallback to audio)")
    source_language: str = Field(default="hi-IN", description="BCP-47 language code (hi-IN, en-IN, ta-IN, etc.)")
    network_quality: float = Field(default=1.0, ge=0.0, le=1.0)


@router.post("/process")
async def process_voice(request: VoiceProcessRequest):
    """
    Process voice/text input and return a response.
    Determines network mode, checks consent, calls Sarvam AI if voice provided.
    """
    # 1. Determine network degradation mode
    network_mode = network_fallback_service.get_mode(request.network_quality)
    mode_config = network_fallback_service.get_mode_config(network_mode)

    # 2. Consent check for voice
    if request.audio_base64:
        consent = get_safe_consent(request.customer_id.upper())
        require_voice_consent(consent, request.customer_id.upper())
        try:
            # Decode base64 audio → file-like object for Sarvam SDK
            audio_bytes = base64.b64decode(request.audio_base64)
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "audio.wav"  # Sarvam SDK uses file name for format hint
            text = transcribe(audio_file, language_code=request.source_language)
        except SarvamServiceError as e:
            logger.error("voice_transcribe_failed", customer_id=request.customer_id, error=e.message)
            return {
                "customer_id": request.customer_id.upper(),
                "transcribed_text": "",
                "network_mode": network_mode,
                "mode_config": mode_config,
                "source_language": request.source_language,
                "error": e.message,
                "message": "Voice transcription failed. Please try text input.",
            }
    else:
        text = request.text_input

    return {
        "customer_id": request.customer_id.upper(),
        "transcribed_text": text,
        "network_mode": network_mode,
        "mode_config": mode_config,
        "source_language": request.source_language,
        "message": "Input processed. Send to /events to trigger agent pipeline.",
    }


@router.post("/synthesize")
async def synthesize_speech(
    customer_id: str,
    text: str,
    target_language: str = "hi-IN",
    speaker: str = "anushka",
):
    """
    Convert agent response text to speech via Sarvam Bulbul v3.
    Returns base64-encoded audio for the frontend to play.
    """
    consent = get_safe_consent(customer_id.upper())
    require_voice_consent(consent, customer_id.upper())

    try:
        response = synthesize(text, target_language_code=target_language, speaker=speaker)
        return {
            "customer_id": customer_id.upper(),
            "text": text,
            "target_language": target_language,
            "speaker": speaker,
            "audio_available": response is not None,
            "message": "Speech synthesis complete." if response else "TTS skipped (no API key).",
        }
    except SarvamServiceError as e:
        logger.error("voice_synthesize_failed", customer_id=customer_id, error=e.message)
        return {"customer_id": customer_id.upper(), "error": e.message, "audio_available": False}


@router.post("/translate")
async def translate_text(
    customer_id: str,
    text: str,
    source_language: str = "en-IN",
    target_language: str = "hi-IN",
):
    """Translate text between Indian languages via Sarvam Mayura."""
    try:
        translated = translate(text, source_language_code=source_language, target_language_code=target_language)
        return {
            "customer_id": customer_id.upper(),
            "original_text": text,
            "translated_text": translated,
            "source_language": source_language,
            "target_language": target_language,
        }
    except SarvamServiceError as e:
        logger.error("voice_translate_failed", customer_id=customer_id, error=e.message)
        return {"customer_id": customer_id.upper(), "error": e.message, "translated_text": text}


@router.get("/network-mode/{customer_id}")
async def get_network_mode(
    customer_id: str,
    network_quality: float = Query(1.0, ge=0.0, le=1.0),
):
    """Return the recommended interaction mode based on network quality signal."""
    mode = network_fallback_service.get_mode(network_quality)
    config = network_fallback_service.get_mode_config(mode)
    return {"customer_id": customer_id.upper(), "network_quality": network_quality, **config}
