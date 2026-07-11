"""Range-aware streaming download primitive.

Lifts the previously-inline /files/{id}/download logic from aidream into
matrx-utils so any host gets the same RFC-7233 Range handling, ETag,
Content-Disposition, and S3 chunked streaming for free.

Public API:

- :class:`StreamingResult` — the typed result a router converts to a FastAPI
  ``StreamingResponse`` (or any other web framework's equivalent).
- :func:`parse_range_header` — RFC-7233 parser. Returns ``(start, end)`` or
  the sentinel ``(-1, -1)`` for unsatisfiable ranges.
- :func:`build_content_disposition` — RFC-5987 + RFC-6266 compliant.
- :func:`sniffed_content_type` — anti-XSS coercion for inline rendering.
- :class:`DownloadStreamer` — orchestrates HEAD + Range parse + S3 streaming.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, AsyncIterator, Callable

# Content-Type / disposition policy lives in the stdlib-only leaf module so the
# write path + re-stamp backfill share the exact same decision. Re-exported
# below (see __all__) for back-compat with existing importers.
from ..content_headers import build_content_disposition, sniffed_content_type

if TYPE_CHECKING:
    from .sync_engine import SyncEngine

logger = logging.getLogger(__name__)


_RANGE_CHUNK_BYTES = 256 * 1024  # 256 KiB


def parse_range_header(header: str | None, total_size: int) -> tuple[int, int] | None:
    """Parse ``Range: bytes=<start>-<end>`` per RFC-7233.

    Returns ``(start, end)`` inclusive byte offsets, or ``None`` when the
    header is absent / malformed (caller serves the whole object). For
    unsatisfiable ranges (start beyond ``total_size``), returns the
    sentinel ``(-1, -1)`` so the caller can emit 416 Range Not Satisfiable.
    """
    if not header or total_size <= 0:
        return None
    if not header.strip().lower().startswith("bytes="):
        return None
    spec = header.strip()[6:]
    spec = spec.split(",", 1)[0].strip()
    if "-" not in spec:
        return None
    start_s, end_s = spec.split("-", 1)
    start_s, end_s = start_s.strip(), end_s.strip()
    last = total_size - 1
    try:
        if not start_s:
            n = int(end_s)
            if n <= 0:
                return None
            start = max(0, total_size - n)
            end = last
        else:
            start = int(start_s)
            end = int(end_s) if end_s else last
    except ValueError:
        return None
    if start > last:
        return (-1, -1)
    if end > last:
        end = last
    if end < start:
        return None
    return (start, end)


@dataclass
class StreamingResult:
    """Typed download response. Host wraps with the framework's streaming type."""
    iterator: Any                                # sync or async iterator yielding bytes
    media_type: str
    headers: dict[str, str]
    status_code: int                             # 200 | 206
    content_length: int


class DownloadStreamer:
    """Reads a cld_files row's bytes with Range support.

    Selects between S3 chunked streaming (current version, S3-backed) and
    buffered fallback (other backends, version reads, public CDN redirect).
    Public CDN redirection is the caller's responsibility — the streamer
    operates on bytes only.
    """

    def __init__(self, engine: "SyncEngine") -> None:
        self._engine = engine

    async def open_stream(
        self,
        record: dict,
        *,
        range_header: str | None = None,
        version: int | None = None,
        allow_inline: bool = False,
    ) -> StreamingResult:
        """Open a streaming download for the given file record.

        - ``range_header``: RFC-7233 Range header value (None → full content).
        - ``version``: pin to a specific version (versions use buffered reads).
        - ``allow_inline``: allow inline disposition for image/video/audio/PDF.
        """
        media_type, force_attachment = sniffed_content_type(
            record, allow_inline=allow_inline,
        )
        base_headers: dict[str, str] = {
            "Accept-Ranges": "bytes",
            "Content-Disposition": build_content_disposition(
                record.get("file_name") or "file",
                force_attachment=force_attachment,
            ),
            "ETag": f'"{record.get("checksum") or ""}"',
        }

        # Version reads: VersionManager owns the storage URI shape. Buffered.
        if version is not None:
            content = await self._engine.versions.read_version_async(
                record["id"], version,
            )
            if content is None:
                raise FileNotFoundError(
                    f"Version {version} not found for file {record['id']!r}"
                )
            return StreamingResult(
                iterator=_single_chunk_iter(content),
                media_type=media_type,
                headers={
                    **base_headers,
                    "Content-Length": str(len(content)),
                },
                status_code=200,
                content_length=len(content),
            )

        # Current version: prefer S3 chunked streaming when the backend
        # supports it; fall back to buffered for non-S3 backends.
        from .cdn import public_url_for  # noqa — caller wrangles redirects, not us
        del public_url_for  # silence linter; intentionally not used here

        storage_uri = (
            record.get("canonical_storage_uri")
            or record.get("storage_uri")
            or ""
        )
        router = self._engine.router
        s3_backend = router.s3 if router.is_configured("s3") else None

        # Non-S3 backend: buffered fallback. Range still advertised, just
        # served as 200 with full content.
        if s3_backend is None or not hasattr(s3_backend, "_get_client"):
            content = await router.read_async(storage_uri)
            return StreamingResult(
                iterator=_single_chunk_iter(content),
                media_type=media_type,
                headers={**base_headers, "Content-Length": str(len(content))},
                status_code=200,
                content_length=len(content),
            )

        # S3 path: resolve bucket/key, HEAD for size if the row didn't carry one.
        uri_path = storage_uri.split("://", 1)[1]
        bucket, key = s3_backend._parse_path(uri_path)
        client = s3_backend._get_client()

        total_size = int(record.get("size_bytes") or 0)
        if total_size <= 0:
            head = client.head_object(Bucket=bucket, Key=key)
            total_size = int(head.get("ContentLength") or 0)

        parsed = parse_range_header(range_header, total_size)
        # Unsatisfiable — caller emits 416 with this Content-Range header.
        if parsed == (-1, -1):
            return StreamingResult(
                iterator=_single_chunk_iter(b""),
                media_type=media_type,
                headers={**base_headers, "Content-Range": f"bytes */{total_size}"},
                status_code=416,
                content_length=0,
            )

        get_kw: dict[str, Any] = {"Bucket": bucket, "Key": key}
        is_range = parsed is not None
        if is_range:
            start, end = parsed  # type: ignore[misc]
            get_kw["Range"] = f"bytes={start}-{end}"

        s3_resp = client.get_object(**get_kw)
        body = s3_resp.get("Body")
        if body is None:
            raise RuntimeError("S3 returned no body")

        if is_range:
            start, end = parsed  # type: ignore[misc]
            content_length = end - start + 1
            headers = {
                **base_headers,
                "Content-Range": f"bytes {start}-{end}/{total_size}",
                "Content-Length": str(content_length),
            }
            status_code = 206
        else:
            content_length = total_size
            headers = {**base_headers, "Content-Length": str(total_size)}
            status_code = 200

        def _iter_chunks():
            try:
                for chunk in body.iter_chunks(chunk_size=_RANGE_CHUNK_BYTES):
                    if chunk:
                        yield chunk
            finally:
                try:
                    body.close()
                except Exception:
                    pass

        return StreamingResult(
            iterator=_iter_chunks(),
            media_type=media_type,
            headers=headers,
            status_code=status_code,
            content_length=content_length,
        )


def _single_chunk_iter(content: bytes):
    """One-shot iterator for buffered fallback paths."""
    def _gen():
        if content:
            yield content
    return _gen()


__all__ = [
    "StreamingResult",
    "DownloadStreamer",
    "parse_range_header",
    "build_content_disposition",
    "sniffed_content_type",
]
