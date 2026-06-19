"""
SAARTHI AI — Gemini LLM Service
================================

Provides a production-grade wrapper around Google's Gemini generative AI
SDK.  All other engines (confidence, persona, event) route their LLM
calls through this service so that retry logic, token budgets, safety
settings, and structured-output parsing are centralised.

Key responsibilities
────────────────────
• Async text generation with configurable temperature / top-p / top-k.
• Structured JSON extraction via constrained decoding prompts.
• Automatic retry with exponential back-off for transient API errors.
• Network-mode–adaptive prompt compression (low-bandwidth mode).
• Token-budget guardrails to prevent run-away costs.
• Comprehensive structured logging for observability.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from typing import Any

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from backend.models.state import NetworkMode

# ─── Structured Logger ──────────────────────────────────────────────────────

logger = logging.getLogger("saarthi.services.gemini")


# ─── Configuration ──────────────────────────────────────────────────────────

_DEFAULT_MODEL: str = "gemini-2.0-flash"
_MAX_RETRIES: int = 3
_INITIAL_BACKOFF_SECONDS: float = 1.0
_BACKOFF_MULTIPLIER: float = 2.0
_MAX_OUTPUT_TOKENS: int = 4096
_LOW_BANDWIDTH_MAX_TOKENS: int = 512
_DEFAULT_TEMPERATURE: float = 0.3
_DEFAULT_TOP_P: float = 0.9
_DEFAULT_TOP_K: int = 40


# ─── Exceptions ─────────────────────────────────────────────────────────────


class GeminiServiceError(Exception):
    """Raised when the Gemini API call fails after all retry attempts."""

    def __init__(self, message: str, *, cause: Exception | None = None) -> None:
        super().__init__(message)
        self.cause = cause


class GeminiParsingError(GeminiServiceError):
    """Raised when a structured-output response cannot be parsed as JSON."""


# ─── Service ────────────────────────────────────────────────────────────────


class GeminiService:
    """
    Centralised gateway to the Gemini generative-AI API.

    Instantiate once at application startup and inject into engines via
    dependency injection (or a service-locator if preferred).

    Parameters
    ----------
    api_key : str | None
        Gemini API key.  Falls back to the ``GEMINI_API_KEY`` env-var.
    model_name : str
        Model identifier, e.g. ``gemini-2.0-flash``.
    """

    # ── Construction ────────────────────────────────────────────────────

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = _DEFAULT_MODEL,
    ) -> None:
        resolved_key: str = api_key or os.getenv("GEMINI_API_KEY", "")
        if not resolved_key:
            raise GeminiServiceError(
                "Gemini API key is required.  Set GEMINI_API_KEY or pass "
                "api_key= to the constructor."
            )

        genai.configure(api_key=resolved_key)

        self._model_name: str = model_name
        self._model: genai.GenerativeModel = genai.GenerativeModel(
            model_name=model_name,
        )

        logger.info(
            "GeminiService initialised",
            extra={"model": model_name},
        )

    # ── Public API ──────────────────────────────────────────────────────

    async def generate_text(
        self,
        prompt: str,
        *,
        system_instruction: str = "",
        temperature: float = _DEFAULT_TEMPERATURE,
        top_p: float = _DEFAULT_TOP_P,
        top_k: int = _DEFAULT_TOP_K,
        max_output_tokens: int = _MAX_OUTPUT_TOKENS,
        network_mode: NetworkMode = NetworkMode.TEXT_MODE,
    ) -> str:
        """
        Generate free-form text from a prompt.

        Parameters
        ----------
        prompt : str
            User-facing (or engine-facing) prompt text.
        system_instruction : str
            Optional system-level instruction prepended to the prompt.
        temperature : float
            Sampling temperature (0.0 – 2.0).
        top_p : float
            Nucleus sampling threshold.
        top_k : int
            Top-k sampling parameter.
        max_output_tokens : int
            Hard ceiling on generated tokens.
        network_mode : NetworkMode
            When ``LOW_BANDWIDTH_MODE``, the token budget is compressed and
            the prompt is augmented with brevity instructions.

        Returns
        -------
        str
            The generated text, stripped of leading/trailing whitespace.

        Raises
        ------
        GeminiServiceError
            After exhausting all retry attempts.
        """
        effective_tokens, effective_prompt = self._adapt_for_network(
            prompt=prompt,
            max_tokens=max_output_tokens,
            network_mode=network_mode,
        )

        full_prompt = self._build_full_prompt(
            system_instruction=system_instruction,
            user_prompt=effective_prompt,
        )

        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            max_output_tokens=effective_tokens,
        )

        response_text: str = await self._call_with_retry(
            full_prompt=full_prompt,
            generation_config=generation_config,
        )

        return response_text

    async def generate_structured(
        self,
        prompt: str,
        *,
        system_instruction: str = "",
        temperature: float = 0.1,
        max_output_tokens: int = _MAX_OUTPUT_TOKENS,
        network_mode: NetworkMode = NetworkMode.TEXT_MODE,
    ) -> dict[str, Any]:
        """
        Generate a **JSON object** by constraining the model output.

        The prompt MUST instruct the model to reply in valid JSON.  This
        method post-processes the raw text, strips markdown fences, and
        parses the result.

        Returns
        -------
        dict[str, Any]
            Parsed JSON dictionary.

        Raises
        ------
        GeminiParsingError
            If the model output is not valid JSON after cleanup.
        """
        json_system = (
            f"{system_instruction}\n\n"
            "CRITICAL: You MUST respond with ONLY a valid JSON object.  "
            "Do NOT wrap the JSON in markdown code fences.  "
            "Do NOT include any text before or after the JSON."
        )

        raw: str = await self.generate_text(
            prompt=prompt,
            system_instruction=json_system,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            network_mode=network_mode,
        )

        return self._parse_json_response(raw)

    async def generate_with_history(
        self,
        conversation_history: list[dict[str, str]],
        current_query: str,
        *,
        system_instruction: str = "",
        temperature: float = _DEFAULT_TEMPERATURE,
        max_output_tokens: int = _MAX_OUTPUT_TOKENS,
        network_mode: NetworkMode = NetworkMode.TEXT_MODE,
    ) -> str:
        """
        Generate a response within a multi-turn conversation context.

        Parameters
        ----------
        conversation_history : list[dict[str, str]]
            Prior turns as ``{"role": "user"|"model", "parts": "..."}``
            dictionaries.
        current_query : str
            The latest user message.

        Returns
        -------
        str
            Generated assistant reply.
        """
        history_block: str = self._format_history(conversation_history)

        composite_prompt = (
            f"{history_block}\n\nCurrent query: {current_query}"
        )

        return await self.generate_text(
            prompt=composite_prompt,
            system_instruction=system_instruction,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            network_mode=network_mode,
        )

    # ── Internals ───────────────────────────────────────────────────────

    async def _call_with_retry(
        self,
        full_prompt: str,
        generation_config: genai.types.GenerationConfig,
    ) -> str:
        """Execute the API call with exponential back-off retries."""
        last_exception: Exception | None = None
        backoff: float = _INITIAL_BACKOFF_SECONDS

        for attempt in range(1, _MAX_RETRIES + 1):
            start = time.monotonic()
            try:
                response = await asyncio.to_thread(
                    self._model.generate_content,
                    full_prompt,
                    generation_config=generation_config,
                )

                elapsed_ms = (time.monotonic() - start) * 1000

                if not response.text:
                    raise GeminiServiceError(
                        "Gemini returned an empty response (possible safety block)."
                    )

                logger.info(
                    "Gemini generation succeeded",
                    extra={
                        "model": self._model_name,
                        "attempt": attempt,
                        "elapsed_ms": round(elapsed_ms, 2),
                        "output_length": len(response.text),
                    },
                )
                return response.text.strip()

            except (
                google_exceptions.ResourceExhausted,
                google_exceptions.ServiceUnavailable,
                google_exceptions.DeadlineExceeded,
                google_exceptions.InternalServerError,
            ) as exc:
                last_exception = exc
                logger.warning(
                    "Gemini transient error — retrying",
                    extra={
                        "attempt": attempt,
                        "backoff_s": backoff,
                        "error": str(exc),
                    },
                )
                await asyncio.sleep(backoff)
                backoff *= _BACKOFF_MULTIPLIER

            except google_exceptions.InvalidArgument as exc:
                logger.error(
                    "Gemini invalid argument (non-retryable)",
                    extra={"error": str(exc)},
                )
                raise GeminiServiceError(
                    f"Invalid API request: {exc}", cause=exc
                ) from exc

            except Exception as exc:
                logger.error(
                    "Gemini unexpected error",
                    extra={"error": str(exc), "type": type(exc).__name__},
                )
                raise GeminiServiceError(
                    f"Unexpected error during Gemini call: {exc}", cause=exc
                ) from exc

        raise GeminiServiceError(
            f"Gemini API call failed after {_MAX_RETRIES} retries",
            cause=last_exception,
        )

    @staticmethod
    def _build_full_prompt(system_instruction: str, user_prompt: str) -> str:
        """Combine system instruction and user prompt into a single string."""
        if system_instruction:
            return f"{system_instruction}\n\n{user_prompt}"
        return user_prompt

    @staticmethod
    def _adapt_for_network(
        prompt: str,
        max_tokens: int,
        network_mode: NetworkMode,
    ) -> tuple[int, str]:
        """
        Adjust token budget and prompt wording for constrained networks.

        In LOW_BANDWIDTH_MODE the model is instructed to be maximally
        concise and the token ceiling is clamped.
        """
        if network_mode == NetworkMode.LOW_BANDWIDTH_MODE:
            effective_tokens = min(max_tokens, _LOW_BANDWIDTH_MAX_TOKENS)
            augmented_prompt = (
                "[LOW BANDWIDTH — keep response under 100 words, "
                "use short sentences, avoid lists longer than 3 items.]\n\n"
                f"{prompt}"
            )
            return effective_tokens, augmented_prompt

        if network_mode == NetworkMode.VOICE_MODE:
            augmented_prompt = (
                "[VOICE MODE — respond conversationally, avoid technical "
                "jargon, use simple language suitable for text-to-speech.]\n\n"
                f"{prompt}"
            )
            return max_tokens, augmented_prompt

        return max_tokens, prompt

    @staticmethod
    def _parse_json_response(raw: str) -> dict[str, Any]:
        """
        Extract a JSON dict from the model's raw text output.

        Handles common issues:
        • Markdown ```json fences.
        • Leading/trailing whitespace.
        • Partial wrapping text before/after the JSON block.
        """
        cleaned: str = raw.strip()

        # Strip markdown code fences
        if cleaned.startswith("```"):
            first_newline = cleaned.index("\n") if "\n" in cleaned else 3
            cleaned = cleaned[first_newline + 1 :]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        cleaned = cleaned.strip()

        # Attempt direct parse
        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict):
                return parsed
            raise GeminiParsingError(
                f"Expected JSON object, got {type(parsed).__name__}"
            )
        except json.JSONDecodeError:
            pass

        # Fallback: find first { … } block
        brace_start = cleaned.find("{")
        brace_end = cleaned.rfind("}")
        if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
            candidate = cleaned[brace_start : brace_end + 1]
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, dict):
                    logger.debug(
                        "Recovered JSON from embedded block",
                        extra={"raw_length": len(raw)},
                    )
                    return parsed
            except json.JSONDecodeError:
                pass

        raise GeminiParsingError(
            f"Unable to parse Gemini response as JSON.  "
            f"Raw output (first 500 chars): {raw[:500]}"
        )

    @staticmethod
    def _format_history(history: list[dict[str, str]]) -> str:
        """Format conversation history into a readable prompt block."""
        if not history:
            return ""

        lines: list[str] = ["Previous conversation:"]
        for turn in history[-10:]:  # cap to last 10 turns
            role = turn.get("role", "unknown").upper()
            content = turn.get("parts", turn.get("content", ""))
            lines.append(f"  {role}: {content}")

        return "\n".join(lines)

    # ── Diagnostics ─────────────────────────────────────────────────────

    @property
    def model_name(self) -> str:
        """Return the active model identifier."""
        return self._model_name

    def health_check(self) -> dict[str, Any]:
        """
        Non-blocking health probe.

        Returns a dict suitable for inclusion in a ``/healthz`` endpoint.
        """
        return {
            "service": "gemini",
            "status": "ok",
            "model": self._model_name,
        }
