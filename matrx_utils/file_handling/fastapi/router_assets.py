"""Canonical asset router — preset-driven uploads + variant rendering.

Exposes:

    GET    /assets/presets               list every preset the server knows
    POST   /assets                       upload + render preset variants
    GET    /assets/{file_id}             read the Asset envelope
    GET    /files/{file_id}/asset        Asset envelope for any cld_files row

(The /files/{id}/asset endpoint lives here for the standalone-test path
where hosts mount a single router and get both /files and /assets.)
"""

from __future__ import annotations

import json
from typing import Any, Callable, Literal

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, Query, UploadFile, status
from pydantic import BaseModel, Field

from ..asset_envelope import Asset
from ..media_sniff import SNIFF_HEAD_BYTES, sniff_mime_type
from ..service import FileService


class _PreviewVariantSpec(BaseModel):
    """One target render for ``POST /assets/preview``. Mirrors
    StudioRenderSpec from the image handler."""
    preset_id: str = Field(..., description="Stable id used as the staged key suffix")
    width: int = Field(..., gt=0, le=8192)
    height: int = Field(..., gt=0, le=8192)
    format: Literal["jpeg", "png", "webp", "avif"] = "jpeg"
    quality: int = Field(85, ge=1, le=100)
    fit: Literal["cover", "contain", "inside"] = "cover"
    position: Any = "center"           # str OR {x, y}
    background_color: str = "#ffffff"


class _PreviewBody(BaseModel):
    """``POST /assets/preview`` accepts EITHER a master MediaRef OR raw
    bytes via multipart (separate endpoint variant)."""
    source: dict[str, Any] = Field(..., description='MediaRef {"file_id": "..."}')
    variants: list[_PreviewVariantSpec]
    max_inline_bytes: int = Field(default=256 * 1024, ge=1024, le=10 * 1024 * 1024)


class _PdfCompressBody(BaseModel):
    source: dict[str, Any] = Field(..., description='MediaRef {"file_id": "..."}')
    level: int = Field(3, ge=1, le=5)
    max_size_bytes: int | None = None
    max_inline_bytes: int = Field(default=256 * 1024, ge=1024, le=10 * 1024 * 1024)


def _map_exc(exc: Exception) -> HTTPException:
    if isinstance(exc, HTTPException):
        return exc
    if isinstance(exc, PermissionError):
        return HTTPException(status.HTTP_403_FORBIDDEN, {"error": "permission_denied", "message": str(exc)})
    if isinstance(exc, FileNotFoundError):
        return HTTPException(status.HTTP_404_NOT_FOUND, {"error": "not_found", "message": str(exc)})
    if isinstance(exc, KeyError):
        return HTTPException(status.HTTP_400_BAD_REQUEST, {"error": "invalid_request", "message": str(exc)})
    if isinstance(exc, ValueError):
        return HTTPException(status.HTTP_400_BAD_REQUEST, {"error": "invalid_request", "message": str(exc)})
    return HTTPException(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        {"error": "internal", "message": "Asset operation failed"},
    )


def build_asset_router(
    file_service: FileService,
    *,
    user_id_dep: Callable[..., str] | None = None,
    prefix: str = "",
    tags: list[str] | None = None,
) -> APIRouter:
    """Build a FastAPI router exposing the preset-driven asset endpoints.

    ``user_id_dep`` is a FastAPI dependency returning the authenticated
    user_id. The router mounts BOTH ``/assets`` AND ``/files/{id}/asset``
    so a single include_router call gets the click-to-render primitive.
    """
    router = APIRouter(prefix=prefix, tags=tags or ["assets"])

    if user_id_dep is None:
        def user_id_dep() -> str:  # noqa: E306
            return "anonymous"

    # ------------------------------------------------------------------
    # GET /assets/presets — preset registry from matrx-utils.
    # ------------------------------------------------------------------
    @router.get("/assets/presets")
    async def list_presets() -> dict[str, Any]:
        from ..specific_handlers.image_handler import PRESETS, SOCIAL_BASELINE
        return {
            "presets": [
                {
                    "name": name,
                    "primary_key": spec["primary_key"],
                    "include_baseline": spec["include_baseline"],
                    "variants": [
                        {"key": v["key"], "width": v["width"], "height": v["height"], "format": v["format"]}
                        for v in spec["variants"]
                    ],
                }
                for name, spec in PRESETS.items()
            ],
            "social_baseline": [
                {"key": v["key"], "width": v["width"], "height": v["height"], "format": v["format"]}
                for v in SOCIAL_BASELINE
            ],
        }

    # ------------------------------------------------------------------
    # POST /assets — upload + render preset variants + bundled options.
    #
    # FE-team A.1: accepts ``options`` form field (JSON-encoded) with:
    #   {
    #     "share": {"permission_level": "read", "expires_at"?: ..., "max_uses"?: ...},
    #     "permissions": [{"grantee_id", "grantee_type"?, "permission_level"}],
    #     "variants": ["thumbnail_256", ...]  // OR ImageVariant dicts
    #   }
    # All sub-ops run after the upload. Failures surface in the
    # response's ``errors[]`` array (best-effort atomic).
    # Idempotency: ``X-Idempotency-Key`` header memoizes the whole
    # bundled response.
    # ------------------------------------------------------------------
    @router.post("/assets")
    async def upload_asset(
        file: UploadFile = File(...),
        preset: str = Form("raw"),
        folder: str | None = Form(None),
        visibility: Literal["public", "private", "shared"] = Form("public"),
        signed_url_ttl: int = Form(3600, ge=60, le=604800),
        metadata_json: str | None = Form(None),
        options_json: str | None = Form(None, description="Bundled share/permissions/variants as JSON"),
        x_idempotency_key: str | None = Header(default=None, alias="X-Idempotency-Key"),
        user_id: str = Depends(user_id_dep),
    ) -> dict:
        try:
            content = await file.read()
            sniffed = sniff_mime_type(
                claimed=file.content_type,
                head_bytes=content[:SNIFF_HEAD_BYTES],
                filename=file.filename,
            )
            parsed_meta: dict[str, Any] | None = None
            if metadata_json:
                try:
                    parsed_meta = json.loads(metadata_json)
                except (json.JSONDecodeError, ValueError) as e:
                    raise HTTPException(400, {"error": "invalid_metadata", "message": str(e)})
            parsed_options: dict[str, Any] = {}
            if options_json:
                try:
                    parsed_options = json.loads(options_json)
                except (json.JSONDecodeError, ValueError) as e:
                    raise HTTPException(400, {"error": "invalid_options", "message": str(e)})

            from pathlib import PurePosixPath
            import uuid
            clean_folder = (folder or f"Assets/{uuid.uuid4()}").strip("/")
            parts = [p for p in PurePosixPath(clean_folder).parts if p not in ("", ".") and p != ".."]
            if not parts:
                parts = ["Assets", str(uuid.uuid4())]
            clean_folder = "/".join(parts)
            file_name = (file.filename or "master").rsplit("/", 1)[-1] or "master"
            master_path = f"{clean_folder}/{file_name}"

            # Determine which variants to render. If preset != "raw" we
            # auto-compose the preset's variant list; the caller can also
            # supply their own list via options.variants.
            variants_to_render = parsed_options.get("variants")
            if not variants_to_render and preset != "raw":
                variants_to_render = [preset]  # let upload_with_options expand it

            # If no bundled sub-ops are requested, the legacy single-op
            # path is fine and faster (skips the IdempotencyStore lookup).
            wants_combined = bool(
                parsed_options or x_idempotency_key or variants_to_render
            )
            if not wants_combined:
                result = await file_service.write(
                    content,
                    file_path=master_path,
                    mime_type=sniffed,
                    visibility=visibility,
                    user_id=user_id,
                    metadata={**(parsed_meta or {}), "asset_master": True, "asset_preset": preset},
                )
                record = await file_service.read_record(result.file_id, user_id=user_id)
                asset = await file_service.build_asset_envelope(
                    record, signed_ttl=signed_url_ttl, preset_name=preset,
                )
                return {"asset": asset.model_dump(), "share_link": None, "errors": []}

            # Combined path — share / permissions / variants in one call.
            return await file_service.upload_with_options(
                content,
                file_path=master_path,
                owner_id=user_id,
                mime_type=sniffed,
                visibility=visibility,
                metadata={**(parsed_meta or {}), "asset_master": True, "asset_preset": preset},
                share=parsed_options.get("share"),
                permissions=parsed_options.get("permissions"),
                variants=variants_to_render,
                preset=preset,
                idempotency_key=x_idempotency_key,
                request_payload_for_idempotency={
                    "preset": preset, "folder": clean_folder, "visibility": visibility,
                    "metadata": parsed_meta, "options": parsed_options,
                },
            )
        except Exception as e:
            raise _map_exc(e)

    # ------------------------------------------------------------------
    # GET /assets/{file_id} — Asset envelope.
    # ------------------------------------------------------------------
    @router.get("/assets/{file_id}", response_model=Asset)
    async def get_asset(
        file_id: str,
        signed_url_ttl: int = Query(3600, ge=60, le=604800),
        user_id: str = Depends(user_id_dep),
    ) -> Asset:
        try:
            record = await file_service.read_record(file_id, user_id=user_id)
            preset_name = (record.get("metadata") or {}).get("asset_preset")
            return await file_service.build_asset_envelope(
                record, signed_ttl=signed_url_ttl, preset_name=preset_name,
            )
        except Exception as e:
            raise _map_exc(e)

    # ------------------------------------------------------------------
    # GET /files/{file_id}/asset — Asset envelope for ANY cld_files row.
    # ------------------------------------------------------------------
    @router.get("/files/{file_id}/asset", response_model=Asset)
    async def get_file_as_asset(
        file_id: str,
        signed_url_ttl: int = Query(3600, ge=60, le=604800),
        user_id: str = Depends(user_id_dep),
    ) -> Asset:
        try:
            record = await file_service.read_record(file_id, user_id=user_id)
            preset_name = (record.get("metadata") or {}).get("asset_preset")
            return await file_service.build_asset_envelope(
                record, signed_ttl=signed_url_ttl, preset_name=preset_name,
            )
        except Exception as e:
            raise _map_exc(e)

    # ------------------------------------------------------------------
    # POST /assets/preview — no-persist preview rendering (FE-team E.16).
    #
    # Accepts a master (MediaRef OR multipart bytes) + variant specs.
    # Returns base64 data URLs for results ≤256 KB, ephemeral 5-min
    # signed URLs otherwise. Replaces the Next.js /api/images/studio/process
    # route on the FE so ``sharp`` can leave the package.json.
    # ------------------------------------------------------------------
    @router.post("/assets/preview")
    async def preview_asset(
        body: _PreviewBody,
        user_id: str = Depends(user_id_dep),
    ) -> dict:
        try:
            results = await file_service.render_preview(
                body.source,
                [spec.model_dump() for spec in body.variants],
                max_inline_bytes=body.max_inline_bytes,
            )
            return {"variants": results}
        except Exception as e:
            raise _map_exc(e)

    # Multipart variant of /assets/preview — upload bytes directly without
    # a prior persistence step. Useful for the Image Studio "drag-and-drop
    # then preview" flow before the user commits to saving.
    @router.post("/assets/preview/multipart")
    async def preview_asset_multipart(
        file: UploadFile = File(...),
        variants_json: str = Form(..., description="JSON-encoded list of _PreviewVariantSpec"),
        max_inline_bytes: int = Form(256 * 1024, ge=1024),
        user_id: str = Depends(user_id_dep),
    ) -> dict:
        try:
            try:
                variants = json.loads(variants_json)
            except (json.JSONDecodeError, ValueError) as e:
                raise HTTPException(400, {"error": "invalid_variants", "message": str(e)})
            content = await file.read()
            results = await file_service.render_preview(
                content,
                variants,
                max_inline_bytes=max_inline_bytes,
            )
            return {"variants": results}
        except Exception as e:
            raise _map_exc(e)

    # ------------------------------------------------------------------
    # POST /assets/pdf-compress — no-persist PDF compression (FE-team E.17).
    # ------------------------------------------------------------------
    @router.post("/assets/pdf-compress")
    async def compress_pdf(
        body: _PdfCompressBody,
        user_id: str = Depends(user_id_dep),
    ) -> dict:
        try:
            return await file_service.compress_pdf(
                body.source,
                level=body.level,
                max_size_bytes=body.max_size_bytes,
                max_inline_bytes=body.max_inline_bytes,
            )
        except Exception as e:
            raise _map_exc(e)

    @router.post("/assets/pdf-compress/multipart")
    async def compress_pdf_multipart(
        file: UploadFile = File(...),
        level: int = Form(3, ge=1, le=5),
        max_size_bytes: int | None = Form(None),
        max_inline_bytes: int = Form(256 * 1024, ge=1024),
        user_id: str = Depends(user_id_dep),
    ) -> dict:
        try:
            content = await file.read()
            return await file_service.compress_pdf(
                content,
                level=level,
                max_size_bytes=max_size_bytes,
                max_inline_bytes=max_inline_bytes,
            )
        except Exception as e:
            raise _map_exc(e)

    return router


__all__ = ["build_asset_router"]
