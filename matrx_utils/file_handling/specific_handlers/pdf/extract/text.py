"""Text extraction from PDFs — native, OCR-fallback, and block/word maps.

All functions are sync. Their ``_async`` variants run on the OCR executor when
OCR is enabled, otherwise on the CPU executor.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Callable
from typing import Any

import pypdfium2 as pdfium
import pytesseract

from ..concurrency import run_in_cpu_executor, run_in_ocr_executor
from ..internal import load_pymupdf
from ..models import PdfExtractStart, PdfPageText, PdfTextBlock, PdfTextWord
from ..tmp import pdf_temp_file
from .ocr import ocr_image_bytes, ocr_pymupdf_page


def _pymupdf_text_blocks(page: Any) -> list[PdfTextBlock]:
    blocks: list[PdfTextBlock] = []
    for block in page.get_text("blocks", sort=False):
        x0, y0, x1, y1, text, block_number, block_type = block[:7]
        blocks.append(
            PdfTextBlock(
                block_number=int(block_number),
                block_type=int(block_type),
                x0=float(x0),
                y0=float(y0),
                x1=float(x1),
                y1=float(y1),
                text=str(text),
            )
        )
    return blocks


def _pymupdf_text_words(page: Any) -> list[PdfTextWord]:
    words: list[PdfTextWord] = []
    for word in page.get_text("words", sort=False):
        x0, y0, x1, y1, text, block_number, line_number, word_number = word[:8]
        words.append(
            PdfTextWord(
                word=str(text),
                x0=float(x0),
                y0=float(y0),
                x1=float(x1),
                y1=float(y1),
                block_number=int(block_number),
                line_number=int(line_number),
                word_number=int(word_number),
            )
        )
    return words


def extract_text_pages(
    path: str,
    force_ocr: bool = False,
    use_ocr_threshold: int = 100,
    include_blocks: bool = False,
    include_words: bool = False,
    on_open: Callable[[int], None] | None = None,
    on_page: Callable[[PdfPageText], None] | None = None,
) -> list[PdfPageText]:
    """Extract per-page text + optional bbox metadata from a PDF on disk.

    Uses native ``get_text("text")`` first; falls back to Tesseract OCR for any
    page whose extracted text is shorter than *use_ocr_threshold* characters
    (or all pages if *force_ocr* is True).

    ``on_open`` / ``on_page`` are optional sync progress hooks called from the
    extraction loop (``on_open`` with the page count the moment the document
    opens, ``on_page`` with each page as it finishes). They exist so callers
    can stream progress in real time — see ``extract_text_pages_stream``.
    """
    pymupdf = load_pymupdf()
    pages: list[PdfPageText] = []
    with pymupdf.open(path) as doc:
        if on_open is not None:
            on_open(doc.page_count)
        for page_index, page in enumerate(doc):
            text = ""
            method = "native"
            if not force_ocr:
                text = page.get_text("text", sort=False)

            if force_ocr or (
                use_ocr_threshold > 0 and len(text.strip()) < use_ocr_threshold
            ):
                text = ocr_pymupdf_page(page)
                method = "ocr"

            rect = page.rect
            page_text = PdfPageText(
                page_number=page_index + 1,
                page_index=page_index,
                width=float(rect.width),
                height=float(rect.height),
                rotation=int(page.rotation),
                text=text,
                extraction_method=method,
                char_count=len(text),
                source_path=path,
                blocks=_pymupdf_text_blocks(page) if include_blocks else None,
                words=_pymupdf_text_words(page) if include_words else None,
            )
            pages.append(page_text)
            if on_page is not None:
                on_page(page_text)
    return pages


async def extract_text_pages_async(
    path: str,
    force_ocr: bool = False,
    use_ocr_threshold: int = 100,
    include_blocks: bool = False,
    include_words: bool = False,
) -> list[PdfPageText]:
    executor = run_in_ocr_executor if force_ocr else run_in_cpu_executor
    return await executor(
        extract_text_pages,
        path,
        force_ocr,
        use_ocr_threshold,
        include_blocks,
        include_words,
    )


async def extract_text_pages_stream(
    path: str,
    force_ocr: bool = False,
    use_ocr_threshold: int = 100,
    include_blocks: bool = False,
    include_words: bool = False,
) -> AsyncIterator[PdfExtractStart | PdfPageText]:
    """Stream extraction as it happens: yields one ``PdfExtractStart`` (page
    count) the moment the document opens, then each ``PdfPageText`` as its
    page finishes (native or OCR).

    Runs the whole sync loop on ONE executor worker (same thread-safety
    discipline as ``extract_text_pages_async`` — the Document never leaves
    its thread); pages cross back to the event loop via a queue. An
    extraction error is re-raised here after all already-extracted pages
    have been yielded.
    """
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue[PdfExtractStart | PdfPageText | None] = asyncio.Queue()

    def _on_open(total_pages: int) -> None:
        loop.call_soon_threadsafe(queue.put_nowait, PdfExtractStart(total_pages=total_pages))

    def _on_page(page: PdfPageText) -> None:
        loop.call_soon_threadsafe(queue.put_nowait, page)

    executor = run_in_ocr_executor if force_ocr else run_in_cpu_executor

    async def _run() -> None:
        try:
            await executor(
                extract_text_pages,
                path,
                force_ocr,
                use_ocr_threshold,
                include_blocks,
                include_words,
                _on_open,
                _on_page,
            )
        finally:
            queue.put_nowait(None)  # sentinel — runs on the event loop already

    worker = asyncio.ensure_future(_run())
    try:
        while True:
            item = await queue.get()
            if item is None:
                break
            yield item
    finally:
        # Propagate an extraction failure (worker is guaranteed settled once
        # the sentinel arrived; on generator abandonment this awaits the tail).
        await worker


def extract_text_pages_from_bytes(
    pdf_bytes: bytes,
    force_ocr: bool = False,
    use_ocr_threshold: int = 100,
    include_blocks: bool = False,
    include_words: bool = False,
) -> list[PdfPageText]:
    with pdf_temp_file(pdf_bytes) as tmp_path:
        return extract_text_pages(
            str(tmp_path),
            force_ocr=force_ocr,
            use_ocr_threshold=use_ocr_threshold,
            include_blocks=include_blocks,
            include_words=include_words,
        )


async def extract_text_pages_from_bytes_async(
    pdf_bytes: bytes,
    force_ocr: bool = False,
    use_ocr_threshold: int = 100,
    include_blocks: bool = False,
    include_words: bool = False,
) -> list[PdfPageText]:
    executor = run_in_ocr_executor if force_ocr else run_in_cpu_executor
    return await executor(
        extract_text_pages_from_bytes,
        pdf_bytes,
        force_ocr,
        use_ocr_threshold,
        include_blocks,
        include_words,
    )


def format_page_text(
    pages: list[PdfPageText],
    include_page_markers: bool = False,
    document_label: str | None = None,
) -> str:
    """Stitch per-page text into a single string, optionally with boundary markers."""
    parts: list[str] = []
    for page in pages:
        if include_page_markers:
            label = document_label or page.source_path or "document"
            parts.append(
                f"--- PDF_PAGE_START document={label} page={page.page_number} ---"
            )
        parts.append(page.text)
        if include_page_markers:
            label = document_label or page.source_path or "document"
            parts.append(
                f"--- PDF_PAGE_END document={label} page={page.page_number} ---"
            )
    return "\n".join(parts)


def extract_text_from_image_bytes(image_bytes: bytes) -> str:
    """Backwards-compatible re-export of the image OCR helper."""
    return ocr_image_bytes(image_bytes)


def extract_text_from_bytes_sync(
    pdf_bytes: bytes,
    force_ocr: bool = False,
    use_ocr_threshold: int = 100,
) -> str:
    """Legacy sync extractor using pypdfium2 + Tesseract.

    Kept for backwards compatibility with the standalone
    ``extract_text_from_pdf_bytes_sync`` public symbol. New code should prefer
    ``extract_text_pages_from_bytes`` + ``format_page_text``.
    """
    with pdf_temp_file(pdf_bytes) as tmp_path:
        doc = pdfium.PdfDocument(str(tmp_path))
        all_text = ""
        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                try:
                    if force_ocr:
                        bitmap = page.render(scale=300 / 72)
                        pil_image = bitmap.to_pil()
                        if pil_image.mode != "RGB":
                            pil_image = pil_image.convert("RGB")
                        text = pytesseract.image_to_string(
                            pil_image, config=r"--oem 3 --psm 6"
                        )
                    else:
                        textpage = page.get_textpage()
                        text = textpage.get_text_range()
                        textpage.close()
                        if len(text.strip()) < use_ocr_threshold:
                            bitmap = page.render(scale=300 / 72)
                            pil_image = bitmap.to_pil()
                            if pil_image.mode != "RGB":
                                pil_image = pil_image.convert("RGB")
                            text = pytesseract.image_to_string(
                                pil_image, config=r"--oem 3 --psm 6"
                            )
                    all_text += text
                finally:
                    page.close()
        finally:
            doc.close()
        return all_text


__all__ = [
    "extract_text_pages",
    "extract_text_pages_async",
    "extract_text_pages_from_bytes",
    "extract_text_pages_from_bytes_async",
    "format_page_text",
    "extract_text_from_image_bytes",
    "extract_text_from_bytes_sync",
]
