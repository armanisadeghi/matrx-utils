from __future__ import annotations

import asyncio
import io
import os
import re
import uuid
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

import fitz
import httpx
import pytesseract
from PIL import Image
from pydantic import BaseModel

from matrx_utils.file_handling.file_handler import FileHandler


# ---------------------------------------------------------------------------
# AI processor protocol
# ---------------------------------------------------------------------------


@runtime_checkable
class AiChunkProcessor(Protocol):
    """
    Callable contract for AI-based chunk processing.

    Callers supply a concrete async function (or any async callable object)
    that accepts a single text chunk and returns a plain dict.  The utility
    library never imports an AI SDK directly — the consumer owns that logic.

    Example implementation (in your AI-enabled app)::

        async def my_ai_processor(chunk: str) -> dict[str, Any]:
            response = await openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": chunk}],
            )
            return {"content": response.choices[0].message.content}

        result = await pdf_handler.full_pipeline(
            source=url,
            options=PdfPipelineOptions(chunk_and_process_with_ai=True),
            ai_processor=my_ai_processor,
        )
    """

    async def __call__(self, chunk: str) -> dict[str, Any]: ...


# ---------------------------------------------------------------------------
# Pydantic models — shared between PDFHandler and the router
# ---------------------------------------------------------------------------


class PdfPipelineOptions(BaseModel):
    extract_text: bool = True
    force_ocr: bool = False
    use_ocr_threshold: int = 100
    extract_tables: bool = False
    chunk_and_process_with_ai: bool = False
    chunk_size: int = 2000
    overlap_size: int = 200
    # Set to a full cloud URI to upload the extracted text after processing.
    # Supports any configured backend, e.g.:
    #   "supabase://bucket/pdf_results/"
    #   "s3://bucket/pdf_results/"
    #   "server://uploads/pdf_results/"
    # Leave as None (default) to skip upload.
    upload_result_to: str | None = None


class PdfResult(BaseModel):
    raw_text: str | None = None
    chunks: list[str] | None = None
    ai_processed: list[dict[str, Any]] | None = None
    tables_path: str | None = None
    cloud_uri: str | None = None


# ---------------------------------------------------------------------------
# PDFHandler
# ---------------------------------------------------------------------------


class PDFHandler(FileHandler):
    def __init__(self, app_name: str, batch_print: bool = False):
        super().__init__(app_name, batch_print=batch_print)

    # ------------------------------------------------------------------
    # Legacy read helpers (kept for backwards compatibility)
    # ------------------------------------------------------------------

    def read_pdf_file(self, path: str) -> fitz.Document | None:
        try:
            pdf = fitz.open(path)
            self._print_link(path=path, message="Read PDF file")
            return pdf
        except Exception as e:
            self._print_link(path=path, message="Error reading PDF", color="red")
            print(f"Error: {str(e)}")
            return None

    def _return_if_pdf_valid(self, pdf: Any) -> fitz.Document | None:
        if pdf and isinstance(pdf, fitz.Document):
            return pdf
        return None

    def custom_read_pdf(self, path: str) -> fitz.Document | None:
        pdf = self.read_pdf_file(path)
        return self._return_if_pdf_valid(pdf)

    def custom_delete_pdf(self, path: str) -> bool:
        return self.delete(path)

    def read_pdf(self, root: str, path: str) -> fitz.Document | None:
        full_path = self._get_full_path(root, path)
        return self.read_pdf_file(str(full_path))

    def delete_pdf(self, root: str, path: str) -> bool:
        return self.delete_from_base(root, path)

    # ------------------------------------------------------------------
    # Remote fetch — URL, Supabase file dict, or local path
    # ------------------------------------------------------------------

    async def fetch_remote(self, source: str | dict) -> str | None:
        """
        Resolve *source* to a local temp file path.

        Accepts:
        - A plain URL string        → downloaded via httpx
        - A Supabase file dict      → tried via URL first, then Supabase storage
        - A local file path string  → returned as-is if the file exists
        """
        if isinstance(source, dict):
            return await self._fetch_file_object(source)

        if isinstance(source, str):
            if source.startswith("http://") or source.startswith("https://"):
                return await self._download_url(source)
            if os.path.isfile(source):
                return source

        return None

    async def _download_url(self, url: str, extension: str = "pdf") -> str | None:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url)
                response.raise_for_status()
                temp_filename = f"{uuid.uuid4()}.{extension}"
                written = self.write_to_base(
                    root="temp", path=temp_filename, content=response.content
                )
                if written:
                    return str(self._get_full_path("temp", temp_filename))
        except Exception as e:
            print(f"[PDFHandler] URL download failed: {e}")
        return None

    async def _fetch_file_object(self, file_object: dict) -> str | None:
        url = file_object.get("url", "")
        details = file_object.get("details", {})
        extension = str(details.get("extension", "pdf"))
        bucket = details.get("bucket")
        filename = details.get("filename")
        path = details.get("path")

        # First attempt: HTTP download
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                http_response = await client.get(url)
                http_response.raise_for_status()
                temp_filename = f"{uuid.uuid4()}.{extension}"
                written = self.write_to_base(
                    root="temp", path=temp_filename, content=http_response.content
                )
                if written:
                    return str(self._get_full_path("temp", temp_filename))
        except Exception:
            pass

        # Second attempt: read via cloud credentials using the URL already
        # present in the file object — cloud_read_url handles signed, expired,
        # public, and native URI formats transparently.
        if url:
            try:
                content = self.cloud_read_url(url)
                if content:
                    temp_filename = f"{uuid.uuid4()}.{extension}"
                    written = self.write_to_base(
                        root="temp", path=temp_filename, content=content, clean=False, remove_html=False
                    )
                    if written:
                        return str(self._get_full_path("temp", temp_filename))
            except Exception as e:
                print(f"[PDFHandler] Cloud credential fetch failed: {e}")

        # Third attempt: construct a native URI from bucket + path and read directly
        if bucket and (path or filename):
            try:
                storage_path = f"{path}/{filename}" if path and filename else (filename or path or "")
                native_uri = f"supabase://{bucket}/{storage_path}"
                content = self.cloud_read(native_uri)
                if content:
                    temp_filename = f"{uuid.uuid4()}.{extension}"
                    written = self.write_to_base(
                        root="temp", path=temp_filename, content=content, clean=False, remove_html=False
                    )
                    if written:
                        return str(self._get_full_path("temp", temp_filename))
            except Exception as e:
                print(f"[PDFHandler] Native URI fetch failed: {e}")

        return None

    # ------------------------------------------------------------------
    # Text extraction
    # ------------------------------------------------------------------

    async def extract_text(
        self,
        path: str,
        force_ocr: bool = False,
        use_ocr_threshold: int = 100,
        emitter: Any | None = None,
    ) -> str:
        """
        Extract text from a PDF at *path* (local absolute path).

        force_ocr=True  → run Tesseract on every page unconditionally.
        Otherwise, Tesseract is used only when a page has fewer than
        *use_ocr_threshold* characters of native text.
        """
        doc = fitz.open(path)
        all_text = ""
        batch_size = 10

        try:
            for page_num in range(doc.page_count):
                page = doc[page_num]

                if force_ocr:
                    text = await self._ocr_page(page)
                else:
                    text = page.get_text()
                    if len(text.strip()) < use_ocr_threshold:
                        text = await self._ocr_page(page)

                all_text += text

                if emitter and (
                    page_num % batch_size == batch_size - 1
                    or page_num == doc.page_count - 1
                ):
                    await emitter.send_status_update(
                        status="processing",
                        user_visible_message=f"Processed page {page_num + 1} of {doc.page_count}",
                        system_message=f"pdf_extract page {page_num + 1}/{doc.page_count}",
                    )
        finally:
            doc.close()

        return all_text

    async def _ocr_page(self, page: fitz.Page) -> str:
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.pil_tobytes(format="jpeg")))
        custom_config = r"--oem 3 --psm 6"
        return pytesseract.image_to_string(img, config=custom_config)

    # ------------------------------------------------------------------
    # Table extraction
    # ------------------------------------------------------------------

    def extract_tables(
        self,
        path: str,
        output_format: str = "csv",
    ) -> str | None:
        """
        Extract tables from the PDF at *path* using tabula.
        Saves the result to the temp directory and returns the output file path.
        Requires Java to be installed on the system.
        """
        try:
            import tabula  # type: ignore[import]
        except ImportError:
            raise RuntimeError(
                "tabula-py is not installed. Run: uv pip install tabula-py"
            )

        try:
            base_name = re.sub(r"[^\w\-]", "_", Path(path).stem)
            out_filename = f"{base_name}_table.{output_format}"
            out_path = str(self._get_full_path("temp", out_filename))
            os.makedirs(os.path.dirname(out_path), exist_ok=True)

            tabula.convert_into(path, out_path, output_format=output_format, pages="all")
            print(f"[PDFHandler] Tables extracted → {out_path}")
            return out_path
        except Exception as e:
            print(f"[PDFHandler] Table extraction failed: {e}")
            return None

    # ------------------------------------------------------------------
    # Chunking
    # ------------------------------------------------------------------

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 2000,
        overlap_size: int = 200,
    ) -> list[str]:
        """Split *text* into overlapping chunks."""
        chunks: list[str] = []
        text_length = len(text)
        step = max(chunk_size - overlap_size, 1)
        for i in range(0, text_length, step):
            chunk = text[i : i + chunk_size]
            if chunk.strip():
                chunks.append(chunk)
        return chunks

    # ------------------------------------------------------------------
    # AI processing
    # ------------------------------------------------------------------

    async def process_chunks_with_ai(
        self,
        chunks: list[str],
        ai_processor: AiChunkProcessor,
        emitter: Any | None = None,
    ) -> list[dict[str, Any]]:
        """
        Process each chunk through a caller-supplied AI function.

        *ai_processor* must be an async callable matching :class:`AiChunkProcessor`:
        it receives a single text chunk and returns a ``dict``.  All chunks are
        dispatched concurrently via ``asyncio.gather``.
        """
        results: list[dict[str, Any]] = []
        tasks = [ai_processor(chunk) for chunk in chunks]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        for idx, resp in enumerate(responses):
            if isinstance(resp, Exception):
                print(f"[PDFHandler] AI chunk {idx} failed: {resp}")
                results.append({"error": str(resp), "chunk_index": idx})
            else:
                content = resp.get("content") if isinstance(resp, dict) else None
                results.append({"content": content, "chunk_index": idx})

            if emitter:
                await emitter.send_status_update(
                    status="processing",
                    user_visible_message=f"AI processed chunk {idx + 1} of {len(chunks)}",
                    system_message=f"ai_chunks {idx + 1}/{len(chunks)}",
                )

        return results

    # ------------------------------------------------------------------
    # PDF write
    # ------------------------------------------------------------------

    def write_pdf(self, root: str, path: str, data: Any) -> bool:
        """
        Write PDF content to *path*.

        Accepts:
        - fitz.Document  → saved directly with fitz
        - bytes           → written as raw binary
        - str             → encoded as UTF-8 and written (plain-text PDF)
        """
        full_path = self._get_full_path(root, path)
        self._ensure_directory(full_path)

        try:
            if isinstance(data, fitz.Document):
                data.save(str(full_path))
                data.close()
                return True
            if isinstance(data, bytes):
                full_path.write_bytes(data)
                return True
            if isinstance(data, str):
                full_path.write_bytes(data.encode("utf-8"))
                return True
        except Exception as e:
            print(f"[PDFHandler] write_pdf failed: {e}")

        return False

    def write_pdf_file(self, path: str, content: Any) -> bool:
        """Write to an absolute path."""
        p = Path(path)
        self._ensure_directory(p)
        try:
            if isinstance(content, fitz.Document):
                content.save(str(p))
                content.close()
                return True
            if isinstance(content, bytes):
                p.write_bytes(content)
                return True
            if isinstance(content, str):
                p.write_bytes(content.encode("utf-8"))
                return True
        except Exception as e:
            print(f"[PDFHandler] write_pdf_file failed: {e}")
        return False

    # ------------------------------------------------------------------
    # Full pipeline
    # ------------------------------------------------------------------

    async def full_pipeline(
        self,
        source: str | dict,
        options: PdfPipelineOptions | None = None,
        emitter: Any | None = None,
        ai_processor: AiChunkProcessor | None = None,
    ) -> PdfResult:
        """
        Run the full PDF processing pipeline.

        *source* can be a URL, file dict (with "url"/"details" keys), or local
        file path. Each stage is independently opt-in via *options*.

        Set ``options.upload_result_to`` to a full cloud URI prefix to store
        the extracted text after processing, e.g.:
            ``"supabase://bucket/pdf_results/"``
            ``"s3://bucket/pdf_results/"``

        When ``options.chunk_and_process_with_ai`` is ``True``, *ai_processor*
        **must** be provided — it is an async callable matching
        :class:`AiChunkProcessor`.  A ``ValueError`` is raised at runtime if
        the flag is set but no processor is supplied, so misconfiguration is
        caught early rather than failing silently mid-pipeline.
        """
        opts = options or PdfPipelineOptions()
        result = PdfResult()

        if opts.chunk_and_process_with_ai and ai_processor is None:
            raise ValueError(
                "[PDFHandler] options.chunk_and_process_with_ai is True but no "
                "ai_processor was provided.  Pass an async callable that accepts "
                "a chunk string and returns a dict."
            )

        # 1. Resolve source to a local path
        local_path = await self.fetch_remote(source)
        if not local_path:
            raise ValueError(f"[PDFHandler] Could not resolve source to a local file: {source}")

        # 2. Text extraction
        if opts.extract_text:
            result.raw_text = await self.extract_text(
                local_path,
                force_ocr=opts.force_ocr,
                use_ocr_threshold=opts.use_ocr_threshold,
                emitter=emitter,
            )

        # 3. Table extraction
        if opts.extract_tables:
            result.tables_path = self.extract_tables(local_path)

        # 4. Chunk + AI
        if opts.chunk_and_process_with_ai and result.raw_text and ai_processor:
            chunks = self.chunk_text(
                result.raw_text,
                chunk_size=opts.chunk_size,
                overlap_size=opts.overlap_size,
            )
            result.chunks = chunks
            result.ai_processed = await self.process_chunks_with_ai(
                chunks,
                ai_processor=ai_processor,
                emitter=emitter,
            )

        # 5. Upload result to cloud storage
        if opts.upload_result_to and result.raw_text:
            try:
                dest_prefix = opts.upload_result_to.rstrip("/")
                dest_uri = f"{dest_prefix}/{uuid.uuid4()}.txt"
                self.cloud_write(dest_uri, result.raw_text.encode("utf-8"))
                result.cloud_uri = dest_uri
            except Exception as e:
                print(f"[PDFHandler] Cloud upload failed: {e}")

        return result
