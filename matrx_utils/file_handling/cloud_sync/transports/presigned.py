"""Presigned-PUT upload state machine.

Two-phase browser-direct upload:

1. ``create`` — server mints a presigned PUT URL + records the pending upload.
2. (Browser PUTs the object straight to S3.)
3. ``finalize`` — server inserts the cld_files row, HEAD-verifies the size,
   runs the same post-upload orchestration as the buffered path.

State today: in-memory dict on the manager instance. Single-process safe;
multi-worker hosts can override :meth:`PresignedManager._put_pending` /
:meth:`PresignedManager._take_pending` with a Redis/DB-backed shim.
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..sync_engine import SyncEngine

logger = logging.getLogger(__name__)


# Pending-entry TTL. Re-runs in finalize and on every create.
_PENDING_TTL_SECONDS = 1800   # 30 min — matches the presigned URL window


# ---------------------------------------------------------------------------
# Errors. Same pattern as TUSSessionManager — host maps to HTTP codes.
# ---------------------------------------------------------------------------


class PresignedError(Exception):
    """Base class for presigned-upload errors."""


class PresignedUnavailable(PresignedError):
    """The configured S3 backend doesn't expose ``get_presigned_put_url``."""


class UploadNotFound(PresignedError):
    """``upload_id`` doesn't match a pending entry (expired or invalid)."""


class OwnerMismatch(PresignedError):
    """The finalize caller is not the user that requested the upload."""


# ---------------------------------------------------------------------------
# Result dataclasses.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PresignedCreateResult:
    upload_id: str
    url: str
    headers: dict[str, str]
    expires_in: int
    file_path: str
    storage_uri: str


@dataclass(frozen=True)
class PresignedFinalizeResult:
    file_id: str
    file_path: str
    storage_uri: str
    size_bytes: int
    checksum: str | None
    version_number: int
    url: str | None
    cdn_url: str | None
    is_new: bool


@dataclass
class _PendingEntry:
    user_id: str
    file_path: str
    storage_uri: str
    content_type: str | None
    visibility: str
    metadata: dict[str, Any] = field(default_factory=dict)
    expected_size: int | None = None
    created_at: float = 0.0


# ---------------------------------------------------------------------------
# Manager.
# ---------------------------------------------------------------------------


class PresignedManager:
    """Presigned PUT upload coordinator.

    Construct via :attr:`SyncEngine.presigned` or directly. The in-memory
    pending-store is the default; subclass + override the two underscore
    methods for a multi-worker shared store (Redis, DB, etc).
    """

    def __init__(self, engine: "SyncEngine") -> None:
        self._engine = engine
        self._pending: dict[str, _PendingEntry] = {}

    # ------------------------------------------------------------------
    # Pending store — override these to swap in a shared backend.
    # ------------------------------------------------------------------

    def _put_pending(self, upload_id: str, entry: _PendingEntry) -> None:
        self._pending[upload_id] = entry

    def _take_pending(self, upload_id: str) -> _PendingEntry | None:
        return self._pending.pop(upload_id, None)

    def _gc(self) -> None:
        cutoff = time.monotonic() - _PENDING_TTL_SECONDS
        for k, v in list(self._pending.items()):
            if v.created_at < cutoff:
                self._pending.pop(k, None)

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    async def create(
        self,
        *,
        owner_id: str,
        file_path: str,
        content_type: str | None = None,
        visibility: str = "private",
        metadata: dict[str, Any] | None = None,
        expected_size_bytes: int | None = None,
        expires_in: int = 900,
    ) -> PresignedCreateResult:
        """Mint a presigned PUT URL + register a pending entry.

        Returns ``(upload_id, url, headers, expires_in, file_path, storage_uri)``.
        The browser PUTs the object to ``url`` with ``headers``; then calls
        :meth:`finalize` with ``upload_id`` to commit the cld_files row.
        """
        router = self._engine.router
        if not router.is_configured("s3"):
            raise PresignedUnavailable("S3 backend is not configured")
        backend = router.s3
        if not hasattr(backend, "get_presigned_put_url"):
            raise PresignedUnavailable(
                "S3 backend does not expose get_presigned_put_url"
            )

        # Visibility-aware bucket selection. Public files go to the
        # CDN-fronted public bucket; private/shared stay on the default.
        from ..cdn import public_bucket
        default_bucket = self._engine.config.resolve_s3_bucket()
        bucket = (
            (public_bucket() or default_bucket)
            if visibility == "public"
            else default_bucket
        )

        storage_uri = f"s3://{bucket}/{owner_id}/{file_path}"
        presigned = backend.get_presigned_put_url(
            f"{bucket}/{owner_id}/{file_path}",
            expires_in=expires_in,
            content_type=content_type,
            max_size_bytes=expected_size_bytes,
        )

        upload_id = str(uuid.uuid4())
        self._put_pending(
            upload_id,
            _PendingEntry(
                user_id=owner_id,
                file_path=file_path,
                storage_uri=storage_uri,
                content_type=content_type,
                visibility=visibility,
                metadata=dict(metadata or {}),
                expected_size=expected_size_bytes,
                created_at=time.monotonic(),
            ),
        )
        self._gc()

        return PresignedCreateResult(
            upload_id=upload_id,
            url=presigned["url"],
            headers=presigned.get("headers") or {},
            expires_in=presigned.get("expires_in") or expires_in,
            file_path=file_path,
            storage_uri=storage_uri,
        )

    # ------------------------------------------------------------------
    # Finalize
    # ------------------------------------------------------------------

    async def finalize(
        self,
        *,
        upload_id: str,
        owner_id: str,
        actual_size_bytes: int | None = None,
        checksum: str | None = None,
        extra_metadata: dict[str, Any] | None = None,
    ) -> PresignedFinalizeResult:
        """Register the uploaded object in cld_files. The bytes are already
        in S3 thanks to the browser PUT.

        The size is HEAD-verified against S3 to defend against client
        misreporting. Folder chain is created via ``ensure_folder_chain``
        so the cld_files row lands with a real ``parent_folder_id``.
        """
        pending = self._take_pending(upload_id)
        if not pending:
            raise UploadNotFound(
                f"No pending upload {upload_id!r} (expired or already finalized)"
            )
        if pending.user_id != owner_id:
            raise OwnerMismatch(
                f"Upload {upload_id!r} was issued for {pending.user_id!r}"
            )

        file_path = pending.file_path
        storage_uri = pending.storage_uri

        # Authoritative size via S3 HEAD; tolerate propagation lag by
        # falling back to the client-reported value.
        actual_size = actual_size_bytes
        router = self._engine.router
        if router.is_configured("s3"):
            try:
                backend = router.s3
                uri_path = storage_uri.split("://", 1)[1]
                obj_bucket, obj_key = backend._parse_path(uri_path)
                head = backend._get_client().head_object(
                    Bucket=obj_bucket, Key=obj_key,
                )
                actual_size = int(head.get("ContentLength") or actual_size or 0)
            except Exception:
                pass

        # Folder chain.
        db = self._engine.db
        client = await db._get_async_client()
        parent_path = "/".join(file_path.split("/")[:-1])
        parent_id: str | None = None
        if parent_path:
            try:
                r = await client.rpc(
                    "ensure_folder_chain",
                    {"p_owner_id": owner_id, "p_folder_path": parent_path},
                ).execute()
                parent_id = r.data if isinstance(r.data, str) else None
            except Exception:
                parent_id = None

        merged_metadata = dict(pending.metadata)
        if extra_metadata:
            for k, v in extra_metadata.items():
                merged_metadata.setdefault(k, v)

        record = await db.upsert_file_async({
            "owner_id": owner_id,
            "file_path": file_path,
            "storage_uri": storage_uri,
            "file_name": file_path.split("/")[-1],
            "mime_type": pending.content_type,
            "size_bytes": actual_size,
            "checksum": checksum,
            "visibility": pending.visibility,
            "parent_folder_id": parent_id,
            "metadata": merged_metadata,
        })

        # URLs from the central minter — same shape as managed_write_async.
        urls = await self._engine.build_urls_for_record_async({
            "visibility": pending.visibility,
            "storage_uri": storage_uri,
            "checksum": checksum,
            "file_name": record.get("file_name") or file_path.rsplit("/", 1)[-1],
            "mime_type": record.get("mime_type"),
            "deleted_at": None,
        })

        return PresignedFinalizeResult(
            file_id=record["id"],
            file_path=file_path,
            storage_uri=storage_uri,
            size_bytes=int(actual_size or 0),
            checksum=checksum,
            version_number=record.get("current_version", 1),
            url=urls.get("url"),
            cdn_url=urls.get("cdn_url"),
            is_new=True,
        )


__all__ = [
    "PresignedManager",
    "PresignedCreateResult",
    "PresignedFinalizeResult",
    "PresignedError",
    "PresignedUnavailable",
    "UploadNotFound",
    "OwnerMismatch",
]
