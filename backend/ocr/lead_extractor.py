"""
SAARTHI AI — Lead Extractor (OCR)
Extracts lead qualification signals from documents for MITRA agent.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from backend.ocr.document_parser import document_parser
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class LeadData:
    name: Optional[str] = None
    phone: Optional[str] = None
    income_mentioned: Optional[float] = None
    employer: Optional[str] = None
    qualification_score: float = 0.0


class LeadExtractor:
    """Extracts lead qualification signals from scanned documents."""

    def extract(self, image_bytes: bytes) -> LeadData:
        raw_text = document_parser.extract_text_from_image(image_bytes)
        result = LeadData()

        # Phone
        phone_match = re.search(r"\b[6-9]\d{9}\b", raw_text)
        if phone_match:
            result.phone = phone_match.group()
            result.qualification_score += 0.3

        # Income mentions
        income_match = re.search(r"(?:salary|income|CTC)[:\s]*(?:Rs\.?|₹)?\s*([\d,]+)", raw_text, re.IGNORECASE)
        if income_match:
            amount_str = income_match.group(1).replace(",", "")
            result.income_mentioned = float(amount_str)
            result.qualification_score += 0.4

        result.qualification_score = min(result.qualification_score, 1.0)
        return result


lead_extractor = LeadExtractor()
