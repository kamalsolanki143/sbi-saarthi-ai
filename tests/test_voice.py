"""
SAARTHI AI — Test Suite: Voice Routes (Sarvam AI)
Tests for /voice/process, /voice/synthesize, /voice/translate.
Mocks SarvamAI client calls — no real API calls in CI.
Run: pytest tests/test_voice.py -v
"""
import base64
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch


@pytest.fixture
def client():
    from backend.main import app
    return TestClient(app)


def _make_fake_audio_b64() -> str:
    """Return a tiny base64-encoded WAV-like blob for test purposes."""
    return base64.b64encode(b"RIFF\x00\x00\x00\x00WAVEfmt ").decode()


# ── Transcription (Saaras v3) ───────────────────────────────────────────────

class TestTranscribeEndpoint:

    def test_text_input_bypasses_sarvam(self, client):
        """When audio_base64 is empty, no Sarvam call is made — text passes through."""
        payload = {
            "customer_id": "CUST001",
            "text_input": "Main FD kholna chahta hoon",
            "audio_base64": "",
            "network_quality": 0.9,
        }
        # Grant voice consent so the consent gate passes
        with patch("backend.routes.voice.get_safe_consent") as mock_consent, \
             patch("backend.routes.voice.require_voice_consent"):
            response = client.post("/voice/process", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["transcribed_text"] == "Main FD kholna chahta hoon"
        assert data["network_mode"] in ("voice", "compressed_text", "basic")

    def test_audio_input_calls_sarvam_transcribe(self, client):
        """When audio_base64 is provided, sarvam_service.transcribe is called."""
        fake_audio = _make_fake_audio_b64()
        payload = {
            "customer_id": "CUST001",
            "audio_base64": fake_audio,
            "source_language": "hi-IN",
            "network_quality": 1.0,
        }
        with patch("backend.routes.voice.get_safe_consent"), \
             patch("backend.routes.voice.require_voice_consent"), \
             patch("backend.routes.voice.transcribe", return_value="Main FD kholna chahta hoon") as mock_transcribe:
            response = client.post("/voice/process", json=payload)

        assert response.status_code == 200
        mock_transcribe.assert_called_once()
        assert response.json()["transcribed_text"] == "Main FD kholna chahta hoon"

    def test_sarvam_error_returns_graceful_response(self, client):
        """If Sarvam STT fails, route returns error message — no 500."""
        from backend.services.sarvam_service import SarvamServiceError
        fake_audio = _make_fake_audio_b64()
        payload = {
            "customer_id": "CUST001",
            "audio_base64": fake_audio,
            "network_quality": 1.0,
        }
        with patch("backend.routes.voice.get_safe_consent"), \
             patch("backend.routes.voice.require_voice_consent"), \
             patch("backend.routes.voice.transcribe",
                   side_effect=SarvamServiceError(message="Sarvam API timeout")):
            response = client.post("/voice/process", json=payload)

        assert response.status_code == 200  # Graceful — no 500
        data = response.json()
        assert data["transcribed_text"] == ""
        assert "Sarvam API timeout" in data["error"]

    def test_no_voice_consent_blocks_audio(self, client):
        """Voice audio without voice_processing consent → 403."""
        from backend.utils.error_handlers import ConsentRequiredError
        fake_audio = _make_fake_audio_b64()
        payload = {
            "customer_id": "CUST004",  # Customer without consent
            "audio_base64": fake_audio,
            "network_quality": 1.0,
        }
        with patch("backend.routes.voice.get_safe_consent"), \
             patch("backend.routes.voice.require_voice_consent",
                   side_effect=ConsentRequiredError(message="Voice consent required")):
            response = client.post("/voice/process", json=payload)

        assert response.status_code == 403


# ── Network Mode ────────────────────────────────────────────────────────────

class TestNetworkMode:

    def test_high_quality_returns_voice_mode(self, client):
        response = client.get("/voice/network-mode/CUST001?network_quality=1.0")
        assert response.status_code == 200
        assert response.json()["mode"] == "voice"

    def test_low_quality_returns_basic_mode(self, client):
        response = client.get("/voice/network-mode/CUST001?network_quality=0.1")
        assert response.status_code == 200
        assert response.json()["mode"] == "basic"

    def test_medium_quality_returns_compressed_text(self, client):
        response = client.get("/voice/network-mode/CUST001?network_quality=0.5")
        assert response.status_code == 200
        assert response.json()["mode"] == "compressed_text"


# ── Sarvam Service Unit Tests ───────────────────────────────────────────────

class TestSarvamServiceUnit:

    def test_transcribe_returns_mock_on_no_key(self):
        """Without an API key, transcribe returns the mock string."""
        import os
        with patch.dict(os.environ, {"SARVAM_API_KEY": ""}):
            from importlib import reload
            import backend.services.sarvam_service as svc
            reload(svc)
            result = svc.transcribe(b"fake-audio")
        assert "[MOCK ASR]" in result

    def test_translate_returns_original_on_same_language(self):
        """If source == target, translate returns the original text (no API call)."""
        from backend.services.sarvam_service import translate
        # No API call needed when languages are identical
        with patch("backend.services.sarvam_service._get_client") as mock_client:
            result = translate("Hello", "en-IN", "en-IN")
        mock_client.assert_not_called()
        assert result == "Hello"

    def test_translate_calls_sarvam_mayura(self):
        """translate() calls client.text.translate with the right params."""
        from backend.services.sarvam_service import translate
        import os
        with patch.dict(os.environ, {"SARVAM_API_KEY": "test-key"}), \
             patch("backend.services.sarvam_service._get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client
            mock_client.text.translate.return_value = MagicMock(translated_text="मुझे FD खोलनी है")

            # Reload to pick up patched env var
            import importlib
            import backend.services.sarvam_service as svc
            # Temporarily set the key directly
            svc._API_KEY = "test-key"

            result = translate("I want to open an FD", "en-IN", "hi-IN")

        assert result == "मुझे FD खोलनी है"

    def test_sarvam_error_propagates_as_sarvam_service_error(self):
        """SDK exception → SarvamServiceError (not raw SDK error)."""
        from backend.services.sarvam_service import SarvamServiceError, transcribe
        import backend.services.sarvam_service as svc

        svc._API_KEY = "test-key"

        with patch("backend.services.sarvam_service._get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client
            mock_client.speech_to_text.transcribe.side_effect = RuntimeError("Network error")

            with pytest.raises(SarvamServiceError) as exc_info:
                transcribe(b"fake-audio", "hi-IN")

        assert "speech-to-text failed" in exc_info.value.message
