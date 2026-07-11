"""Private helpers shared across the pdf/ submodules.

This module intentionally has no external dependencies on sibling matrx-*
packages. Optional integrations (matrx_connect.context.events.InfoPayload)
are deferred to function-local imports so the package remains usable when
matrx-connect is not installed.
"""

from __future__ import annotations

from typing import Any

from .models import PdfPageRange


def load_pymupdf() -> Any:
    """Resolve PyMuPDF as either the modern `pymupdf` import or legacy `fitz`."""
    try:
        import pymupdf

        return pymupdf
    except ImportError:
        try:
            import fitz as pymupdf

            return pymupdf
        except ImportError as exc:
            raise RuntimeError(
                "PyMuPDF is required for PDF manipulation. Install `pymupdf`."
            ) from exc


def build_info_payload(code: str, system_message: str, user_message: str) -> Any:
    """Build an info-event payload, preferring matrx-connect's typed model when present.

    Falls back to a plain dict with identical field names so emitters that
    accept dict-shaped payloads still work when matrx-connect is absent.
    """
    try:
        from matrx_connect.context.events import InfoPayload  # type: ignore

        return InfoPayload(
            code=code,
            system_message=system_message,
            user_message=user_message,
        )
    except ImportError:
        return {
            "code": code,
            "system_message": system_message,
            "user_message": user_message,
        }


def normalise_page_ranges(
    page_count: int,
    pages: list[int] | None = None,
    page_ranges: list[PdfPageRange | dict[str, Any]] | None = None,
    default_all: bool = False,
) -> list[int]:
    """Resolve a mix of single pages + ranges into a sorted-unique list of 1-based page numbers.

    Returns the union of *pages* and the inclusive integer expansion of *page_ranges*,
    de-duplicated while preserving first-occurrence order. If neither is provided and
    *default_all* is True, returns every page in the document.
    """
    selected: list[int] = []

    if pages:
        selected.extend(int(page) for page in pages)

    if page_ranges:
        for page_range in page_ranges:
            start = getattr(page_range, "start", None)
            end = getattr(page_range, "end", None)
            if start is None and isinstance(page_range, dict):
                start = page_range.get("start")
                end = page_range.get("end")
            if start is None or end is None:
                raise ValueError("Page ranges must contain start and end.")
            start_int = int(start)
            end_int = int(end)
            if start_int > end_int:
                raise ValueError("Page range start must be <= end.")
            selected.extend(range(start_int, end_int + 1))

    if not selected and default_all:
        selected = list(range(1, page_count + 1))

    normalised: list[int] = []
    seen: set[int] = set()
    for page in selected:
        if page < 1 or page > page_count:
            raise ValueError(
                f"Page {page} is outside the document range 1..{page_count}."
            )
        if page not in seen:
            normalised.append(page)
            seen.add(page)
    return normalised


def save_pymupdf_doc(doc: Any) -> bytes:
    """Serialize a PyMuPDF Document to bytes using safe optimization defaults.

    Uses ``garbage=4, deflate=True, clean=True`` — the same set required by the
    redaction algorithm to guarantee no incremental-update trailers carry
    recoverable history. Safe as the default for every page-op output.
    """
    return doc.tobytes(garbage=4, deflate=True, clean=True)


__all__ = [
    "load_pymupdf",
    "build_info_payload",
    "normalise_page_ranges",
    "save_pymupdf_doc",
]
