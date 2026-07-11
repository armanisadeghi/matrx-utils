"""Canonical files router — CRUD + URLs.

Exposes the most-used file endpoints:

    POST   /files/upload
    GET    /files/{file_id}
    GET    /files/{file_id}/url
    PATCH  /files/{file_id}
    DELETE /files/{file_id}
    POST   /files/{file_id}/restore

A host that needs more (folder CRUD, share-link CRUD, group ACL, search,
trash, presigned uploads, TUS) wires their own routers calling the
same ``FileService`` methods. This factory covers the standalone-test
surface: a new host can mount this and have a working file system.
"""

from __future__ import annotations

import json
from typing import Any, AsyncIterator, Callable, Literal
from urllib.parse import quote as _url_quote

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel, Field

from ..service import FileService
from ..media_sniff import SNIFF_HEAD_BYTES, sniff_mime_type


class _FileRecord(BaseModel):
    file_id: str
    file_path: str
    file_name: str
    mime_type: str | None = None
    size_bytes: int | None = None
    visibility: str = "private"
    folder_id: str | None = None
    owner_id: str
    created_at: str | None = None
    updated_at: str | None = None
    deleted_at: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    version: int = 1


class _UploadResponse(BaseModel):
    file_id: str
    file_path: str
    size_bytes: int | None = None
    checksum: str | None = None
    url: str | None = None
    cdn_url: str | None = None
    signed_url: str | None = None
    download_url: str | None = None
    visibility: str = "private"


class _UrlResponse(BaseModel):
    file_id: str
    url: str | None = None
    cdn_url: str | None = None
    signed_url: str | None = None
    download_url: str | None = None


class _PatchBody(BaseModel):
    """Union mutation body for PATCH /files/{id}.

    Every field is optional. Sub-operations run sequentially with best-
    effort atomicity; failures accumulate in ``errors[]`` on the
    response envelope rather than rolling everything back.
    """
    # Direct field updates
    name: str | None = None
    folder: str | None = None
    visibility: Literal["public", "private", "shared"] | None = None
    metadata: dict[str, Any] | None = None
    # Bundled sub-ops
    share: dict[str, Any] | None = None
    share_revoke: bool = False
    permissions: list[dict[str, Any]] | None = None
    permissions_revoke: list[dict[str, Any]] | None = None
    variants: list[str] | list[dict[str, Any]] | None = None
    # Version + trash management
    restore_version: int | None = None
    restore_from_trash: bool = False
    # Copy out
    copy_to: str | None = None


class _BulkBody(BaseModel):
    """Bulk discriminator: ``{ids[], op, args}``."""
    ids: list[str] = Field(..., min_length=1, max_length=500)
    op: Literal["move", "delete", "restore", "visibility", "share"]
    args: dict[str, Any] | None = None


def _to_record(row: dict) -> _FileRecord:
    return _FileRecord(
        file_id=row["id"],
        file_path=row["file_path"],
        file_name=row.get("file_name") or row["file_path"].rsplit("/", 1)[-1],
        mime_type=row.get("mime_type"),
        size_bytes=row.get("size_bytes"),
        visibility=row.get("visibility", "private"),
        folder_id=row.get("parent_folder_id"),
        owner_id=row.get("owner_id", ""),
        created_at=str(row["created_at"]) if row.get("created_at") else None,
        updated_at=str(row["updated_at"]) if row.get("updated_at") else None,
        deleted_at=str(row["deleted_at"]) if row.get("deleted_at") else None,
        metadata=row.get("metadata") or {},
        version=row.get("current_version", 1),
    )


def _map_exc(exc: Exception) -> HTTPException:
    if isinstance(exc, HTTPException):
        return exc
    if isinstance(exc, PermissionError):
        return HTTPException(status.HTTP_403_FORBIDDEN, {"error": "permission_denied", "message": str(exc)})
    if isinstance(exc, FileNotFoundError):
        return HTTPException(status.HTTP_404_NOT_FOUND, {"error": "not_found", "message": str(exc)})
    if isinstance(exc, ValueError):
        return HTTPException(status.HTTP_400_BAD_REQUEST, {"error": "invalid_request", "message": str(exc)})
    return HTTPException(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        {"error": "internal", "message": "File operation failed"},
    )


# Range-header support for /download endpoint (RFC 7233).
_RANGE_CHUNK_BYTES = 256 * 1024  # 256 KiB — keeps the byte cache happy.


def _parse_range_header(header: str | None, total_size: int) -> tuple[int, int] | None:
    """Parse ``Range: bytes=<start>-<end>``.

    Returns (start, end) inclusive offsets, ``None`` when absent or malformed,
    or the sentinel ``(-1, -1)`` when the request is unsatisfiable so the
    caller can return 416.
    """
    if not header or total_size <= 0:
        return None
    if not header.strip().lower().startswith("bytes="):
        return None
    spec = header.strip()[6:].split(",", 1)[0].strip()
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
            start, end = max(0, total_size - n), last
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


def _content_disposition(file_name: str, *, attachment: bool) -> str:
    disp = "attachment" if attachment else "inline"
    try:
        file_name.encode("ascii")
        return f'{disp}; filename="{file_name}"'
    except UnicodeEncodeError:
        ascii_fallback = file_name.encode("ascii", "replace").decode("ascii")
        return f"{disp}; filename=\"{ascii_fallback}\"; filename*=UTF-8''{_url_quote(file_name)}"


def build_file_router(
    file_service: FileService,
    *,
    user_id_dep: Callable[..., str] | None = None,
    prefix: str = "/files",
    tags: list[str] | None = None,
) -> APIRouter:
    """Build a FastAPI router exposing the core file endpoints.

    ``user_id_dep`` MUST be a FastAPI dependency that returns the
    authenticated user_id (a string). Hosts wire this to their JWT
    validation / guest fingerprint resolver. Without a real
    ``user_id_dep`` the router will accept all requests with an
    anonymous user_id — fine for tests, dangerous in production.
    """
    router = APIRouter(prefix=prefix, tags=tags or ["files"])

    if user_id_dep is None:
        # Test-mode default: every request is the same anonymous user.
        def user_id_dep() -> str:  # noqa: E306
            return "anonymous"

    # ------------------------------------------------------------------
    # POST /upload — buffered multipart write.
    # ------------------------------------------------------------------
    @router.post("/upload", response_model=_UploadResponse)
    async def upload_file(
        file: UploadFile = File(...),
        file_path: str = Form(...),
        visibility: Literal["public", "private", "shared"] = Form("private"),
        metadata_json: str | None = Form(None),
        x_request_id: str | None = Header(default=None, alias="X-Request-Id"),
        x_idempotency_key: str | None = Header(default=None, alias="X-Idempotency-Key"),
        user_id: str = Depends(user_id_dep),
    ) -> _UploadResponse:
        try:
            content = await file.read()
            sniffed_mime = sniff_mime_type(
                claimed=file.content_type,
                head_bytes=content[:SNIFF_HEAD_BYTES],
                filename=file.filename,
            )
            parsed_meta: dict[str, Any] = {}
            if metadata_json:
                try:
                    parsed_meta = json.loads(metadata_json)
                except (json.JSONDecodeError, ValueError) as e:
                    raise HTTPException(400, {"error": "invalid_metadata", "message": str(e)})
            # Stamp request_id into metadata so the realtime row carries it
            # and the FE can deterministically dedup its own writes.
            if x_request_id:
                parsed_meta["request_id"] = x_request_id
            if x_idempotency_key:
                parsed_meta["_idempotency_key"] = x_idempotency_key
            result = await file_service.write(
                content,
                file_path=file_path,
                mime_type=sniffed_mime,
                visibility=visibility,
                user_id=user_id,
                metadata=parsed_meta or None,
            )
            return _UploadResponse(
                file_id=result.file_id,
                file_path=file_path,
                size_bytes=result.size_bytes,
                checksum=result.checksum,
                url=result.url,
                cdn_url=result.cdn_url,
                signed_url=result.signed_url,
                download_url=result.download_url,
                visibility=result.visibility,
            )
        except Exception as e:
            raise _map_exc(e)

    # ------------------------------------------------------------------
    # GET /{file_id} — fetch a single record.
    # ------------------------------------------------------------------
    @router.get("/{file_id}", response_model=_FileRecord)
    async def get_file(
        file_id: str,
        user_id: str = Depends(user_id_dep),
    ) -> _FileRecord:
        try:
            record = await file_service.read_record(file_id, user_id=user_id)
            return _to_record(record)
        except Exception as e:
            raise _map_exc(e)

    # ------------------------------------------------------------------
    # GET /{file_id}/download — bytes stream with ETag + Range + Length.
    #
    # Honours RFC 7233 Range requests so the FE byte cache + Service
    # Worker can stream large PDFs / videos chunk-by-chunk and resume
    # mid-flight. ETag is the SHA-256 checksum from the cld_files row;
    # the FE keys its IndexedDB cache on this so the cache survives
    # version bumps without unnecessary re-downloads.
    # ------------------------------------------------------------------
    @router.get("/{file_id}/download")
    async def download_file(
        file_id: str,
        request: Request,
        inline: bool = Query(False, description="Set Content-Disposition: inline (render in browser)"),
        user_id: str = Depends(user_id_dep),
    ):
        try:
            record = await file_service.read_record(file_id, user_id=user_id)
        except Exception as e:
            raise _map_exc(e)

        file_name = record.get("file_name") or record["file_path"].rsplit("/", 1)[-1]
        media_type = record.get("mime_type") or "application/octet-stream"
        checksum = record.get("checksum") or ""
        total_size = int(record.get("size_bytes") or 0)

        # If we don't know the total size yet (legacy rows), HEAD S3.
        storage_uri = record.get("canonical_storage_uri") or record["storage_uri"]
        s3 = None
        backend_router = file_service.router
        if hasattr(backend_router, "is_configured") and backend_router.is_configured("s3"):
            s3 = backend_router.s3
        if total_size <= 0 and s3 is not None:
            try:
                uri_path = storage_uri.split("://", 1)[1]
                bucket, key = s3._parse_path(uri_path)
                head = await s3.get_metadata_async(uri_path)
                total_size = int(head.get("size") or 0)
            except Exception:
                pass

        base_headers = {
            "Accept-Ranges": "bytes",
            "X-Content-Type-Options": "nosniff",
            "ETag": f'"{checksum}"',
            "Content-Disposition": _content_disposition(file_name, attachment=not inline),
        }

        # Range path (RFC 7233). Only S3-backed reads support streaming —
        # other backends fall back to buffered.
        range_header = request.headers.get("range") or request.headers.get("Range")
        parsed = _parse_range_header(range_header, total_size) if total_size > 0 else None

        if parsed == (-1, -1):
            return Response(
                status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                headers={**base_headers, "Content-Range": f"bytes */{total_size}"},
            )

        # S3 streaming path (range-aware).
        if s3 is not None and total_size > 0:
            try:
                uri_path = storage_uri.split("://", 1)[1]
                bucket, key = s3._parse_path(uri_path)
            except Exception as e:
                raise _map_exc(e)
            client = s3._get_client()
            get_kw: dict[str, Any] = {"Bucket": bucket, "Key": key}
            is_range = parsed is not None
            if is_range:
                start, end = parsed  # type: ignore[misc]
                get_kw["Range"] = f"bytes={start}-{end}"
            try:
                s3_resp = client.get_object(**get_kw)
            except Exception as e:
                raise _map_exc(e)
            body = s3_resp.get("Body")
            if body is None:
                raise HTTPException(502, {"error": "s3_error", "message": "S3 returned no body"})

            if is_range:
                start, end = parsed  # type: ignore[misc]
                length = end - start + 1
                headers = {**base_headers, "Content-Range": f"bytes {start}-{end}/{total_size}", "Content-Length": str(length)}
                status_code = status.HTTP_206_PARTIAL_CONTENT
            else:
                headers = {**base_headers, "Content-Length": str(total_size)}
                status_code = status.HTTP_200_OK

            def _iter_chunks() -> AsyncIterator[bytes]:
                try:
                    for chunk in body.iter_chunks(chunk_size=_RANGE_CHUNK_BYTES):
                        if chunk:
                            yield chunk
                finally:
                    try:
                        body.close()
                    except Exception:
                        pass

            return StreamingResponse(
                _iter_chunks(),
                status_code=status_code,
                media_type=media_type,
                headers=headers,
            )

        # Buffered fallback (non-S3 backends or unknown size).
        try:
            content = await backend_router.read_async(storage_uri)
        except Exception as e:
            raise _map_exc(e)
        return Response(
            content=content,
            media_type=media_type,
            headers={**base_headers, "Content-Length": str(len(content))},
        )

    # ------------------------------------------------------------------
    # GET /{file_id}/url — canonical URL envelope.
    # ------------------------------------------------------------------
    @router.get("/{file_id}/url", response_model=_UrlResponse)
    async def get_file_url(
        file_id: str,
        user_id: str = Depends(user_id_dep),
    ) -> _UrlResponse:
        try:
            record = await file_service.read_record(file_id, user_id=user_id)
            urls = await file_service.build_urls(record)
            return _UrlResponse(file_id=file_id, **urls)
        except Exception as e:
            raise _map_exc(e)

    # ------------------------------------------------------------------
    # PATCH /{file_id} — union mutation body (FE-team A.2).
    #
    # Accepts any combination of: name / folder / visibility / metadata /
    # share / share_revoke / permissions / permissions_revoke / variants /
    # restore_version / restore_from_trash / copy_to.
    # Returns the canonical envelope with an ``errors[]`` array listing
    # any sub-op failures (best-effort atomic, never full rollback).
    # ------------------------------------------------------------------
    @router.patch("/{file_id}")
    async def patch_file(
        file_id: str,
        body: _PatchBody,
        x_idempotency_key: str | None = Header(default=None, alias="X-Idempotency-Key"),
        user_id: str = Depends(user_id_dep),
    ) -> dict:
        try:
            return await file_service.mutate_file(
                file_id,
                user_id=user_id,
                name=body.name,
                folder=body.folder,
                visibility=body.visibility,
                metadata=body.metadata,
                share=body.share,
                share_revoke=body.share_revoke,
                permissions=body.permissions,
                permissions_revoke=body.permissions_revoke,
                variants=body.variants,
                restore_version=body.restore_version,
                restore_from_trash=body.restore_from_trash,
                copy_to=body.copy_to,
                idempotency_key=x_idempotency_key,
                request_payload_for_idempotency=body.model_dump(exclude_none=True),
            )
        except Exception as e:
            raise _map_exc(e)

    # ------------------------------------------------------------------
    # POST /bulk — bulk discriminator (FE-team A.3).
    # ------------------------------------------------------------------
    @router.post("/bulk")
    async def bulk_files(
        body: _BulkBody,
        x_idempotency_key: str | None = Header(default=None, alias="X-Idempotency-Key"),
        user_id: str = Depends(user_id_dep),
    ) -> dict:
        try:
            return await file_service.bulk_op(
                user_id=user_id,
                ids=body.ids,
                op=body.op,
                args=body.args,
                idempotency_key=x_idempotency_key,
                request_payload_for_idempotency=body.model_dump(),
            )
        except Exception as e:
            raise _map_exc(e)

    # ------------------------------------------------------------------
    # DELETE /{file_id} — soft delete.
    # ------------------------------------------------------------------
    @router.delete("/{file_id}")
    async def delete_file(
        file_id: str,
        user_id: str = Depends(user_id_dep),
    ) -> dict:
        try:
            ok = await file_service.soft_delete(file_id, user_id=user_id)
            return {"deleted": bool(ok)}
        except Exception as e:
            raise _map_exc(e)

    # ------------------------------------------------------------------
    # POST /{file_id}/restore — undo a soft-delete.
    # ------------------------------------------------------------------
    @router.post("/{file_id}/restore")
    async def restore_file(
        file_id: str,
        user_id: str = Depends(user_id_dep),
    ) -> dict:
        try:
            ok = await file_service.restore(file_id, user_id=user_id)
            return {"restored": bool(ok)}
        except Exception as e:
            raise _map_exc(e)

    return router


__all__ = ["build_file_router"]
