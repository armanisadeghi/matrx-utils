"""Sync engine — orchestrates cloud upload, database tracking, and versioning.

This is the central component of the cloud sync layer.  It is created by
FileManager when a ``CloudSyncConfig`` is provided, and is called
automatically on every file write/delete operation.

Design goals:
    1. **Transparent** — local operations succeed even if sync fails.
       Sync errors are logged, never raised to the caller (unless using
       the ``managed_*`` methods that explicitly return results).
    2. **Background** — auto-sync on existing FileManager methods runs in
       a daemon thread (sync context) or a background task (async context).
    3. **Full control** — the ``managed_*`` methods give callers a
       ``SyncResult`` with file_id, version, URL, etc.
    4. **Permission-aware** — managed reads/writes check permissions.

Usage::

    # Auto-created by FileManager:
    fm = FileManager("my_app", cloud_sync=CloudSyncConfig(...))

    # Background sync happens on every write:
    fm.write_json("base", "report.json", data)

    # Full control via managed methods:
    result = await fm.managed_write_async("reports/q1.json", data)
    result = await fm.managed_read_async("reports/q1.json")
"""

from __future__ import annotations

import hashlib
import json
import logging
import mimetypes
import threading
import time
import uuid
from posixpath import basename, dirname
from typing import TYPE_CHECKING

from .config import CloudSyncConfig
from .db import DatabaseClient
from .models import SyncResult
from .permissions import PermissionsManager
from .versioning import VersionManager

if TYPE_CHECKING:
    from .download_stream import DownloadStreamer
    from .transports.presigned import PresignedManager
    from .transports.tus import TUSSessionManager
    from .variants_service import VariantsService

logger = logging.getLogger(__name__)


def _stamp_request_id(metadata: dict | None) -> dict:
    """Add ``metadata.request_id`` from the active matrx-utils context.

    Phase 1d.5 (FE REQUESTS item 9). Every cloud_sync write stamps the
    request_id of the inbound HTTP request into the row's ``metadata``
    JSONB. Supabase Realtime then echoes the metadata back to every
    subscriber, including the FE that just issued the write — which uses
    the round-tripped request_id to dedupe its own optimistic state
    from the server broadcast.

    Caller-supplied ``metadata.request_id`` always wins (back-compat +
    explicit override). When no active context is available (background
    jobs, scripts, tests) the field is simply not added.
    """
    out = dict(metadata or {})
    if "request_id" in out:
        return out
    try:
        from matrx_utils.ctx import get_active_context

        ctx = get_active_context()
        rid = getattr(ctx, "request_id", None) if ctx else None
        if rid:
            out["request_id"] = rid
    except Exception:
        # Never let request-id stamping break a real write.
        pass
    return out


class SyncEngine:
    """Orchestrates cloud storage, Postgres metadata, permissions, and versioning."""

    def __init__(self, config: CloudSyncConfig, router: object) -> None:
        self._config = config
        self._router = router  # BackendRouter
        self._db = DatabaseClient(config)
        self.permissions = PermissionsManager(self._db, config.user_id)
        self.versions = VersionManager(self._db, router, config)
        # Lazy: instantiated on first access so a circular import between
        # variants_service and sync_engine can't form.
        self._variants_service: object | None = None
        self._fm_ref: object | None = None  # set by FileManager when wiring

    # ------------------------------------------------------------------
    # Public sub-component accessors. These supersede direct ``_db``,
    # ``_router``, ``_config`` reads from outside this class — callers
    # should use the unprefixed names. The underscore variants are kept
    # for the lifetime of the v1.x line for back-compat.
    # ------------------------------------------------------------------

    @property
    def db(self) -> DatabaseClient:
        """The metadata store. Use ``engine.db.get_file_async(...)`` etc."""
        return self._db

    @property
    def router(self) -> object:
        """The storage gateway (``BackendRouter``). Use for raw bytes reads/writes."""
        return self._router

    @property
    def config(self) -> CloudSyncConfig:
        return self._config

    @property
    def fm(self) -> object:
        """The owning FileManager. Set by FileManager.__init__ via _fm_ref.

        Needed by VariantsService to reach fm.image_handler for the actual
        Pillow encoder. Returns None when the engine was constructed
        outside a FileManager (rare — only test fixtures do this).
        """
        return self._fm_ref

    @property
    def variants(self) -> VariantsService:
        """The idempotent variants engine. See VariantsService docstring."""
        if self._variants_service is None:
            from .variants_service import VariantsService

            self._variants_service = VariantsService(self)
        return self._variants_service  # type: ignore[return-value]

    @property
    def tus(self) -> TUSSessionManager:
        """The TUS resumable-upload state machine. See TUSSessionManager docstring."""
        if not hasattr(self, "_tus_manager") or self._tus_manager is None:
            from .transports.tus import TUSSessionManager

            self._tus_manager = TUSSessionManager(self)
        return self._tus_manager  # type: ignore[return-value]

    @property
    def presigned(self) -> PresignedManager:
        """The presigned-PUT upload coordinator. Two-phase create + finalize."""
        if not hasattr(self, "_presigned_manager") or self._presigned_manager is None:
            from .transports.presigned import PresignedManager

            self._presigned_manager = PresignedManager(self)
        return self._presigned_manager  # type: ignore[return-value]

    @property
    def streamer(self) -> DownloadStreamer:
        """Range-aware download streamer. Picks S3 chunked vs buffered."""
        if not hasattr(self, "_streamer") or self._streamer is None:
            from .download_stream import DownloadStreamer

            self._streamer = DownloadStreamer(self)
        return self._streamer  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Authorized record fetch — the public primitive every router /
    # service should use instead of ``engine._db.get_file_async(id)``
    # followed by an inlined ``_require_access`` block. Returns the
    # cld_files row only after the access check passes; raises
    # ``PermissionError`` on denial and ``FileNotFoundError`` on miss.
    # ------------------------------------------------------------------

    async def get_authorized_record_async(
        self,
        file_id: str,
        *,
        user_id: str,
        level: str = "read",
    ) -> dict:
        """Load a file row and enforce access in one call.

        ``level`` is ``"read" | "write" | "admin"``. Raises ``FileNotFoundError``
        if the row is missing, ``PermissionError`` if the caller lacks access.

        The ONLY inline rule is the owner fast-path — it is the first rule of the
        DB policy too (``iam.has_access_for``) and cannot diverge without the
        whole ownership model changing, so it saves a round-trip on the hot path.
        EVERYTHING else (visibility tiers, org access, grants, memberships,
        reachability, super-admin) is decided by ``PermissionsManager``, which
        defers to the one authoritative DB policy. Do NOT re-add a `visibility`
        shortcut here: visibility is a 4-level ladder (private < internal < link
        < public) and duplicating its semantics is exactly how the two
        implementations drifted apart before.
        """
        record = await self._db.get_file_async(file_id)
        if not record:
            raise FileNotFoundError(f"File {file_id!r} not found")
        if user_id and record.get("owner_id") == user_id:
            return record
        await self.permissions.require_async("file", record["id"], level, user_id)
        return record

    # ------------------------------------------------------------------
    # User context (for per-request user switching in web apps)
    # ------------------------------------------------------------------

    def set_user(self, user_id: str) -> None:
        """Switch the active user (call per-request in FastAPI)."""
        self._config = CloudSyncConfig(
            user_id=user_id,
            s3_bucket=self._config.s3_bucket,
            storage_backend=self._config.storage_backend,
            supabase_url=self._config.supabase_url,
            supabase_key=self._config.supabase_key,
            auto_sync=self._config.auto_sync,
            version_storage_prefix=self._config.version_storage_prefix,
            database_url=self._config.database_url,
        )
        self.permissions.user_id = user_id

    @property
    def user_id(self) -> str:
        return self._config.user_id

    @property
    def auto_sync(self) -> bool:
        return self._config.auto_sync

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_user_id(self, explicit: str | None) -> str:
        """Resolve user_id with three-level priority:

        1. Explicitly passed ``user_id`` argument (highest — per-call override).
        2. ``CloudSyncConfig.user_id`` baked in at construction time.
        3. Active request context via ``matrx_utils.ctx.get_active_user_id()``
           (set automatically by middleware in web apps that called
           ``configure_context()``).

        Returns ``""`` if none of the above is set.
        """
        if explicit:
            return explicit
        if self._config.user_id:
            return self._config.user_id
        from matrx_utils.ctx import get_active_user_id

        return get_active_user_id()

    def _storage_uri(
        self,
        file_path: str,
        user_id: str | None = None,
        *,
        visibility: str = "private",
    ) -> str:
        """Build the canonical cloud storage URI for a file path.

        Public files (``visibility="public"``) live in a dedicated
        public S3 bucket whose name equals the CDN host (configured
        via ``AWS_S3_PUBLIC_BUCKET`` + ``CDN_PUBLIC_BASE_URL``). When
        the CDN feature is unconfigured the public bucket falls back
        to the default bucket (single-bucket dev).
        Private/shared files always use the default bucket.
        """
        from .cdn import public_bucket

        uid = self._resolve_user_id(user_id)
        backend = self._config.storage_backend
        if visibility == "public":
            bucket = public_bucket() or self._config.resolve_s3_bucket()
        else:
            bucket = self._config.resolve_s3_bucket()
        return f"{backend}://{bucket}/{uid}/{file_path}"

    @staticmethod
    def _checksum(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    # ==================================================================
    # URL MINTING — centralized. ALL callers (routers, services, scripts)
    # use these helpers; nothing else may import cdn.public_url_for or
    # call _router.get_url_async directly on a record's storage_uri.
    # ==================================================================

    # Default signed-URL TTL (1 hour). Callers can override per-call.
    DEFAULT_SIGNED_TTL = 3600

    @staticmethod
    def _content_disposition(file_name: str | None, disposition: str) -> str:
        """Build an RFC 6266 Content-Disposition value with safe quoting.

        ``disposition`` is "inline" or "attachment". File names with
        non-ASCII characters use the ``filename*=UTF-8''<pct-encoded>``
        extended form.
        """
        from urllib.parse import quote as _quote

        name = file_name or "download"
        try:
            name.encode("ascii")
            return f'{disposition}; filename="{name}"'
        except UnicodeEncodeError:
            ascii_fallback = name.encode("ascii", "replace").decode("ascii")
            return (
                f'{disposition}; filename="{ascii_fallback}"; '
                f"filename*=UTF-8''{_quote(name, safe='')}"
            )

    def build_urls_for_record(
        self,
        record_or_synthetic: dict,
        *,
        signed_ttl: int | None = None,
    ) -> dict:
        """Mint every URL flavour the platform supports for a file.

        ``record_or_synthetic`` is either a real ``cld_files`` row (dict
        as returned by ``DatabaseClient.get_file_async``) OR a synthetic
        dict assembled from a ``SyncResult`` for just-written files
        (must carry at minimum: ``storage_uri``, ``visibility``, optional
        ``checksum``, ``file_name``, ``mime_type``, ``deleted_at``).

        Returns ``{url, cdn_url, signed_url, download_url, signed_url_expires_at}``.

        ``signed_url_expires_at`` is the ms-epoch when ``signed_url``
        becomes invalid (computed from ``ttl`` at mint time). ``None``
        when no signed URL was minted (CDN-only public files).

        Soft-deleted records yield all-None values. CDN-disabled
        deployments simply return ``cdn_url=None``; ``url`` then becomes
        the signed-inline URL.

        Sync entry point — performs blocking presigned-URL generation.
        Use ``build_urls_for_record_async`` from FastAPI routes.
        """
        ttl = signed_ttl or self.DEFAULT_SIGNED_TTL
        empty = {
            "url": None,
            "cdn_url": None,
            "signed_url": None,
            "download_url": None,
            "signed_url_expires_at": None,
        }
        if not record_or_synthetic:
            return empty
        if record_or_synthetic.get("deleted_at"):
            return empty
        from .cdn import public_url_for

        cdn_url = public_url_for(record_or_synthetic)
        # Prefer canonical_storage_uri when set — the row is either born
        # canonical (new uploads with file_id pinned) OR rekey has copied
        # the bytes to <owner>/<file_id>. Either way, canonical carries
        # file_id in the path. Falls back to storage_uri for legacy rows
        # whose rekey hasn't run yet.
        storage_uri = record_or_synthetic.get("canonical_storage_uri") or record_or_synthetic.get(
            "storage_uri"
        )
        if not storage_uri:
            return {**empty, "cdn_url": cdn_url, "url": cdn_url}
        file_name = record_or_synthetic.get("file_name")
        mime_type = record_or_synthetic.get("mime_type")
        try:
            signed_inline = self._router.get_url(
                storage_uri,
                expires_in=ttl,
                response_content_disposition=self._content_disposition(file_name, "inline"),
                response_content_type=mime_type,
            )
        except Exception:
            logger.debug("build_urls_for_record: signed_inline failed", exc_info=True)
            signed_inline = None
        try:
            download_url = self._router.get_url(
                storage_uri,
                expires_in=ttl,
                response_content_disposition=self._content_disposition(file_name, "attachment"),
                response_content_type=mime_type,
            )
        except Exception:
            logger.debug("build_urls_for_record: download_url failed", exc_info=True)
            download_url = signed_inline
        signed_url_expires_at = int((time.time() + ttl) * 1000) if signed_inline else None
        return {
            "url": cdn_url or signed_inline,
            "cdn_url": cdn_url,
            "signed_url": signed_inline,
            "download_url": download_url or signed_inline,
            "signed_url_expires_at": signed_url_expires_at,
        }

    async def build_urls_for_record_async(
        self,
        record_or_synthetic: dict,
        *,
        signed_ttl: int | None = None,
    ) -> dict:
        """Async version of ``build_urls_for_record``.

        Returns ``{url, cdn_url, signed_url, download_url, signed_url_expires_at}``.
        ``signed_url_expires_at`` is the ms-epoch when ``signed_url``
        becomes invalid (computed from ``ttl`` at mint time). ``None``
        when no signed URL was minted (CDN-only public files).
        """
        ttl = signed_ttl or self.DEFAULT_SIGNED_TTL
        empty = {
            "url": None,
            "cdn_url": None,
            "signed_url": None,
            "download_url": None,
            "signed_url_expires_at": None,
        }
        if not record_or_synthetic:
            return empty
        if record_or_synthetic.get("deleted_at"):
            return empty
        from .cdn import public_url_for

        cdn_url = public_url_for(record_or_synthetic)
        # Prefer canonical_storage_uri when set — the row is either born
        # canonical (new uploads with file_id pinned) OR rekey has copied
        # the bytes to <owner>/<file_id>. Either way, canonical carries
        # file_id in the path. Falls back to storage_uri for legacy rows
        # whose rekey hasn't run yet.
        storage_uri = record_or_synthetic.get("canonical_storage_uri") or record_or_synthetic.get(
            "storage_uri"
        )
        if not storage_uri:
            return {**empty, "cdn_url": cdn_url, "url": cdn_url}
        file_name = record_or_synthetic.get("file_name")
        mime_type = record_or_synthetic.get("mime_type")
        try:
            signed_inline = await self._router.get_url_async(
                storage_uri,
                expires_in=ttl,
                response_content_disposition=self._content_disposition(file_name, "inline"),
                response_content_type=mime_type,
            )
        except Exception:
            logger.debug("build_urls_for_record_async: signed_inline failed", exc_info=True)
            signed_inline = None
        try:
            download_url = await self._router.get_url_async(
                storage_uri,
                expires_in=ttl,
                response_content_disposition=self._content_disposition(file_name, "attachment"),
                response_content_type=mime_type,
            )
        except Exception:
            logger.debug("build_urls_for_record_async: download_url failed", exc_info=True)
            download_url = signed_inline
        signed_url_expires_at = int((time.time() + ttl) * 1000) if signed_inline else None
        return {
            "url": cdn_url or signed_inline,
            "cdn_url": cdn_url,
            "signed_url": signed_inline,
            "download_url": download_url or signed_inline,
            "signed_url_expires_at": signed_url_expires_at,
        }

    @staticmethod
    def _to_bytes(content: object) -> bytes:
        """Convert content to bytes for upload and checksum."""
        if isinstance(content, bytes):
            return content
        if isinstance(content, str):
            return content.encode("utf-8")
        if isinstance(content, (dict, list)):
            return json.dumps(content, indent=2, default=str).encode("utf-8")
        if isinstance(content, memoryview):
            return bytes(content)
        return str(content).encode("utf-8")

    @staticmethod
    def _guess_mime(file_path: str) -> str | None:
        mime, _ = mimetypes.guess_type(file_path)
        return mime

    def _resolve_write_organization_id(
        self, user_id: str, organization_id: str | None = None
    ) -> str | None:
        if organization_id:
            return organization_id
        try:
            return self._db.ensure_personal_organization(user_id)
        except Exception:
            logger.error(
                "personal-org resolution failed for owner %s — folder write will "
                "violate organization_id NOT NULL. Investigate "
                "ensure_personal_organization / org membership.",
                user_id,
                exc_info=True,
            )
            return None

    async def _resolve_write_organization_id_async(
        self, user_id: str, organization_id: str | None = None
    ) -> str | None:
        if organization_id:
            return organization_id
        try:
            return await self._db.ensure_personal_organization_async(user_id)
        except Exception:
            logger.error(
                "personal-org resolution failed for owner %s — folder write will "
                "violate organization_id NOT NULL. Investigate "
                "ensure_personal_organization / org membership.",
                user_id,
                exc_info=True,
            )
            return None

    def _ensure_folder(
        self,
        file_path: str,
        user_id: str,
        organization_id: str | None = None,
    ) -> str | None:
        """Ensure the parent folder exists in the database, return its id."""
        folder_path = dirname(file_path)
        if not folder_path or folder_path == ".":
            return None

        existing = self._db.get_folder_by_path(user_id, folder_path)
        if existing:
            return existing["id"]

        org_id = organization_id or self._resolve_write_organization_id(user_id)

        # Ensure parent folders recursively
        parent_id = self._ensure_folder(folder_path, user_id, org_id)
        folder_name = basename(folder_path)

        result = self._db.upsert_folder(
            {
                "owner_id": user_id,
                "folder_path": folder_path,
                "folder_name": folder_name,
                "parent_id": parent_id,
                "organization_id": org_id,
            }
        )
        return result["id"]

    async def _ensure_folder_async(
        self,
        file_path: str,
        user_id: str,
        organization_id: str | None = None,
    ) -> str | None:
        folder_path = dirname(file_path)
        if not folder_path or folder_path == ".":
            return None

        existing = await self._db.get_folder_by_path_async(user_id, folder_path)
        if existing:
            return existing["id"]

        org_id = organization_id or await self._resolve_write_organization_id_async(user_id)

        parent_id = await self._ensure_folder_async(folder_path, user_id, org_id)
        folder_name = basename(folder_path)

        result = await self._db.upsert_folder_async(
            {
                "owner_id": user_id,
                "folder_path": folder_path,
                "folder_name": folder_name,
                "parent_id": parent_id,
                "organization_id": org_id,
            }
        )
        return result["id"]

    # ==================================================================
    # AUTO-SYNC — called by FileManager after local operations
    # ==================================================================

    def track_write(
        self,
        file_path: str,
        content: bytes | str | dict | list,
        mime_type: str | None = None,
        user_id: str | None = None,
    ) -> None:
        """Upload to cloud and record in database.  Fire-and-forget."""
        try:
            uid = self._resolve_user_id(user_id)
            content_bytes = self._to_bytes(content)
            storage_uri = self._storage_uri(file_path, uid)

            # Upload to cloud — stamp Content-Type so a bare public URL renders
            # inline (canonical keys are extensionless; pass the mime explicitly).
            self._router.write(
                storage_uri,
                content_bytes,
                content_type=mime_type or self._guess_mime(file_path),
            )

            # Ensure folder structure
            folder_id = self._ensure_folder(file_path, uid)

            # Compute metadata
            checksum = self._checksum(content_bytes)
            mime = mime_type or self._guess_mime(file_path)

            # Check if file exists
            existing = self._db.get_file_by_path(uid, file_path)
            if existing:
                new_version = existing["current_version"] + 1
                self._db.update_file(
                    existing["id"],
                    {
                        "storage_uri": storage_uri,
                        "size_bytes": len(content_bytes),
                        "checksum": checksum,
                        "mime_type": mime,
                        "current_version": new_version,
                        "parent_folder_id": folder_id,
                    },
                )
                file_record = {**existing, "current_version": new_version}
            else:
                file_record = self._db.upsert_file(
                    {
                        "owner_id": uid,
                        "file_path": file_path,
                        "storage_uri": storage_uri,
                        "file_name": basename(file_path),
                        "mime_type": mime,
                        "size_bytes": len(content_bytes),
                        "checksum": checksum,
                        "parent_folder_id": folder_id,
                    }
                )

            # Record version
            self.versions.record_version(file_record, content_bytes, checksum=checksum, user_id=uid)

            logger.debug("Synced write: %s → %s", file_path, storage_uri)

        except Exception:
            logger.warning("Cloud sync failed for '%s'", file_path, exc_info=True)

    async def track_write_async(
        self,
        file_path: str,
        content: bytes | str | dict | list,
        mime_type: str | None = None,
        user_id: str | None = None,
    ) -> None:
        """Async version of track_write()."""
        try:
            uid = self._resolve_user_id(user_id)
            content_bytes = self._to_bytes(content)
            storage_uri = self._storage_uri(file_path, uid)

            await self._router.write_async(
                storage_uri,
                content_bytes,
                content_type=mime_type or self._guess_mime(file_path),
            )

            folder_id = await self._ensure_folder_async(file_path, uid)
            checksum = self._checksum(content_bytes)
            mime = mime_type or self._guess_mime(file_path)

            existing = await self._db.get_file_by_path_async(uid, file_path)
            if existing:
                new_version = existing["current_version"] + 1
                await self._db.update_file_async(
                    existing["id"],
                    {
                        "storage_uri": storage_uri,
                        "size_bytes": len(content_bytes),
                        "checksum": checksum,
                        "mime_type": mime,
                        "current_version": new_version,
                        "parent_folder_id": folder_id,
                    },
                )
                file_record = {**existing, "current_version": new_version}
            else:
                file_record = await self._db.upsert_file_async(
                    {
                        "owner_id": uid,
                        "file_path": file_path,
                        "storage_uri": storage_uri,
                        "file_name": basename(file_path),
                        "mime_type": mime,
                        "size_bytes": len(content_bytes),
                        "checksum": checksum,
                        "parent_folder_id": folder_id,
                    }
                )

            await self.versions.record_version_async(
                file_record, content_bytes, checksum=checksum, user_id=uid
            )

            logger.debug("Synced write: %s → %s", file_path, storage_uri)

        except Exception:
            logger.warning("Cloud sync failed for '%s'", file_path, exc_info=True)

    def track_delete(self, file_path: str, user_id: str | None = None) -> None:
        """Soft-delete in database and optionally remove from cloud."""
        try:
            uid = self._resolve_user_id(user_id)
            existing = self._db.get_file_by_path(uid, file_path)
            if existing:
                self._db.soft_delete_file(existing["id"])
                logger.debug("Synced delete: %s", file_path)
        except Exception:
            logger.warning("Cloud sync delete failed for '%s'", file_path, exc_info=True)

    async def track_delete_async(self, file_path: str, user_id: str | None = None) -> None:
        try:
            uid = self._resolve_user_id(user_id)
            existing = await self._db.get_file_by_path_async(uid, file_path)
            if existing:
                await self._db.soft_delete_file_async(existing["id"])
                logger.debug("Synced delete: %s", file_path)
        except Exception:
            logger.warning("Cloud sync delete failed for '%s'", file_path, exc_info=True)

    def fire_and_forget_write(
        self,
        file_path: str,
        content: bytes | str | dict | list,
        mime_type: str | None = None,
        user_id: str | None = None,
    ) -> None:
        """Run track_write in a background daemon thread.

        Captures the current ContextVar context BEFORE spawning the
        thread so the worker thread sees the same active user. Without
        this, ContextVars revert to defaults inside the thread and the
        sync would write under user_id="" (H17 fix).
        """
        if user_id is None:
            user_id = self._resolve_user_id(None) or None

        import contextvars

        ctx = contextvars.copy_context()

        def _runner():
            ctx.run(self.track_write, file_path, content, mime_type=mime_type, user_id=user_id)

        t = threading.Thread(target=_runner, daemon=True)
        t.start()

    def fire_and_forget_delete(self, file_path: str, user_id: str | None = None) -> None:
        """Run track_delete in a background daemon thread.

        Same context-capture pattern as fire_and_forget_write.
        """
        if user_id is None:
            user_id = self._resolve_user_id(None) or None

        import contextvars

        ctx = contextvars.copy_context()

        def _runner():
            ctx.run(self.track_delete, file_path, user_id=user_id)

        t = threading.Thread(target=_runner, daemon=True)
        t.start()

    # ==================================================================
    # MANAGED OPERATIONS — full control with permission checks
    # ==================================================================

    def managed_write(
        self,
        file_path: str,
        content: bytes | str | dict | list,
        *,
        mime_type: str | None = None,
        visibility: str = "private",
        share_with: list[str] | None = None,
        share_level: str = "read",
        change_summary: str | None = None,
        user_id: str | None = None,
        metadata: dict | None = None,
    ) -> SyncResult:
        """Write a file to cloud with full metadata, versioning, and permissions.

        Unlike the auto-sync methods, this returns a ``SyncResult`` and
        raises on errors rather than swallowing them.
        """
        uid = self._resolve_user_id(user_id)
        content_bytes = self._to_bytes(content)
        storage_uri = self._storage_uri(file_path, uid, visibility=visibility)

        # Upload to cloud — stamp Content-Type so a bare public URL renders inline.
        self._router.write(
            storage_uri,
            content_bytes,
            content_type=mime_type or self._guess_mime(file_path),
        )

        # Ensure folder structure
        folder_id = self._ensure_folder(file_path, uid)

        # Compute metadata
        checksum = self._checksum(content_bytes)
        mime = mime_type or self._guess_mime(file_path)

        # Check if file exists
        existing = self._db.get_file_by_path(uid, file_path)
        is_new = existing is None

        # Phase 1d.5 — stamp request_id into metadata for realtime dedup.
        effective_metadata = _stamp_request_id(
            metadata or (existing.get("metadata", {}) if existing else {})
        )

        if existing:
            # Permission check for updates on files owned by others
            if existing["owner_id"] != uid:
                self.permissions.require("file", existing["id"], "write", uid)
            new_version = existing["current_version"] + 1
            self._db.update_file(
                existing["id"],
                {
                    "storage_uri": storage_uri,
                    "size_bytes": len(content_bytes),
                    "checksum": checksum,
                    "mime_type": mime,
                    "current_version": new_version,
                    "visibility": visibility,
                    "parent_folder_id": folder_id,
                    "metadata": effective_metadata,
                },
            )
            file_record = {**existing, "current_version": new_version, "id": existing["id"]}
        else:
            file_record = self._db.upsert_file(
                {
                    "owner_id": uid,
                    "file_path": file_path,
                    "storage_uri": storage_uri,
                    # canonical_storage_uri intentionally not written — migration
                    # 007 consolidates it into storage_uri. See managed_write_async.
                    "file_name": basename(file_path),
                    "mime_type": mime,
                    "size_bytes": len(content_bytes),
                    "checksum": checksum,
                    "visibility": visibility,
                    "parent_folder_id": folder_id,
                    "metadata": effective_metadata,
                }
            )

        # Record version
        self.versions.record_version(
            file_record,
            content_bytes,
            checksum=checksum,
            change_summary=change_summary,
            user_id=uid,
        )

        # Grant permissions to shared users
        if share_with:
            for grantee_id in share_with:
                self._db.upsert_permission(
                    {
                        "resource_id": file_record["id"],
                        "resource_type": "file",
                        "grantee_id": grantee_id,
                        "grantee_type": "user",
                        "permission_level": share_level,
                        "granted_by": uid,
                    }
                )
            # Canonical sharing model: specific-user access is granted by the
            # iam.permissions rows above (RLS via iam.has_access), NOT by
            # elevating ambient visibility. The file stays 'private' — the
            # legacy 'shared' visibility no longer exists (the platform.visibility
            # enum is private<internal<link<public), and elevating to 'link'
            # would widen access to anyone-with-link. build_urls already mints
            # signed URLs for every non-public file, so URLs are unaffected.

        # Mint every URL flavour via the central helper (CDN if public,
        # signed-inline + signed-download for private/shared).
        synthetic = {
            "storage_uri": storage_uri,
            "visibility": visibility,
            "checksum": checksum,
            "file_name": basename(file_path),
            "mime_type": mime,
            "deleted_at": None,
        }
        urls = self.build_urls_for_record(synthetic)

        return SyncResult(
            file_id=file_record["id"],
            storage_uri=storage_uri,
            version_number=file_record.get("current_version", 1),
            size_bytes=len(content_bytes),
            checksum=checksum,
            is_new=is_new,
            visibility=visibility,
            url=urls["url"],
            cdn_url=urls["cdn_url"],
            signed_url=urls["signed_url"],
            download_url=urls["download_url"],
            signed_url_expires_at=urls.get("signed_url_expires_at"),
            parent_file_id=file_record.get("parent_file_id"),
            derivation_kind=file_record.get("derivation_kind"),
        )

    @staticmethod
    def _is_dedup_unique_violation(exc: BaseException) -> bool:
        """True if ``exc`` is a Postgres 23505 on the dedup canonical index.

        Race fallback: between our checksum lookup and the INSERT, another
        concurrent write of the same content can win the canonical slot.
        The DB-level unique index (migration 0065,
        ``cld_files_dedup_canonical``) rejects the loser. Detect that
        specific case so we can recover gracefully; any other violation
        (e.g. ``owner_id, file_path`` collision) bubbles up as a real bug.
        """
        msg = str(exc).lower()
        # Match postgrest 23505 / asyncpg UniqueViolationError surfaces.
        if "23505" not in msg and "unique" not in msg:
            return False
        return "cld_files_dedup_canonical" in msg

    @staticmethod
    def _is_path_unique_violation(exc: BaseException) -> bool:
        """True if ``exc`` is a Postgres 23505 on the (owner_id, file_path) key.

        Race fallback for pinned-id inserts (TUS / AI media / variants):
        between our ``get_file_by_path`` lookup and the INSERT, a concurrent
        write to the SAME ``(owner_id, file_path)`` can win the slot. The
        canonical example is two variant-render passes for the same master
        (content-dedup merges two saves of identical bytes into one master,
        so both passes render ``system-files/variants/<master>/og.jpg``).
        Now that pinned-id inserts are plain inserts (never an
        ``ON CONFLICT DO UPDATE`` that would rewrite the winner's primary
        key), the loser raises this violation and recovers by reading the
        winning row — converging on one variant instead of corrupting the
        winner's id and orphaning its cld_file_versions insert (FK 23503).
        """
        msg = str(exc).lower()
        if "23505" not in msg and "unique" not in msg and "duplicate key" not in msg:
            return False
        return (
            "cld_files_owner_id_file_path_key" in msg
            or "owner_id, file_path" in msg
            or "owner_id,file_path" in msg
        )

    async def _sync_result_for_existing_async(
        self,
        *,
        existing_row: dict,
        content_bytes: bytes,
        checksum: str,
        visibility: str,
        share_with: list[str] | None,
        share_level: str,
        granter_uid: str,
    ) -> SyncResult:
        """Build a SyncResult for an already-canonical row (dedup hit).

        No bytes are written to S3; the existing storage_uri is reused
        verbatim. Caller-supplied ``share_with`` grants are still applied
        so a caller that expected "upload + share with X" still gets the
        share. Bytes are pushed into the in-process byte cache so the
        typical "upload then immediately use" flow doesn't refetch from
        S3 — they're in hand right now.
        """
        existing_id = str(existing_row["id"])

        if share_with:
            for grantee_id in share_with:
                await self._db.upsert_permission_async(
                    {
                        "resource_id": existing_id,
                        "resource_type": "file",
                        "grantee_id": grantee_id,
                        "grantee_type": "user",
                        "permission_level": share_level,
                        "granted_by": granter_uid,
                    }
                )
            # Specific-user access comes from the iam.permissions rows above
            # (RLS via iam.has_access); ambient visibility stays as-is. The
            # legacy 'shared' visibility was removed (enum: private<internal<
            # link<public) and is never written.

        urls = await self.build_urls_for_record_async(existing_row)

        try:
            from matrx_utils.file_handling.cloud_sync.byte_cache import get_byte_cache

            get_byte_cache().put(
                existing_id,
                bytes_=content_bytes,
                mime_type=existing_row.get("mime_type"),
                owner_id=str(existing_row.get("owner_id") or granter_uid),
                file_path=existing_row.get("file_path"),
            )
        except Exception:
            logger.debug("byte cache populate failed (dedup alias)", exc_info=True)

        storage_uri = existing_row.get("canonical_storage_uri") or existing_row.get("storage_uri")
        return SyncResult(
            file_id=existing_id,
            storage_uri=storage_uri,
            version_number=int(existing_row.get("current_version") or 1),
            size_bytes=len(content_bytes),
            checksum=checksum,
            is_new=False,
            visibility=existing_row.get("visibility") or visibility,
            url=urls["url"],
            cdn_url=urls["cdn_url"],
            signed_url=urls["signed_url"],
            download_url=urls["download_url"],
            signed_url_expires_at=urls.get("signed_url_expires_at"),
            parent_file_id=existing_row.get("parent_file_id"),
            derivation_kind=existing_row.get("derivation_kind"),
        )

    async def managed_write_async(
        self,
        file_path: str,
        content: bytes | str | dict | list,
        *,
        mime_type: str | None = None,
        visibility: str = "private",
        share_with: list[str] | None = None,
        share_level: str = "read",
        change_summary: str | None = None,
        user_id: str | None = None,
        metadata: dict | None = None,
        file_id: str | None = None,
        parent_file_id: str | None = None,
        derivation_kind: str | None = None,
    ) -> SyncResult:
        """Async version of managed_write().

        When ``file_id`` is supplied the row id AND the S3 key are pinned
        to that UUID — the S3 key becomes ``<owner_id>/<file_id>`` (the
        canonical scheme) instead of ``<owner_id>/<file_path>``. This
        skips the legacy-then-rekey dance entirely: ``storage_uri`` and
        ``canonical_storage_uri`` both equal the canonical URI from day
        one, and any URL minted from the row carries the file_id in its
        path. Use this when the caller already owns a stable file_id
        (TUS, AI-generated media, anything fresh) — leave ``file_id``
        unset for the legacy path-based scheme (back-compat for routes
        that update an existing row by ``(owner_id, file_path)``).

        Dedup (Phase 1, migration 0065): brand-new ROOT inserts
        (no existing row at this ``file_path``, no ``parent_file_id``)
        consult the content-hash dedup table first. A scope-matching
        hit short-circuits — no S3 write, no INSERT, returns the
        canonical row's SyncResult with ``is_new=False``. Implicit
        alias_existing semantics for back-compat with the thousands of
        legacy callers; the strict-intent variants (create / force_new)
        live on ``FileService.upload_with_intent``. Derivative writes
        (parent_file_id set) skip dedup — variants of the same master
        are intentionally separate rows.
        """
        uid = self._resolve_user_id(user_id)
        content_bytes = self._to_bytes(content)
        checksum = self._checksum(content_bytes)
        mime = mime_type or self._guess_mime(file_path)

        # Path-keyed lookup: preserves the legacy "save over an existing
        # file at this path" semantics (new version, in-place update).
        # Has to come BEFORE the dedup check so a caller updating a file
        # with the same content as another file in the scope doesn't get
        # silently redirected to that other file.
        existing = await self._db.get_file_by_path_async(uid, file_path)
        is_new = existing is None

        # Content-hash dedup short-circuit — runs only for brand-new
        # ROOT inserts. Derivatives bypass: variants of the same master
        # can legitimately share a checksum (asset variant thumbnails are
        # byte-identical when source images are identical; rendered
        # blank pages from different PDFs are byte-identical), and the
        # post-write lineage promotion pattern (see
        # services/documents/page_image.py, page_pdf_attachments.py,
        # routers/pdf_processing.py) depends on getting a FRESH row id
        # back from the write.
        #
        # Three derivative-detection signals — any one bypasses dedup:
        #   1. parent_file_id kwarg (newer call convention)
        #   2. derivation_kind kwarg (same convention)
        #   3. parent_file_id or derivation_kind smuggled in metadata
        #      (legacy "write then UPDATE" promotion pattern — kept
        #      working without forcing every caller to migrate)
        metadata_dict = metadata or {}
        # Org resolution (K0-1 / platform invariant): every cld_files row must
        # carry a non-NULL organization_id. The caller may pass one explicitly
        # (metadata.organization_id, or nested under metadata.scope from the FE
        # handler); otherwise we default to the owner's personal org. If
        # resolution fails we fall back to whatever was provided (possibly None)
        # and log loudly rather than break the write — "loud recovery".
        scope_dict = (
            metadata_dict.get("scope") if isinstance(metadata_dict.get("scope"), dict) else {}
        )
        org_id_for_dedup = metadata_dict.get("organization_id") or (
            scope_dict.get("organization_id") if scope_dict else None
        )
        if not org_id_for_dedup:
            try:
                org_id_for_dedup = await self._db.ensure_personal_organization_async(uid)
            except Exception:
                logger.error(
                    "personal-org resolution failed for owner %s — writing file "
                    "with NULL organization_id (invariant violated). Investigate "
                    "ensure_personal_organization / org membership.",
                    uid,
                    exc_info=True,
                )
                org_id_for_dedup = None
        is_derivative_write = (
            parent_file_id is not None
            or derivation_kind is not None
            or metadata_dict.get("parent_file_id") is not None
            or metadata_dict.get("derivation_kind") is not None
        )
        if is_new and not is_derivative_write and checksum:
            from matrx_utils.file_handling.dedup import lookup_existing_async

            dedup_lookup = await lookup_existing_async(
                self._db,
                checksum=checksum,
                owner_id=uid,
                organization_id=org_id_for_dedup,
            )
            if dedup_lookup.has_duplicate and dedup_lookup.existing is not None:
                return await self._sync_result_for_existing_async(
                    existing_row=dedup_lookup.existing,
                    content_bytes=content_bytes,
                    checksum=checksum,
                    visibility=visibility,
                    share_with=share_with,
                    share_level=share_level,
                    granter_uid=uid,
                )

        # Resolve the canonical row id / S3 key.
        #   - caller-supplied file_id  → pin to it (TUS, AI media).
        #   - brand-new insert (is_new) → mint a fresh UUID and use the
        #     canonical <owner>/<file_id> key. CRITICAL (P0-2): the old
        #     path-derived key <owner>/<file_path> let two concurrent NEW
        #     uploads to the SAME path target the SAME S3 object — the
        #     second PUT overwrote the first's bytes, then lost the
        #     (owner_id, file_path) INSERT race, leaving the first row
        #     pointing at the second's bytes (silent corruption). A
        #     per-write UUID key makes every concurrent writer target a
        #     distinct object; the loser's INSERT still fails cleanly and
        #     its orphan object is cleaned up below.
        #   - existing-version update  → keep the legacy path-derived key
        #     so in-place version overwrites keep their established URI.
        effective_file_id: str | None
        if file_id is not None:
            effective_file_id = file_id
        elif is_new:
            effective_file_id = str(uuid.uuid4())
        else:
            effective_file_id = None

        if effective_file_id is not None:
            backend = self._config.storage_backend
            from .cdn import public_bucket

            bucket = (
                (public_bucket() or self._config.resolve_s3_bucket())
                if visibility == "public"
                else self._config.resolve_s3_bucket()
            )
            storage_uri = f"{backend}://{bucket}/{uid}/{effective_file_id}"
        else:
            # Version update of an existing row (existing is not None here):
            # overwrite the SAME object the row already references. Do NOT
            # recompute a path key — the row may have been created with a
            # canonical <owner>/<file_id> key, and recomputing would rekey it
            # to a path key, orphaning the canonical object and churning the URI.
            storage_uri = (
                existing.get("canonical_storage_uri")
                or existing.get("storage_uri")
                or self._storage_uri(file_path, uid, visibility=visibility)
            )

        # mime computed above (mime_type or guessed). Stamp it onto the object so
        # the canonical extensionless <owner>/<file_id> key still renders inline.
        await self._router.write_async(storage_uri, content_bytes, content_type=mime)

        folder_id = await self._ensure_folder_async(file_path, uid, org_id_for_dedup)

        # Phase 1d.5 — stamp the inbound request_id into metadata so the
        # FE's realtime echo carries the round-trip id back for dedup.
        # Caller-supplied metadata.request_id wins. See _stamp_request_id.
        effective_metadata = _stamp_request_id(
            metadata or existing.get("metadata", {}) if existing else metadata
        )

        if existing:
            if existing["owner_id"] != uid:
                await self.permissions.require_async("file", existing["id"], "write", uid)
            new_version = existing["current_version"] + 1
            await self._db.update_file_async(
                existing["id"],
                {
                    "storage_uri": storage_uri,
                    "size_bytes": len(content_bytes),
                    "checksum": checksum,
                    "mime_type": mime,
                    "current_version": new_version,
                    "visibility": visibility,
                    "parent_folder_id": folder_id,
                    "metadata": effective_metadata,
                },
            )
            file_record = {**existing, "current_version": new_version, "id": existing["id"]}
        else:
            insert_payload = {
                "owner_id": uid,
                "file_path": file_path,
                "storage_uri": storage_uri,
                "file_name": basename(file_path),
                "mime_type": mime,
                "size_bytes": len(content_bytes),
                "checksum": checksum,
                "visibility": visibility,
                "parent_folder_id": folder_id,
                "metadata": effective_metadata,
                # K0-1: stamp the resolved org (explicit or personal-org default)
                # so every file participates in the Knowledge/Scope system. None
                # is stripped by upsert_file_async (_strip_none) → DB default NULL,
                # which only happens if personal-org resolution failed (logged).
                "organization_id": org_id_for_dedup,
            }
            # Phase 1d.3 — lineage columns must be settable at insert time
            # (e.g. variants set parent_file_id=master_id +
            # derivation_kind='variant') so consumers can identify
            # derived rows by data shape without inspecting metadata.
            if parent_file_id is not None:
                insert_payload["parent_file_id"] = parent_file_id
            if derivation_kind is not None:
                insert_payload["derivation_kind"] = derivation_kind
            if effective_file_id is not None:
                # Pin the row id to the canonical UUID (caller-owned for
                # file_id writes, or the freshly-minted one for new inserts)
                # so row id == S3 key uuid. See P0-2 note above.
                insert_payload["id"] = effective_file_id
            # NOTE: we no longer write canonical_storage_uri. Migration 007
            # consolidates it INTO storage_uri (rename), making storage_uri
            # the single authoritative URI. A fresh insert's storage_uri is
            # already that URI, so there is nothing else to set. Readers use
            # `record.get("canonical_storage_uri") or record["storage_uri"]`,
            # which resolves correctly before AND after 007.
            try:
                file_record = await self._db.upsert_file_async(insert_payload)
            except Exception as insert_exc:
                # Race: a concurrent write of the same content won the
                # canonical slot between our dedup lookup and this INSERT.
                # Recover by re-querying for the winner; delete the orphan
                # S3 object we just PUT. Re-raise anything else.
                #
                # Only applies to root inserts (derivatives are excluded
                # by the dedup-canonical index predicate, so they cannot
                # violate it).
                if (
                    not is_derivative_write
                    and checksum
                    and self._is_dedup_unique_violation(insert_exc)
                ):
                    from matrx_utils.file_handling.dedup import lookup_existing_async

                    winner_lookup = await lookup_existing_async(
                        self._db,
                        checksum=checksum,
                        owner_id=uid,
                        organization_id=org_id_for_dedup,
                    )
                    if winner_lookup.has_duplicate and winner_lookup.existing is not None:
                        try:
                            await self._router.delete_async(storage_uri)
                        except Exception:
                            logger.warning(
                                "orphan S3 cleanup failed after dedup race for %s",
                                storage_uri,
                                exc_info=True,
                            )
                        return await self._sync_result_for_existing_async(
                            existing_row=winner_lookup.existing,
                            content_bytes=content_bytes,
                            checksum=checksum,
                            visibility=visibility,
                            share_with=share_with,
                            share_level=share_level,
                            granter_uid=uid,
                        )
                # Path-unique race: a concurrent pinned-id insert won the
                # (owner_id, file_path) slot between our lookup and this
                # INSERT (e.g. two variant-render passes for the same
                # content-deduped master writing the same variant path).
                # Recover idempotently: read the winning row and return its
                # SyncResult; delete the orphan S3 object we just PUT (it
                # lives under our exclusive <owner>/<file_id> key, so it was
                # never a prior version's bytes). This applies to derivative
                # writes too — the variant path IS the idempotency key.
                if self._is_path_unique_violation(insert_exc):
                    winner = await self._db.get_file_by_path_async(uid, file_path)
                    if winner is not None:
                        try:
                            await self._router.delete_async(storage_uri)
                        except Exception:
                            logger.warning(
                                "orphan S3 cleanup failed after path-collision for %s",
                                storage_uri,
                                exc_info=True,
                            )
                        return await self._sync_result_for_existing_async(
                            existing_row=winner,
                            content_bytes=content_bytes,
                            checksum=checksum,
                            visibility=visibility,
                            share_with=share_with,
                            share_level=share_level,
                            granter_uid=uid,
                        )
                # P0-1: the row INSERT failed for a reason we can't recover
                # (path-unique conflict on different content, DB error, …).
                # The S3 object we PUT moments ago is now orphaned — best-effort
                # delete it so failed writes don't leak storage forever. This is
                # safe here because we ONLY reach this branch on a NEW insert
                # (the `else` of `if existing`), so the object is exclusively
                # ours and was never a prior version's bytes. Loud log: an
                # orphan-cleanup failure is itself a defect worth seeing.
                try:
                    await self._router.delete_async(storage_uri)
                except Exception:
                    logger.warning(
                        "orphan S3 cleanup failed after INSERT failure for %s",
                        storage_uri,
                        exc_info=True,
                    )
                raise

        await self.versions.record_version_async(
            file_record,
            content_bytes,
            checksum=checksum,
            change_summary=change_summary,
            user_id=uid,
        )

        if share_with:
            for grantee_id in share_with:
                await self._db.upsert_permission_async(
                    {
                        "resource_id": file_record["id"],
                        "resource_type": "file",
                        "grantee_id": grantee_id,
                        "grantee_type": "user",
                        "permission_level": share_level,
                        "granted_by": uid,
                    }
                )
            # Specific-user access comes from the iam.permissions rows above
            # (RLS via iam.has_access); ambient visibility stays 'private'. The
            # legacy 'shared' visibility was removed (enum: private<internal<
            # link<public) and is never written. build_urls mints signed URLs
            # for every non-public file, so URLs are unaffected.

        # Mint every URL flavour via the central helper.
        synthetic = {
            "storage_uri": storage_uri,
            "visibility": visibility,
            "checksum": checksum,
            "file_name": basename(file_path),
            "mime_type": mime,
            "deleted_at": None,
        }
        urls = await self.build_urls_for_record_async(synthetic)

        # Populate the in-process byte cache so the typical
        # "upload then immediately submit AI request" flow doesn't have to
        # re-fetch from S3. The bytes are in hand right now — cache them.
        # Failure here is non-fatal (cache is best-effort).
        try:
            from matrx_utils.file_handling.cloud_sync.byte_cache import get_byte_cache

            get_byte_cache().put(
                file_record["id"],
                bytes_=content_bytes,
                mime_type=mime,
                owner_id=uid,
                file_path=file_path,
            )
        except Exception:
            logger.debug("byte cache populate failed", exc_info=True)

        return SyncResult(
            file_id=file_record["id"],
            storage_uri=storage_uri,
            version_number=file_record.get("current_version", 1),
            size_bytes=len(content_bytes),
            checksum=checksum,
            is_new=is_new,
            visibility=visibility,
            url=urls["url"],
            cdn_url=urls["cdn_url"],
            signed_url=urls["signed_url"],
            download_url=urls["download_url"],
            signed_url_expires_at=urls.get("signed_url_expires_at"),
            parent_file_id=file_record.get("parent_file_id"),
            derivation_kind=file_record.get("derivation_kind"),
        )

    # ==================================================================
    # IN-PLACE REPLACE BY FILE_ID
    # ==================================================================
    #
    # Why this exists separately from ``managed_write_async``:
    #
    # ``managed_write_async`` is keyed by ``(owner_id, file_path)`` — it
    # cannot update a row owned by someone else even when the caller has
    # an explicit write grant, because its initial lookup filters by
    # ``owner_id``. ``replace_file_async`` is keyed by ``file_id`` and
    # honours share-grants via PermissionsManager. It is the right
    # primitive for "transform a file and write the result back" flows
    # (compress, redact, AI-edit, collaborative document apps, etc.).
    # ==================================================================

    async def replace_file_async(
        self,
        file_id: str,
        content: bytes | str | dict | list,
        *,
        user_id: str,
        change_summary: str | None = None,
        mime_type: str | None = None,
        metadata_patch: dict | None = None,
        new_file_name: str | None = None,
    ) -> SyncResult:
        """Replace the contents of an existing cld_files row in place.

        Bumps ``current_version`` on the file row, archives the new bytes
        into ``cld_file_versions`` (so the prior version is restorable
        via ``versions.restore_version_async``), and updates the row's
        size / checksum / mime / metadata in one flow.

        ``metadata_patch`` is shallow-merged into the existing metadata
        JSONB. Pass ``{}`` (not None) to overwrite with an empty dict.

        ``new_file_name`` optionally updates the row's display
        ``file_name`` (the storage URI and ``file_path`` are unchanged so
        existing references keep working). Use for things like
        prefixing "optimized_" after a compression replace.
        """
        existing = await self._db.get_file_async(file_id)
        if not existing:
            raise ValueError(f"File '{file_id}' not found or soft-deleted.")

        if existing["owner_id"] != user_id:
            await self.permissions.require_async("file", file_id, "write", user_id)

        content_bytes = self._to_bytes(content)
        storage_uri = existing["storage_uri"]

        await self._router.write_async(
            storage_uri,
            content_bytes,
            content_type=mime_type
            or existing.get("mime_type")
            or self._guess_mime(existing["file_path"]),
        )

        checksum = self._checksum(content_bytes)
        mime = mime_type or existing.get("mime_type") or self._guess_mime(existing["file_path"])
        new_version = existing["current_version"] + 1

        updates: dict = {
            "size_bytes": len(content_bytes),
            "checksum": checksum,
            "mime_type": mime,
            "current_version": new_version,
        }
        # Phase 1d.5 — always stamp request_id on metadata; merge with the
        # caller's patch + the existing row's metadata so the round-trip
        # FE dedup works for in-place replace operations too.
        base_meta = existing.get("metadata") or {}
        merged_meta = {**base_meta, **(metadata_patch or {})}
        updates["metadata"] = _stamp_request_id(merged_meta)
        if new_file_name is not None:
            updates["file_name"] = new_file_name

        await self._db.update_file_async(file_id, updates)

        file_record = {
            **existing,
            **updates,
            "id": file_id,
        }

        await self.versions.record_version_async(
            file_record,
            content_bytes,
            checksum=checksum,
            change_summary=change_summary,
            user_id=user_id,
        )

        try:
            from matrx_utils.file_handling.cloud_sync.byte_cache import get_byte_cache

            get_byte_cache().invalidate(file_id)
            get_byte_cache().put(
                file_id,
                bytes_=content_bytes,
                mime_type=mime,
                owner_id=existing["owner_id"],
                file_path=existing["file_path"],
            )
        except Exception:
            logger.debug("byte cache update failed on replace", exc_info=True)

        # Mint URL flavours via the central helper — same contract as
        # managed_write_async. The replaced file_id keeps its visibility
        # and file_name from the existing row.
        synthetic = {
            "storage_uri": storage_uri,
            "visibility": existing.get("visibility") or "private",
            "checksum": checksum,
            "file_name": file_record.get("file_name") or basename(existing["file_path"]),
            "mime_type": mime,
            "deleted_at": None,
        }
        urls = await self.build_urls_for_record_async(synthetic)

        return SyncResult(
            file_id=file_id,
            storage_uri=storage_uri,
            version_number=new_version,
            size_bytes=len(content_bytes),
            checksum=checksum,
            is_new=False,
            visibility=synthetic["visibility"],
            url=urls["url"],
            cdn_url=urls["cdn_url"],
            signed_url=urls["signed_url"],
            download_url=urls["download_url"],
            signed_url_expires_at=urls.get("signed_url_expires_at"),
            parent_file_id=existing.get("parent_file_id"),
            derivation_kind=existing.get("derivation_kind"),
        )

    # ==================================================================
    # VISIBILITY CHANGE — moves the object between public/ and root prefixes
    # ==================================================================

    async def change_visibility_async(
        self,
        file_id: str,
        new_visibility: str,
        *,
        user_id: str | None = None,
    ) -> dict | None:
        """Change a file's visibility AND move the S3 object to the
        correct prefix in one transaction-like flow.

        Steps:
          1. Load the cld_files row.
          2. If visibility is unchanged → no-op (return record).
          3. Compute new_storage_uri based on the new visibility's prefix.
          4. Server-side S3 copy old → new (no download).
          5. Delete the old object.
          6. Update cld_files (storage_uri + visibility).
          7. Return the updated record so the caller can purge the CDN
             cache for the old URL.

        On any failure we leave both the row and the bytes in a
        consistent state — either the new URI exists and we update the
        row, or the old URI is intact and we surface the error.
        """
        record = await self._db.get_file_async(file_id)
        if not record:
            return None
        old_visibility = record.get("visibility")
        if old_visibility == new_visibility:
            return record

        old_uri = record["storage_uri"]
        # Rekey-safe new URI derivation: preserve the OLD URI's key
        # (everything after the bucket) and swap ONLY the bucket. The
        # legacy approach of `_storage_uri(file_path, owner_id)` would
        # rewrite the key to `<owner>/<file_path>`, breaking files that
        # the rekey backfill moved to `<owner>/<file_id>`.
        from .cdn import public_bucket

        try:
            scheme, rest = old_uri.split("://", 1)
        except ValueError:
            scheme, rest = "s3", old_uri
        old_bucket, _, key = rest.partition("/")
        if new_visibility == "public":
            target_bucket = public_bucket() or self._config.resolve_s3_bucket()
        else:
            target_bucket = self._config.resolve_s3_bucket()
        new_uri = f"{scheme}://{target_bucket}/{key}" if key else old_uri
        if new_uri == old_uri:
            # storage_uri shape didn't change (e.g. private→shared).
            await self._db.update_file_async(file_id, {"visibility": new_visibility})
            return await self._db.get_file_async(file_id)

        # Stage 1: copy the bytes to the new location BEFORE we touch
        # anything else. If this fails the old object is still live.
        await self._router.copy_async(old_uri, new_uri)

        # Stage 2: update the row so reads start hitting the new URI.
        await self._db.update_file_async(
            file_id,
            {
                "storage_uri": new_uri,
                "visibility": new_visibility,
            },
        )

        # Stage 3: delete the old object. If this fails we have an orphan
        # in S3 (small lifecycle-policy chore) but the row is correct.
        try:
            await self._router.delete_async(old_uri)
        except Exception:
            logger.warning(
                "change_visibility_async: orphaned old key %s after move",
                old_uri,
                exc_info=True,
            )

        # Stage 4: notify the CDN purger of the URL the FE previously
        # cached against the OLD storage URI. If the host hasn't wired a
        # purger this is a no-op. Fire-and-forget — we never block on it.
        try:
            from matrx_utils.conf import get_cdn_purger

            purger = get_cdn_purger()
            if purger is not None:
                from .cdn import public_url_for

                old_cdn_url = public_url_for(
                    {
                        "visibility": old_visibility,
                        "storage_uri": old_uri,
                        "checksum": record.get("checksum"),
                        "deleted_at": None,
                    }
                )
                if old_cdn_url:
                    purger([old_cdn_url])
        except Exception:
            logger.debug("CDN purge dispatch failed", exc_info=True)

        return await self._db.get_file_async(file_id)

    def managed_read(
        self,
        file_path: str,
        *,
        user_id: str | None = None,
        version: int | None = None,
    ) -> bytes:
        """Read a file from cloud, checking permissions.

        If *version* is given, reads that specific version.
        Raises PermissionError if the user lacks read access.
        """
        uid = self._resolve_user_id(user_id)
        file_record = self._db.get_file_by_path(uid, file_path)

        if not file_record:
            # Try to find a file shared with this user
            # (owned by someone else but shared via permissions)
            raise FileNotFoundError(f"File '{file_path}' not found for user '{uid}'.")

        if file_record["owner_id"] != uid:
            self.permissions.require("file", file_record["id"], "read", uid)

        if version is not None:
            content = self.versions.read_version(file_record["id"], version)
            if content is None:
                raise ValueError(f"Version {version} not found for '{file_path}'.")
            return content

        return self._router.read(file_record["storage_uri"])

    async def managed_read_async(
        self,
        file_path: str,
        *,
        user_id: str | None = None,
        version: int | None = None,
    ) -> bytes:
        """Async version of managed_read()."""
        uid = self._resolve_user_id(user_id)
        file_record = await self._db.get_file_by_path_async(uid, file_path)

        if not file_record:
            raise FileNotFoundError(f"File '{file_path}' not found for user '{uid}'.")

        if file_record["owner_id"] != uid:
            await self.permissions.require_async("file", file_record["id"], "read", uid)

        if version is not None:
            content = await self.versions.read_version_async(file_record["id"], version)
            if content is None:
                raise ValueError(f"Version {version} not found for '{file_path}'.")
            return content

        return await self._router.read_async(file_record["storage_uri"])

    # ------------------------------------------------------------------
    # Hard-delete — the ONE primitive.  Cascade the DB row + versions +
    # permissions + share-links via the SQL fn, THEN purge every storage
    # object it reported and drop the byte cache.  Every hard-delete path
    # (managed_delete, FileService.hard_delete, orphan cleanup) MUST route
    # through here — calling ``db.hard_delete_file[_async]`` directly deletes
    # the rows but strands the S3 objects (the C10 orphan-data leak).  The
    # boundary guard ``scripts/audit_hard_delete_purge.py`` fails the build on
    # any direct DB-fn call outside this method.
    # ------------------------------------------------------------------

    @staticmethod
    def _purge_uris_from(storage_uri: object, purge: object) -> list[str]:
        """Dedupe every storage location a hard-delete must remove: the row's
        own ``storage_uri`` plus the ``main`` + ``versions`` the SQL fn reports
        (a service-role caller receives them; a JWT caller does not)."""
        uris: list[str] = []
        seen: set[str] = set()

        def _add(u: object) -> None:
            if isinstance(u, str) and u and u not in seen:
                seen.add(u)
                uris.append(u)

        _add(storage_uri)
        if isinstance(purge, dict):
            _add(purge.get("main"))
            for u in purge.get("versions") or []:
                _add(u)
        return uris

    def hard_delete_and_purge(self, file_id: str, storage_uri: object) -> dict | None:
        """Cascade-delete the row/versions/perms/links, then purge every
        storage object.  Returns the SQL fn's purge report (or ``None`` if it
        failed).  The single sanctioned hard-delete entry point."""
        try:
            purge = self._db.hard_delete_file(file_id)
        except Exception:
            logger.warning(
                "hard_delete_file SQL fn failed for %s; purging known object only",
                file_id,
                exc_info=True,
            )
            purge = None
        for uri in self._purge_uris_from(storage_uri, purge):
            try:
                self._router.delete(uri)
            except Exception:
                logger.warning("Failed to delete storage object during hard-delete: %s", uri)
        self._invalidate_byte_cache(file_id)
        return purge

    async def hard_delete_and_purge_async(self, file_id: str, storage_uri: object) -> dict | None:
        """Async twin of :meth:`hard_delete_and_purge`."""
        try:
            purge = await self._db.hard_delete_file_async(file_id)
        except Exception:
            logger.warning(
                "hard_delete_file_async SQL fn failed for %s; purging known object only",
                file_id,
                exc_info=True,
            )
            purge = None
        for uri in self._purge_uris_from(storage_uri, purge):
            try:
                await self._router.delete_async(uri)
            except Exception:
                logger.warning("Failed to delete storage object during hard-delete: %s", uri)
        self._invalidate_byte_cache(file_id)
        return purge

    @staticmethod
    def _invalidate_byte_cache(file_id: str) -> None:
        try:
            from matrx_utils.file_handling.cloud_sync.byte_cache import get_byte_cache

            get_byte_cache().invalidate(file_id)
        except Exception:
            pass

    def managed_delete(
        self,
        file_path: str,
        *,
        user_id: str | None = None,
        hard_delete: bool = False,
    ) -> bool:
        """Delete a file (soft by default).  Requires admin access."""
        uid = self._resolve_user_id(user_id)
        file_record = self._db.get_file_by_path(uid, file_path)
        if not file_record:
            return False

        if file_record["owner_id"] != uid:
            self.permissions.require("file", file_record["id"], "admin", uid)

        if hard_delete:
            self.hard_delete_and_purge(file_record["id"], file_record["storage_uri"])
            return True

        ok = self._db.soft_delete_file(file_record["id"])
        self._invalidate_byte_cache(file_record["id"])
        return ok

    async def managed_delete_async(
        self,
        file_path: str,
        *,
        user_id: str | None = None,
        hard_delete: bool = False,
    ) -> bool:
        """Async version of managed_delete()."""
        uid = self._resolve_user_id(user_id)
        file_record = await self._db.get_file_by_path_async(uid, file_path)
        if not file_record:
            return False

        if file_record["owner_id"] != uid:
            await self.permissions.require_async("file", file_record["id"], "admin", uid)

        if hard_delete:
            await self.hard_delete_and_purge_async(file_record["id"], file_record["storage_uri"])
            return True

        ok = await self._db.soft_delete_file_async(file_record["id"])
        self._invalidate_byte_cache(file_record["id"])
        return ok

    # ------------------------------------------------------------------
    # Listing / querying
    # ------------------------------------------------------------------

    def list_files(
        self,
        folder_path: str | None = None,
        user_id: str | None = None,
    ) -> list[dict]:
        """List files owned by the user, optionally filtered by folder."""
        uid = self._resolve_user_id(user_id)
        folder_id = None
        if folder_path:
            folder = self._db.get_folder_by_path(uid, folder_path)
            folder_id = folder["id"] if folder else "__nonexistent__"
        return self._db.list_files(uid, folder_id)

    async def list_files_async(
        self,
        folder_path: str | None = None,
        user_id: str | None = None,
    ) -> list[dict]:
        uid = self._resolve_user_id(user_id)
        folder_id = None
        if folder_path:
            folder = await self._db.get_folder_by_path_async(uid, folder_path)
            folder_id = folder["id"] if folder else "__nonexistent__"
        return await self._db.list_files_async(uid, folder_id)

    async def list_changed_files_async(
        self,
        since_iso: str,
        limit: int = 1000,
        user_id: str | None = None,
    ) -> list[dict]:
        uid = self._resolve_user_id(user_id)
        return await self._db.list_changed_files_async(uid, since_iso, limit)

    async def list_files_paginated_async(
        self,
        prefix: str | None = None,
        limit: int = 1000,
        user_id: str | None = None,
    ) -> list[dict]:
        uid = self._resolve_user_id(user_id)
        return await self._db.list_files_paginated_async(uid, prefix, limit)

    async def get_storage_usage_async(self, user_id: str | None = None) -> dict:
        uid = self._resolve_user_id(user_id)
        return await self._db.get_storage_usage_async(uid)

    def list_folders(
        self,
        parent_path: str | None = None,
        user_id: str | None = None,
    ) -> list[dict]:
        uid = self._resolve_user_id(user_id)
        parent_id = None
        if parent_path:
            parent = self._db.get_folder_by_path(uid, parent_path)
            parent_id = parent["id"] if parent else "__nonexistent__"
        return self._db.list_folders(uid, parent_id)

    async def list_folders_async(
        self,
        parent_path: str | None = None,
        user_id: str | None = None,
    ) -> list[dict]:
        uid = self._resolve_user_id(user_id)
        parent_id = None
        if parent_path:
            parent = await self._db.get_folder_by_path_async(uid, parent_path)
            parent_id = parent["id"] if parent else "__nonexistent__"
        return await self._db.list_folders_async(uid, parent_id)

    def get_file_info(self, file_path: str, user_id: str | None = None) -> dict | None:
        """Get file metadata from the database."""
        uid = self._resolve_user_id(user_id)
        return self._db.get_file_by_path(uid, file_path)

    async def get_file_info_async(self, file_path: str, user_id: str | None = None) -> dict | None:
        uid = self._resolve_user_id(user_id)
        return await self._db.get_file_by_path_async(uid, file_path)

    def get_file_url(
        self,
        file_path: str,
        expires_in: int = 3600,
        user_id: str | None = None,
    ) -> str:
        """Get a signed URL for a tracked file, with permission check."""
        uid = self._resolve_user_id(user_id)
        file_record = self._db.get_file_by_path(uid, file_path)
        if not file_record:
            raise FileNotFoundError(f"File '{file_path}' not found for user '{uid}'.")
        if file_record["owner_id"] != uid:
            self.permissions.require("file", file_record["id"], "read", uid)
        return self._router.get_url(file_record["storage_uri"], expires_in=expires_in)

    async def get_file_url_async(
        self,
        file_path: str,
        expires_in: int = 3600,
        user_id: str | None = None,
    ) -> str:
        uid = self._resolve_user_id(user_id)
        file_record = await self._db.get_file_by_path_async(uid, file_path)
        if not file_record:
            raise FileNotFoundError(f"File '{file_path}' not found for user '{uid}'.")
        if file_record["owner_id"] != uid:
            await self.permissions.require_async("file", file_record["id"], "read", uid)
        return await self._router.get_url_async(file_record["storage_uri"], expires_in=expires_in)
