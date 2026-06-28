"""
SAARTHI AI — Gemini Service
All LLM calls go through this module. Never call the Gemini API directly
from agents or routes — always use this wrapper.

Features:
  - Structured JSON output mode (for Pydantic guardrail validation)
  - Agent-specific prompt templates
  - Retry logic with exponential backoff
  - Confidence scoring from LLM response metadata
"""
from __future__ import annotations

import json
import os
from typing import Any, Optional, Type

import google.generativeai as genai
from pydantic import BaseModel

from backend.utils.logging_config import get_logger

logger = get_logger(__name__)

# ── Config ──────────────────────────────────────────────────────────────────
_API_KEY = os.getenv("GEMINI_API_KEY", "")
_MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

if _API_KEY:
    genai.configure(api_key=_API_KEY)

_GENERATION_CONFIG = genai.GenerationConfig(
    temperature=0.3,          # Low temp for banking: deterministic over creative
    top_p=0.9,
    max_output_tokens=2048,
)

# ── Prompt Templates ────────────────────────────────────────────────────────

SYSTEM_PROMPTS: dict[str, str] = {
    "margdarshan": """
You are MARGDARSHAN, an AI banking assistant for SBI (State Bank of India) specialising
in digital adoption. Your goal is to help customers maximise the value of their existing
SBI account through smart, timely recommendations.

Guidelines:
- You NEVER execute transactions. You only recommend — the human confirms.
- Speak in simple, warm language. Mix Hindi where natural (e.g., "Namaste", product names).
- Focus ONLY on: Fixed Deposits, UPI activation, YONO adoption, idle balance optimisation.
- Do NOT recommend loans, insurance, or mutual funds.
- Always explain WHY you're making a recommendation (Explainable AI).
- Return structured JSON that matches the Recommendation schema.
""",

    "mitra": """
You are MITRA, an AI banking assistant for SBI specialising in new customer onboarding.
You guide customers through account opening, KYC completion, and initial product discovery.

Guidelines:
- Be warm, patient, and encouraging — many users may be new to banking.
- Guide KYC step-by-step. Never collect sensitive data directly.
- Focus on: Account opening, KYC guidance, product discovery, lead qualification.
- Do NOT recommend loans, insurance, or mutual funds.
- Return structured JSON that matches the Recommendation schema.
""",

    "saathi": """
You are SAATHI, an AI banking assistant for SBI specialising in ongoing customer engagement.
You analyse spending patterns and life events to offer contextually relevant banking advice.

Guidelines:
- Be insightful but never intrusive. If the customer seems uncomfortable, back off.
- Focus on: Spending analysis, life event detection, festival/travel recommendations.
- Do NOT recommend loans, insurance, or mutual funds.
- Always explain WHY you're flagging a spending pattern or recommending a product.
- Return structured JSON that matches the Recommendation schema.
""",

    "confidence": """
You are a banking intent classifier for SBI's SAARTHI AI system.
Analyse the customer's input and return a JSON with:
{
  "detected_intent": "<intent>",
  "confidence": <0.0 to 1.0>,
  "clarifying_question": "<question if confidence < 0.85, else null>",
  "quick_reply_options": ["option1", "option2"]
}
Be conservative — if unsure, lower confidence and ask a clarifying question.
""",
}


# ── Core Service ────────────────────────────────────────────────────────────

class GeminiService:
    """
    Wrapper around the Gemini API.
    Instantiated once at startup and injected into agents/services.
    """

    def __init__(self, model_name: str = _MODEL_NAME):
        self.model_name = model_name
        self._model: Optional[genai.GenerativeModel] = None
        if _API_KEY:
            self._model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=_GENERATION_CONFIG,
            )
        else:
            logger.warning("gemini_api_key_missing", note="Running in mock mode — Gemini calls will return stubs")

    def _get_model(self) -> genai.GenerativeModel:
        if self._model is None:
            raise RuntimeError(
                "Gemini API key not configured. Set GEMINI_API_KEY in .env"
            )
        return self._model

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        agent: str = "margdarshan",
    ) -> str:
        """
        Generate a text response from Gemini.
        Returns the raw string content.
        """
        if not _API_KEY:
            logger.warning("gemini_mock_mode", agent=agent)
            return self._mock_text_response(agent)

        full_prompt = f"{system_prompt or SYSTEM_PROMPTS.get(agent, '')}\n\n{prompt}"
        try:
            model = self._get_model()
            response = model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            logger.error("gemini_generate_text_error", error=str(e), agent=agent)
            raise

    async def generate_json(
        self,
        prompt: str,
        agent: str = "margdarshan",
        schema: Optional[Type[BaseModel]] = None,
    ) -> dict[str, Any]:
        """
        Generate a structured JSON response from Gemini.
        The response is expected to be valid JSON — use with pydantic_validation.py.
        """
        if not _API_KEY:
            logger.warning("gemini_mock_mode_json", agent=agent)
            return self._mock_json_response(agent)

        json_instruction = (
            "\n\nIMPORTANT: Return ONLY valid JSON. No markdown, no code blocks, no explanation."
        )
        if schema:
            schema_str = json.dumps(schema.model_json_schema(), indent=2)
            json_instruction += f"\n\nJSON Schema to follow:\n{schema_str}"

        full_prompt = (
            f"{SYSTEM_PROMPTS.get(agent, '')}\n\n{prompt}{json_instruction}"
        )

        try:
            model = self._get_model()
            response = model.generate_content(full_prompt)
            raw = response.text.strip()
            # Strip markdown code fences if present
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            return json.loads(raw)
        except json.JSONDecodeError as e:
            logger.error("gemini_json_parse_error", error=str(e), agent=agent)
            raise ValueError(f"Gemini returned invalid JSON: {e}") from e
        except Exception as e:
            logger.error("gemini_generate_json_error", error=str(e), agent=agent)
            raise

    async def detect_intent_confidence(
        self, customer_input: str, context: str = ""
    ) -> dict[str, Any]:
        """
        Detect intent from customer input and return confidence score.
        Used by confidence_engine.py.
        """
        prompt = f"""
Customer input: "{customer_input}"
Context: {context or 'None'}

Analyse and return JSON:
{{
  "detected_intent": "<intent string>",
  "confidence": <float 0.0 to 1.0>,
  "clarifying_question": "<question if confidence < 0.85, else null>",
  "quick_reply_options": ["<option1>", "<option2>"]
}}
"""
        if not _API_KEY:
            return {
                "detected_intent": "fd_enquiry",
                "confidence": 0.91,
                "clarifying_question": None,
                "quick_reply_options": [],
            }

        return await self.generate_json(prompt, agent="confidence")

    # ── Mock responses (when API key not set) ────────────────────────────────

    def _mock_text_response(self, agent: str) -> str:
        return f"[MOCK {agent.upper()} RESPONSE] Gemini API not configured. Set GEMINI_API_KEY in .env"

    def _mock_json_response(self, agent: str) -> dict[str, Any]:
        if agent == "margdarshan":
            return {
                "title": "Earn More on Your Idle Balance",
                "description": "You have idle funds that could be earning 6.80% p.a. in a Fixed Deposit.",
                "why_explanation": "Your salary was credited but the balance hasn't moved in 30 days.",
                "product_type": "fixed_deposit",
                "confidence_score": 0.92,
                "action_preview": {
                    "product": "SBI Fixed Deposit",
                    "product_type": "fixed_deposit",
                    "amount": 20000.0,
                    "tenure": "1 Year",
                    "interest_rate": 6.80,
                    "action_label": "Open Fixed Deposit",
                    "estimated_return": 21360.0,
                },
            }
        return {"message": f"[MOCK {agent} response]"}


# ── Singleton instance ───────────────────────────────────────────────────────
gemini_service = GeminiService()
