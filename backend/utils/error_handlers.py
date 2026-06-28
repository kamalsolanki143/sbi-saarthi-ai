"""
SAARTHI AI — Error Handlers
Standardised FastAPI exception handlers and error response formatting.
Register these in main.py with app.add_exception_handler(...).
"""
from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from backend.utils.logging_config import get_logger

logger = get_logger(__name__)


# ── Custom Exception Classes ───────────────────────────────────────────────

class SaarthiBaseError(Exception):
    """Base class for all SAARTHI AI domain errors."""
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "SAARTHI_ERROR"

    def __init__(self, message: str, detail: str | None = None):
        self.message = message
        self.detail = detail
        super().__init__(message)


class CustomerNotFoundError(SaarthiBaseError):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "CUSTOMER_NOT_FOUND"


class EventNotFoundError(SaarthiBaseError):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "EVENT_NOT_FOUND"


class RecommendationNotFoundError(SaarthiBaseError):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "RECOMMENDATION_NOT_FOUND"


class ConsentRequiredError(SaarthiBaseError):
    """Raised by consent_validator.py when a required consent is missing."""
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "CONSENT_REQUIRED"


class LowConfidenceError(SaarthiBaseError):
    """
    Raised by confidence_checker.py when intent confidence < CONFIDENCE_THRESHOLD.
    Triggers the fallback clarifying-question flow.
    """
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "LOW_CONFIDENCE"


class HumanInLoopViolationError(SaarthiBaseError):
    """
    Raised by human_in_loop.py when code attempts to skip the
    Recommendation → Preview → MPIN → Execute chain.
    This is a safety-critical error.
    """
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "HUMAN_IN_LOOP_VIOLATION"


class MPINVerificationError(SaarthiBaseError):
    """Raised when MPIN verification fails."""
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "MPIN_INVALID"


class ValidationError(SaarthiBaseError):
    """Raised when Pydantic guardrail validation fails on LLM output."""
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "VALIDATION_FAILED"


class ExternalServiceError(SaarthiBaseError):
    """Raised when Gemini / Sarvam AI / external API fails."""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "EXTERNAL_SERVICE_ERROR"


# ── Error Response Builder ─────────────────────────────────────────────────

def _error_response(
    error_code: str,
    message: str,
    status_code: int,
    detail: str | None = None,
) -> JSONResponse:
    """Build a standard SAARTHI error JSON response."""
    body = {
        "status": "error",
        "error_code": error_code,
        "message": message,
    }
    if detail:
        body["detail"] = detail
    return JSONResponse(status_code=status_code, content=body)


# ── Handler Registrations ──────────────────────────────────────────────────

def register_exception_handlers(app: FastAPI) -> None:
    """Call this in main.py to wire all exception handlers."""

    @app.exception_handler(SaarthiBaseError)
    async def saarthi_error_handler(request: Request, exc: SaarthiBaseError):
        logger.warning(
            "saarthi_domain_error",
            error_code=exc.error_code,
            message=exc.message,
            path=str(request.url),
        )
        return _error_response(exc.error_code, exc.message, exc.status_code, exc.detail)

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        logger.error(
            "unhandled_exception",
            exc_type=type(exc).__name__,
            message=str(exc),
            path=str(request.url),
        )
        return _error_response(
            "INTERNAL_ERROR",
            "An unexpected error occurred. Please try again.",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
