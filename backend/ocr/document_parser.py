"""
SAARTHI AI — Document Parser (OCR)
Generic OCR extraction utility using Tesseract.
Used by kyc_processor.py and lead_extractor.py.
"""
from __future__ import annotations

import base64
import io
import os
from pathlib import Path
from typing import Optional

from backend.utils.logging_config import get_logger

logger = get_logger(__name__)

# Tesseract path (configurable via env)
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "/usr/bin/tesseract")


class DocumentParser:
    """Generic OCR document parser using Pytesseract + PIL."""

    def extract_text_from_image(
        self,
        image_bytes: bytes,
        language: str = "eng+hin",
    ) -> str:
        """
        Extract text from an image using Tesseract OCR.

        Args:
            image_bytes: Raw image bytes (JPEG/PNG/PDF page).
            language: Tesseract language string (e.g. 'eng+hin' for English + Hindi).

        Returns:
            Extracted text string.
        """
        try:
            import pytesseract
            from PIL import Image

            pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
            image = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(image, lang=language)
            logger.info("ocr_extraction_complete", chars=len(text))
            return text.strip()

        except ImportError:
            logger.warning("pytesseract_not_installed", note="OCR features unavailable")
            return ""
        except Exception as e:
            logger.error("ocr_extraction_error", error=str(e))
            return ""

    def extract_text_from_base64(
        self, base64_image: str, language: str = "eng+hin"
    ) -> str:
        """Extract text from a base64-encoded image string."""
        image_bytes = base64.b64decode(base64_image)
        return self.extract_text_from_image(image_bytes, language)

    def extract_text_from_pdf(self, pdf_bytes: bytes, language: str = "eng+hin") -> str:
        """
        Extract text from a PDF by converting pages to images first.
        """
        try:
            from pdf2image import convert_from_bytes
            pages = convert_from_bytes(pdf_bytes)
            all_text = []
            for i, page in enumerate(pages):
                import io
                img_bytes = io.BytesIO()
                page.save(img_bytes, format="PNG")
                text = self.extract_text_from_image(img_bytes.getvalue(), language)
                all_text.append(text)
            return "\n\n--- Page Break ---\n\n".join(all_text)
        except ImportError:
            logger.warning("pdf2image_not_installed")
            return ""
        except Exception as e:
            logger.error("pdf_extraction_error", error=str(e))
            return ""


document_parser = DocumentParser()
