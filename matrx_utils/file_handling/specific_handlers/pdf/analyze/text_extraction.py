"""Text-extraction detectors — native and OCR variants.

Native: PyMuPDF .get_text("text") per page. Records per-page coverage map
into PipelineContext so downstream detectors can find which pages have which
text source, and so the OCR router knows which pages to OCR.

OCR: renders the pages flagged by the OCR router and runs the host-injected
provider. Writes results under text_source="ocr" so consumers can distinguish.
Also writes per-page OCR confidence (mean of word-level confidences from
pytesseract.image_to_data) back to file_pages via the host persistence proto.
"""

from __future__ import annotations

import io
import time
from typing import Any

from ....analysis import (
    Detector,
    DetectorResult,
    DetectorSpec,
    PipelineContext,
    register_detector,
)
from ....analysis.ocr_router import select_pages_for_ocr
from ....analysis.text_sanitize import sanitize_text
from ..concurrency import run_in_cpu_executor, run_in_ocr_executor
from ..internal import load_pymupdf

NATIVE_KIND = "text_extraction_native"
OCR_KIND = "text_extraction_ocr"
DETECTOR_VERSION = "v1"


def _open_doc(ctx: PipelineContext):
    doc = ctx.cache.get("pymupdf_doc")
    if doc is not None:
        return doc
    pymupdf = load_pymupdf()
    doc = pymupdf.open(stream=ctx.bytes_in_memory, filetype="pdf")
    ctx.cache["pymupdf_doc"] = doc
    return doc


def _extract_native_text(doc) -> tuple[dict[int, dict[str, Any]], dict[int, dict[str, Any]], int]:
    """CPU-bound per-page native text pull — designed to run off the loop."""
    per_page: dict[int, dict[str, Any]] = {}
    coverage: dict[int, dict[str, Any]] = {}
    char_total = 0
    for i in range(doc.page_count):
        page = doc[i]
        # PyMuPDF can pull control characters (notably \x00 NUL bytes)
        # straight out of PDF font / encoding tables. Postgres rejects
        # those in text / jsonb columns, so we sanitize at the extraction
        # boundary — every downstream consumer can treat the text as
        # storage-safe. See ``analysis.text_sanitize`` for the policy.
        text = sanitize_text(page.get_text("text", sort=False))
        rect = page.rect
        has_text_layer = bool(text.strip())
        per_page[i + 1] = {
            "page_number": i + 1,
            "text": text,
            "chars": len(text),
            "source": "native",
        }
        coverage[i + 1] = {
            "chars": len(text),
            "has_text_layer": has_text_layer,
            "width": float(rect.width),
            "height": float(rect.height),
        }
        char_total += len(text)
    return per_page, coverage, char_total


class TextExtractionNativeDetector(Detector):
    kind = NATIVE_KIND
    version = DETECTOR_VERSION
    cost_class = "fast"

    async def run(self, ctx: PipelineContext, tier: str) -> DetectorResult:
        started = time.monotonic()
        doc = _open_doc(ctx)
        # PyMuPDF text extraction across every page is CPU-bound; run it OFF
        # the event loop. The dispatcher serializes detectors so the shared
        # ``doc`` is only touched by this one worker thread at a time.
        per_page, coverage, char_total = await run_in_cpu_executor(_extract_native_text, doc)

        # Stash for downstream detectors.
        ctx.cache["page_text_native"] = per_page
        ctx.cache["text_coverage_map"] = coverage
        text_source_map = {
            str(p): "native" if coverage[p]["has_text_layer"] else "missing" for p in coverage
        }
        ctx.cache["text_source_map"] = text_source_map

        # Pre-pick pages for OCR so the OCR detector can read it.
        ocr_pages = select_pages_for_ocr(coverage)
        ctx.cache["ocr_pages_needed"] = ocr_pages

        # Persist text_source per page so file_pages knows which pages have
        # native text vs. need OCR. The OCR detector overrides this for OCR'd
        # pages after it lands.
        persistence = ctx.cache.get("persistence")
        page_id_by_index: dict[int, str] = ctx.cache.get("page_id_by_index") or {}
        if persistence is not None:
            ocr_set = set(ocr_pages)
            for page_no in coverage.keys():
                pid = page_id_by_index.get(page_no - 1)
                if pid is None:
                    continue
                if page_no in ocr_set:
                    # Will be filled in by the OCR detector.
                    text_source = "none" if not coverage[page_no]["has_text_layer"] else "native"
                else:
                    text_source = "native"
                try:
                    await persistence.update_page_text_source(
                        page_id=pid,
                        text_source=text_source,
                        ocr_confidence=None,
                    )
                except Exception:
                    pass

        elapsed = int((time.monotonic() - started) * 1000)
        summary = {
            "page_count": doc.page_count,
            "chars_total": char_total,
            "pages_with_text_layer": sum(1 for c in coverage.values() if c["has_text_layer"]),
            "pages_needing_ocr": len(ocr_pages),
        }
        payload = {
            "pages": list(per_page.values()),
            "coverage": coverage,
            "ocr_pages_needed": ocr_pages,
        }
        return DetectorResult(
            kind=NATIVE_KIND,
            confidence_tier="n/a",
            detector_version=DETECTOR_VERSION,
            elapsed_ms=elapsed,
            summary=summary,
            payload=payload,
            text_sources=["native"],
        )


def _render_page_png(page) -> bytes:
    pix = page.get_pixmap(dpi=200, alpha=False)
    return bytes(pix.tobytes("png"))


def _ocr_confidence_for_image(image_bytes: bytes) -> float | None:
    """Mean word-level confidence (0..1) from pytesseract.image_to_data.

    Returns None when Tesseract isn't available or when the image had no
    recognisable words. Used to flag bad-scan pages in the UI.
    """
    try:
        import pytesseract
        from PIL import Image
    except Exception:
        return None
    try:
        img = Image.open(io.BytesIO(image_bytes))
        data = pytesseract.image_to_data(
            img,
            output_type=pytesseract.Output.DICT,
            config="--oem 3 --psm 6",
        )
    except Exception:
        return None
    raw = data.get("conf") or []
    # Tesseract returns -1 for tokens it skipped — filter those.
    confs: list[float] = []
    for v in raw:
        try:
            f = float(v)
        except (TypeError, ValueError):
            continue
        if f >= 0:
            confs.append(f)
    if not confs:
        return None
    return sum(confs) / len(confs) / 100.0  # Tesseract returns 0..100 → normalise to 0..1


class TextExtractionOcrDetector(Detector):
    kind = OCR_KIND
    version = DETECTOR_VERSION
    cost_class = "slow"

    async def run(self, ctx: PipelineContext, tier: str) -> DetectorResult:
        started = time.monotonic()
        ocr_pages = ctx.cache.get("ocr_pages_needed") or []
        provider = ctx.cache.get("ocr_provider")
        if not ocr_pages or provider is None:
            return DetectorResult(
                kind=OCR_KIND,
                confidence_tier="n/a",
                detector_version=DETECTOR_VERSION,
                elapsed_ms=int((time.monotonic() - started) * 1000),
                status="skipped",
                summary={"pages_ocred": 0},
                payload={"pages": []},
                text_sources=["ocr"],
            )

        doc = _open_doc(ctx)
        per_page: dict[int, dict[str, Any]] = dict(ctx.cache.get("page_text_native") or {})
        ocr_results: list[dict[str, Any]] = []
        chars_ocred = 0

        # Per-page persistence is host-injected; resolves page_id from page_index.
        persistence = ctx.cache.get("persistence")
        page_id_by_index: dict[int, str] = ctx.cache.get("page_id_by_index") or {}

        for page_no in ocr_pages:
            if page_no < 1 or page_no > doc.page_count:
                continue
            page = doc[page_no - 1]
            # Page rasterization is CPU-bound (PyMuPDF pixmap) — off the loop.
            png = await run_in_ocr_executor(_render_page_png, page)
            # OCR providers (Tesseract, cloud OCR) occasionally emit control
            # characters embedded in their output — particularly on scans
            # with non-Latin glyphs or low-quality images. Same Postgres-safety
            # boundary as the native extractor above. Each provider owns keeping
            # itself off the event loop: the in-process Tesseract provider offloads
            # to the OCR executor, a cloud provider awaits genuine async HTTP I/O.
            text = sanitize_text(await provider.ocr_page_image(png))
            # pytesseract confidence scoring is CPU-bound — off the loop.
            confidence = await run_in_ocr_executor(_ocr_confidence_for_image, png)
            ocr_results.append(
                {
                    "page_number": page_no,
                    "chars": len(text),
                    "text": text,
                    "ocr_confidence": confidence,
                }
            )
            existing = per_page.get(page_no) or {"page_number": page_no, "chars": 0, "text": ""}
            existing["text_ocr"] = text
            existing["chars_ocr"] = len(text)
            existing["ocr_confidence"] = confidence
            text_source = "mixed" if existing.get("chars") else "ocr"
            existing["source"] = text_source
            per_page[page_no] = existing
            chars_ocred += len(text)

            # Persist text_source + confidence back to file_pages — this is
            # the override-protection-aware "this page now has OCR text"
            # signal that downstream consumers read.
            if persistence is not None:
                pid = page_id_by_index.get(page_no - 1)
                if pid is not None:
                    try:
                        await persistence.update_page_text_source(
                            page_id=pid,
                            text_source=text_source,
                            ocr_confidence=confidence,
                        )
                    except Exception:
                        # Non-fatal — analysis still completes.
                        pass

        ctx.cache["page_text_combined"] = per_page
        ctx.cache["ocr_pages_completed"] = ocr_pages
        # Update text_source_map for OCR'd pages.
        tsm = ctx.cache.get("text_source_map") or {}
        for p in ocr_pages:
            key = str(p)
            tsm[key] = "ocr" if tsm.get(key) in (None, "missing") else "mixed"
        ctx.cache["text_source_map"] = tsm

        # Mean OCR confidence across pages (filter out None).
        confs = [r["ocr_confidence"] for r in ocr_results if r.get("ocr_confidence") is not None]
        mean_conf = (sum(confs) / len(confs)) if confs else None

        summary = {
            "pages_ocred": len(ocr_results),
            "chars_total_ocr": chars_ocred,
            "provider": getattr(provider, "provider_id", "unknown"),
            "mean_confidence": mean_conf,
        }
        return DetectorResult(
            kind=OCR_KIND,
            confidence_tier="n/a",
            detector_version=DETECTOR_VERSION,
            elapsed_ms=int((time.monotonic() - started) * 1000),
            summary=summary,
            payload={"pages": ocr_results},
            text_sources=["ocr"],
            page_numbers=ocr_pages,
        )


def _native_factory(spec: DetectorSpec) -> Detector:
    return TextExtractionNativeDetector()


def _ocr_factory(spec: DetectorSpec) -> Detector:
    return TextExtractionOcrDetector()


register_detector(NATIVE_KIND, _native_factory)
register_detector(OCR_KIND, _ocr_factory)


__all__ = [
    "NATIVE_KIND",
    "OCR_KIND",
    "DETECTOR_VERSION",
    "TextExtractionNativeDetector",
    "TextExtractionOcrDetector",
]
