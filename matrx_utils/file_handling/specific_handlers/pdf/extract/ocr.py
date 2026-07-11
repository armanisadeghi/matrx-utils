"""OCR helpers used by text extraction.

Tesseract is invoked via ``pytesseract``. The default configuration
(``--oem 3 --psm 6``) treats every page as a uniform block of text, which is
the most reliable mode for legal/medical document scans.
"""

from __future__ import annotations

import io
from typing import Any

import pytesseract
from PIL import Image


_DEFAULT_TESSERACT_CONFIG = r"--oem 3 --psm 6"


def ocr_pymupdf_page(page: Any, dpi: int = 300, config: str | None = None) -> str:
    """Render a PyMuPDF page at *dpi* and run Tesseract over the result."""
    pix = page.get_pixmap(dpi=dpi, alpha=False)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    return pytesseract.image_to_string(
        img, config=config or _DEFAULT_TESSERACT_CONFIG
    )


def ocr_image_bytes(image_bytes: bytes, config: str | None = None) -> str:
    """Run Tesseract over arbitrary image bytes. Returns "" on failure."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        return pytesseract.image_to_string(
            img, config=config or _DEFAULT_TESSERACT_CONFIG
        )
    except Exception as exc:
        print(f"[matrx-pdf-ocr] image OCR failed: {exc}")
        return ""


__all__ = ["ocr_pymupdf_page", "ocr_image_bytes"]
