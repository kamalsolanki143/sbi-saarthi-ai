"""
SAARTHI AI — KYC Processor (OCR)
Extracts structured KYC fields from OCR output for MITRA agent.

Supports:
  - Aadhaar card extraction
  - PAN card extraction
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from backend.ocr.document_parser import document_parser
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class KYCExtractedData:
    document_type: str  # "aadhaar" | "pan" | "unknown"
    name: Optional[str] = None
    date_of_birth: Optional[str] = None
    aadhaar_number: Optional[str] = None
    pan_number: Optional[str] = None
    address: Optional[str] = None
    gender: Optional[str] = None
    confidence: float = 0.0
    raw_text: str = ""
    errors: list[str] = field(default_factory=list)


class KYCProcessor:
    """Extracts KYC fields from document images."""

    def process_aadhaar(self, image_bytes: bytes) -> KYCExtractedData:
        raw_text = document_parser.extract_text_from_image(image_bytes, language="eng+hin")
        result = KYCExtractedData(document_type="aadhaar", raw_text=raw_text)

        # Aadhaar number: 12 digits, often formatted as XXXX XXXX XXXX
        aadhaar_match = re.search(r"\b\d{4}\s?\d{4}\s?\d{4}\b", raw_text)
        if aadhaar_match:
            result.aadhaar_number = re.sub(r"\s", "", aadhaar_match.group())
            result.confidence += 0.4

        # DOB: DD/MM/YYYY or DD-MM-YYYY
        dob_match = re.search(r"\b(\d{2})[/\-](\d{2})[/\-](\d{4})\b", raw_text)
        if dob_match:
            result.date_of_birth = f"{dob_match.group(3)}-{dob_match.group(2)}-{dob_match.group(1)}"
            result.confidence += 0.2

        # Gender
        if re.search(r"\bMALE\b", raw_text, re.IGNORECASE):
            result.gender = "M"
            result.confidence += 0.1
        elif re.search(r"\bFEMALE\b", raw_text, re.IGNORECASE):
            result.gender = "F"
            result.confidence += 0.1

        result.confidence = min(result.confidence, 1.0)
        logger.info("aadhaar_processed", confidence=result.confidence)
        return result

    def process_pan(self, image_bytes: bytes) -> KYCExtractedData:
        raw_text = document_parser.extract_text_from_image(image_bytes, language="eng")
        result = KYCExtractedData(document_type="pan", raw_text=raw_text)

        # PAN format: AAAAA9999A (5 letters, 4 digits, 1 letter)
        pan_match = re.search(r"\b[A-Z]{5}\d{4}[A-Z]\b", raw_text)
        if pan_match:
            result.pan_number = pan_match.group()
            result.confidence += 0.5

        result.confidence = min(result.confidence, 1.0)
        logger.info("pan_processed", confidence=result.confidence)
        return result


kyc_processor = KYCProcessor()
