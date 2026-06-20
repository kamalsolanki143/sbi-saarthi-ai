"""
SAARTHI AI — Pydantic Validation (Guardrail)
Generic utility for validating raw LLM JSON output against a Pydantic schema.

Every LLM response MUST pass through this before any downstream action.
Used by: all agents, action_validator.py, confidence_checker.py
"""
from __future__ import annotations

import json
from typing import Any, Type, TypeVar

from pydantic import BaseModel, ValidationError

from backend.utils.error_handlers import ValidationError as SaarthiValidationError
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


def validate_llm_output(
    raw_output: str | dict[str, Any],
    schema: Type[T],
    context: str = "",
) -> T:
    """
    Validate raw LLM output (string or dict) against a Pydantic schema.

    Args:
        raw_output: Raw string from Gemini or a pre-parsed dict.
        schema: Pydantic model class to validate against.
        context: Description for logging (e.g., 'margdarshan FD recommendation').

    Returns:
        Validated Pydantic model instance.

    Raises:
        SaarthiValidationError: If validation fails — the flow MUST NOT continue.
    """
    # 1. Parse string to dict if needed
    if isinstance(raw_output, str):
        raw_output = _parse_json_string(raw_output, context)

    # 2. Validate against schema
    try:
        validated = schema.model_validate(raw_output)
        logger.info(
            "llm_output_validated",
            schema=schema.__name__,
            context=context,
        )
        return validated
    except ValidationError as e:
        error_summary = _format_validation_errors(e)
        logger.error(
            "llm_output_validation_failed",
            schema=schema.__name__,
            context=context,
            errors=error_summary,
        )
        raise SaarthiValidationError(
            message=f"LLM output failed validation for {schema.__name__}",
            detail=error_summary,
        ) from e


def validate_dict_against_schema(
    data: dict[str, Any],
    schema: Type[T],
    context: str = "",
) -> T:
    """Validate a dict (not from LLM, but from internal code) against a schema."""
    return validate_llm_output(data, schema, context)


def _parse_json_string(raw: str, context: str) -> dict[str, Any]:
    """Parse a JSON string, stripping markdown fences if present."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # Remove first and last ``` lines
        cleaned = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error("json_parse_failed", context=context, error=str(e), raw_preview=raw[:100])
        raise SaarthiValidationError(
            message="LLM returned invalid JSON",
            detail=f"Parse error: {e}. Raw preview: {raw[:200]}",
        ) from e


def _format_validation_errors(e: ValidationError) -> str:
    """Format Pydantic validation errors into a readable string."""
    errors = []
    for error in e.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        msg = error["msg"]
        errors.append(f"  [{field}]: {msg}")
    return "\n".join(errors)


def is_valid(data: dict[str, Any], schema: Type[T]) -> bool:
    """Quick boolean check — does data match schema? No exception raised."""
    try:
        schema.model_validate(data)
        return True
    except ValidationError:
        return False
