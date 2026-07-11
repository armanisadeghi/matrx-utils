"""Public share-link resolver router.

Mounted WITHOUT authentication — anyone with a share token can resolve
or download the referenced file. The matrx-utils ``consume_share_link``
RPC enforces expiry / max-uses atomically.

    GET /share/{token}              resolve the link, return file metadata + URL
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, status

from ..service import FileService


def build_share_router(
    file_service: FileService,
    *,
    prefix: str = "/share",
    tags: list[str] | None = None,
) -> APIRouter:
    """Build the public share-link resolver router. No auth required."""
    router = APIRouter(prefix=prefix, tags=tags or ["share"])

    @router.get("/{token}")
    async def resolve_share(token: str) -> dict[str, Any]:
        try:
            link = await file_service.sync_engine.db.increment_share_link_use_async(token)
        except Exception:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                {"error": "internal", "message": "Share link resolution failed"},
            )
        if not link:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                {"error": "share_link_invalid", "message": "Share link invalid, expired, or exhausted"},
            )
        file_id = link.get("resource_id") or link.get("file_id")
        if not file_id:
            return {"share_token": token, "link": link}
        record = await file_service.read_record_unchecked(file_id)
        if not record:
            return {"share_token": token, "link": link}
        urls = await file_service.build_urls(record)
        return {
            "share_token": token,
            "resource_type": link.get("resource_type", "file"),
            "resource_id": file_id,
            "permission_level": link.get("permission_level", "read"),
            "file": {
                "file_id": record["id"],
                "file_path": record["file_path"],
                "file_name": record.get("file_name"),
                "mime_type": record.get("mime_type"),
                "file_size": record.get("file_size"),
                "visibility": record.get("visibility"),
            },
            **urls,
            "expires_at": str(link["expires_at"]) if link.get("expires_at") else None,
            "max_uses": link.get("max_uses"),
            "use_count": link.get("use_count", 0),
        }

    return router


__all__ = ["build_share_router"]
