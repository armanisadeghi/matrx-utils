"""FileService — the single public entry point for file handling.

A high-level facade over the matrx-utils file_handling stack. Hosts
construct one ``FileService`` at startup and delegate every file
operation through it. Eliminates the pattern where routers reach into
``fm.sync_engine.db.get_file_async(...)`` because the underlying
facade exposes everything they need.

Usage in a host application:

    from matrx_utils import configure_settings, configure_context
    from matrx_utils.file_handling import FileService

    configure_settings(my_settings)
    configure_context(get_active_user_id)
    file_service = FileService.from_env()

    # Reads with authorization in one call:
    record = await file_service.read_record(file_id, user_id=uid)

    # URL minting — never re-implement.
    asset = await file_service.build_asset_envelope(record)

    # Soft delete + restore.
    await file_service.soft_delete(file_id, user_id=uid)

The facade composes:
  * ``SyncEngine`` — managed_write_async, change_visibility_async,
    build_urls_for_record_async (centralized URL minting).
  * ``PermissionsManager`` — share-links, grants, group ACL.
  * ``VersionManager`` — version history + restore.

Plus host-injected callbacks (``configure_cdn_purger``,
``configure_quota_check``, ``configure_audit_logger``) so the same
service handles host-specific concerns without the matrx-utils code
importing from any host.

This file replaces the audit-flagged "27 files reach into ``_db``"
anti-pattern: every method here is the public API a caller should use.
"""

from __future__ import annotations

from typing import Any

from .file_manager import FileManager
from .asset_envelope import Asset, AssetVariant


class FileService:
    """High-level facade for file handling. The single entry point.

    Construct via ``FileService.from_env()`` to read settings (S3
    credentials, Supabase URL) from ``configure_settings()`` /
    environment variables and bootstrap a process-wide singleton.
    """

    _instance: "FileService | None" = None

    def __init__(self, file_manager: FileManager) -> None:
        if file_manager.sync_engine is None:
            raise RuntimeError(
                "FileService requires a FileManager with cloud_sync configured. "
                "Pass cloud_sync=CloudSyncConfig(...) when constructing."
            )
        self._fm = file_manager

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    @classmethod
    def from_env(cls, *, app_name: str = "matrx-files") -> "FileService":
        """Build a process-wide singleton from env-vars / ``configure_settings``.

        Reads ``AWS_S3_DEFAULT_BUCKET``, ``SUPABASE_URL``,
        ``SUPABASE_SECRET_KEY`` (and friends) through the matrx-utils
        settings registry. Idempotent — subsequent calls return the
        cached instance.
        """
        if cls._instance is not None:
            return cls._instance
        from .cloud_sync.config import CloudSyncConfig
        fm = FileManager(app_name, cloud_sync=CloudSyncConfig(auto_sync=True))
        cls._instance = cls(fm)
        return cls._instance

    @classmethod
    def for_file_manager(cls, fm: FileManager) -> "FileService":
        """Wrap a caller-constructed FileManager. Use in tests or for
        per-app-name isolation where the singleton is the wrong shape."""
        return cls(fm)

    # ------------------------------------------------------------------
    # Sub-component accessors (so callers don't drill through to
    # ``service._fm.sync_engine.permissions``).
    # ------------------------------------------------------------------

    @property
    def file_manager(self) -> FileManager:
        return self._fm

    @property
    def sync_engine(self) -> Any:
        return self._fm.sync_engine

    @property
    def db(self) -> Any:
        return self._fm.sync_engine.db

    @property
    def router(self) -> Any:
        return self._fm.sync_engine.router

    @property
    def permissions(self) -> Any:
        return self._fm.sync_engine.permissions

    @property
    def versions(self) -> Any:
        return self._fm.sync_engine.versions

    @property
    def image_handler(self) -> Any:
        return self._fm.image_handler

    # ------------------------------------------------------------------
    # Authorization-aware reads
    # ------------------------------------------------------------------

    async def read_record(
        self,
        file_id: str,
        *,
        user_id: str,
        level: str = "read",
    ) -> dict:
        """Fetch a cld_files row after enforcing access in one call.

        Raises ``FileNotFoundError`` if the row is missing,
        ``PermissionError`` if the caller lacks the requested level.
        """
        return await self._fm.sync_engine.get_authorized_record_async(
            file_id, user_id=user_id, level=level
        )

    async def read_record_unchecked(self, file_id: str) -> dict | None:
        """Load a cld_files row WITHOUT authorization. For background
        tasks that already verified access (thumbnails, rekey, audit
        dispatcher). Never use in a request handler."""
        return await self._fm.sync_engine.db.get_file_async(file_id)

    async def read_record_for_active_user(self, file_id: str, *, level: str = "read") -> dict | None:
        """Load a cld_files row, enforcing access for the AMBIENT request user.

        The same ACCESS GATE contract as resolve_media, for byte-serving paths
        that resolve a user-supplied ``file_id`` but do not go through
        resolve_media (preview, pdf-compress, …):

        FAIL-CLOSED, matching the resolve_media gate:
          * request user present → enforce owner / public / shared; raises
            ``PermissionError`` on denial.
          * an explicit ``matrx_utils.ctx.system_file_access("<reason>")`` scope
            (internal/background job that declared itself) → trusted lookup.
          * otherwise (anonymous HTTP, OR a no-context call with no marker) →
            ``PermissionError``. No identity + no declared system scope = denied.

        Use this instead of ``db.get_file_async`` anywhere a request handler
        turns a client-supplied file_id into bytes.
        """
        from matrx_utils.ctx import get_active_context, get_system_file_access_reason

        ctx = get_active_context()
        uid = (getattr(ctx, "user_id", None) or "") if ctx is not None else ""
        if uid:
            return await self._fm.sync_engine.get_authorized_record_async(
                file_id, user_id=uid, level=level
            )
        if get_system_file_access_reason():
            return await self._fm.sync_engine.db.get_file_async(file_id)  # explicit internal job
        raise PermissionError(
            "file access requires an authenticated user or an explicit "
            "matrx_utils.ctx.system_file_access() scope (fail-closed)"
        )

    async def read_by_path(self, owner_id: str, file_path: str) -> dict | None:
        return await self._fm.sync_engine.db.get_file_by_path_async(
            owner_id, file_path
        )

    # ------------------------------------------------------------------
    # URL minting (centralized — see SyncEngine.build_urls_for_record_async).
    # ------------------------------------------------------------------

    async def build_urls(
        self,
        record: dict,
        *,
        signed_ttl: int = 3600,
    ) -> dict:
        """Return ``{url, cdn_url, signed_url, download_url}`` for a record.

        Never call ``router.get_url_async`` directly — that bypasses
        content-disposition + CDN-vs-signed routing.
        """
        return await self._fm.sync_engine.build_urls_for_record_async(
            record, signed_ttl=signed_ttl
        )

    async def build_asset_envelope(
        self,
        record: dict,
        *,
        signed_ttl: int = 3600,
        preset_name: str | None = None,
        primary_key: str | None = None,
        include_variants: bool = True,
        master_width: int | None = None,
        master_height: int | None = None,
    ) -> Asset:
        """Build a full ``Asset`` envelope for a master record.

        Loads sibling variant rows (when present) and assembles the
        canonical wire shape consumed by every FE. Self-contained — no
        host dependency. The renderer (``_render_image_variants_to_cloud``
        that writes new variants) still lives in the host's asset router
        for now since it carries account-tier + quota concerns.
        """
        from .asset_builder import build_asset_from_master
        return await build_asset_from_master(
            self._fm, record,
            preset_name=preset_name,
            primary_key=primary_key,
            signed_ttl=signed_ttl,
            include_variants=include_variants,
            master_width=master_width,
            master_height=master_height,
        )

    # ------------------------------------------------------------------
    # Writes
    # ------------------------------------------------------------------

    async def write(
        self,
        content: bytes | str | dict | list,
        *,
        file_path: str,
        mime_type: str | None = None,
        visibility: str = "private",
        share_with: list[str] | None = None,
        share_level: str = "read",
        change_summary: str | None = None,
        user_id: str | None = None,
        metadata: dict | None = None,
    ) -> Any:
        """Buffered write through the canonical engine path.

        Returns a ``SyncResult`` with the full URL envelope already
        populated (``url`` / ``cdn_url`` / ``signed_url`` /
        ``download_url`` / ``visibility``).
        """
        return await self._fm.sync_engine.managed_write_async(
            file_path,
            content,
            mime_type=mime_type,
            visibility=visibility,
            share_with=share_with,
            share_level=share_level,
            change_summary=change_summary,
            user_id=user_id,
            metadata=metadata,
        )

    async def replace_file(
        self,
        file_id: str,
        content: bytes | str | dict | list,
        *,
        user_id: str,
        change_summary: str | None = None,
        mime_type: str | None = None,
        metadata_patch: dict | None = None,
        new_file_name: str | None = None,
    ) -> Any:
        """In-place replace by file_id — preserves storage_uri + version-bumps."""
        return await self._fm.sync_engine.replace_file_async(
            file_id,
            content,
            user_id=user_id,
            change_summary=change_summary,
            mime_type=mime_type,
            metadata_patch=metadata_patch,
            new_file_name=new_file_name,
        )

    # ------------------------------------------------------------------
    # Visibility / sharing
    # ------------------------------------------------------------------

    async def change_visibility(
        self,
        file_id: str,
        *,
        user_id: str,
        new_visibility: str,
    ) -> dict | None:
        """Change a file's visibility (moves the S3 object between buckets)."""
        # Authorization: writer-level access required.
        record = await self.read_record(file_id, user_id=user_id, level="write")
        result = await self._fm.sync_engine.change_visibility_async(
            file_id, new_visibility, user_id=user_id
        )
        self._audit("file.visibility_changed", record, user_id,
                    new_visibility=new_visibility)
        return result

    async def grant_permission(
        self,
        *,
        file_id: str,
        user_id: str,                  # grantor
        grantee_id: str,
        level: str = "read",
        grantee_type: str = "user",
    ) -> dict:
        """Grant access to another user. Grantor must be admin/owner."""
        record = await self.read_record(file_id, user_id=user_id, level="admin")
        result = await self._fm.sync_engine.db.upsert_permission_async({
            "resource_id": file_id,
            "resource_type": "file",
            "grantee_id": grantee_id,
            "grantee_type": grantee_type,
            "permission_level": level,
            "granted_by": user_id,
        })
        self._audit("permission.granted", record, user_id,
                    grantee_id=grantee_id, grantee_type=grantee_type, level=level)
        return result

    async def revoke_permission(
        self,
        *,
        file_id: str,
        user_id: str,
        grantee_id: str,
        grantee_type: str = "user",
    ) -> bool:
        record = await self.read_record(file_id, user_id=user_id, level="admin")
        result = await self._fm.sync_engine.db.delete_permission_async(
            resource_id=file_id,
            resource_type="file",
            grantee_id=grantee_id,
            grantee_type=grantee_type,
        )
        self._audit("permission.revoked", record, user_id,
                    grantee_id=grantee_id, grantee_type=grantee_type)
        return result

    # ------------------------------------------------------------------
    # Soft / hard delete
    # ------------------------------------------------------------------

    def _audit(self, event_type: str, record: dict | None, user_id: str, **extras: Any) -> None:
        """Fire a file-mutation audit event through the host-configured
        logger (``fire_audit_event`` is a no-op when none is wired, and
        never raises). The actor (``user_id``) is what lets the event
        match owner-scoped webhooks downstream."""
        from .cloud_sync.events import fire_audit_event

        record = record or {}
        fire_audit_event(event_type, {
            "resource_id": record.get("id"),
            "resource_type": "file",
            "organization_id": record.get("organization_id"),
            "user_id": user_id,
            **extras,
        })

    async def soft_delete(self, file_id: str, *, user_id: str) -> bool:
        """Mark a file deleted (recoverable via /restore)."""
        record = await self.read_record(file_id, user_id=user_id, level="admin")
        result = await self._fm.sync_engine.db.soft_delete_file_async(record["id"])
        self._audit("file.deleted", record, user_id)
        return result

    async def restore(self, file_id: str, *, user_id: str) -> bool:
        """Undo a soft-delete. Requires admin on the file."""
        # We can't read the record through the public path (it's soft-deleted).
        # Pull via raw DB then check ownership manually.
        record = await self._fm.sync_engine.db.get_file_async(
            file_id, include_deleted=True
        )
        if not record:
            raise FileNotFoundError(f"File {file_id!r} not found")
        if record.get("owner_id") != user_id:
            await self.permissions.require_async("file", file_id, "admin", user_id)
        from .cloud_sync.db import T_FILES, afiles_table

        client = await self._fm.sync_engine.db._get_async_client()
        await afiles_table(client, T_FILES).update({"deleted_at": None}).eq("id", file_id).execute()
        self._audit("file.restored", record, user_id)
        return True

    async def hard_delete(self, file_id: str, *, user_id: str) -> dict | None:
        """Hard delete — removes the row + all versions AND purges every S3
        object.  Routes through the ONE sanctioned primitive
        (``SyncEngine.hard_delete_and_purge_async``); calling the raw DB fn
        here would strand the storage objects (the C10 orphan-data leak)."""
        record = await self.read_record(file_id, user_id=user_id, level="admin")
        result = await self._fm.sync_engine.hard_delete_and_purge_async(
            record["id"], record.get("storage_uri")
        )
        self._audit("file.hard_deleted", record, user_id)
        return result

    # ------------------------------------------------------------------
    # Backfill conveniences (delegate to the cloud_sync.backfill module).
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Sub-component accessors — host code reaches portable primitives.
    # ------------------------------------------------------------------

    @property
    def tus(self) -> Any:
        """TUS resumable-upload manager. See cloud_sync/transports/tus.py."""
        return self.sync_engine.tus

    @property
    def presigned(self) -> Any:
        """Presigned PUT upload coordinator. See cloud_sync/transports/presigned.py."""
        return self.sync_engine.presigned

    @property
    def streamer(self) -> Any:
        """Range-aware download streamer. See cloud_sync/download_stream.py."""
        return self.sync_engine.streamer

    @property
    def variants(self) -> Any:
        """Idempotent variant rendering. See cloud_sync/variants_service.py."""
        return self.sync_engine.variants

    # ------------------------------------------------------------------
    # Buffered upload (single-POST). The portable orchestration; hosts
    # supply quota policy + post-upload hooks.
    # ------------------------------------------------------------------

    async def upload_simple(
        self,
        content: bytes,
        *,
        file_path: str,
        user_id: str,
        mime_type: str | None = None,
        visibility: str = "private",
        share_with: list[str] | None = None,
        share_level: str = "read",
        change_summary: str | None = None,
        metadata: dict | None = None,
        auto_thumbnail: bool = True,
        auto_rekey: bool = True,
        on_complete: Any = None,
        file_id: str | None = None,
    ) -> Any:
        """Buffered upload + automatic post-write orchestration.

        Always:
          - calls ``managed_write_async`` with the canonical write path
          - fires the thumbnail processor (if ``auto_thumbnail=True``)
          - fires the canonical-key rekey (if ``auto_rekey=True``)

        Optionally calls the host-supplied ``on_complete(result)`` callable
        — async or sync — for host-specific work (quota delta, custom
        analysis dispatch, audit emission). The callback is fire-and-forget;
        its failure logs but does not propagate.

        Returns the ``SyncResult`` from ``managed_write_async``.
        """
        import asyncio as _asyncio
        result = await self.sync_engine.managed_write_async(
            file_path,
            content,
            mime_type=mime_type,
            visibility=visibility,
            share_with=share_with,
            share_level=share_level,
            change_summary=change_summary,
            metadata=metadata,
            user_id=user_id,
            file_id=file_id,
        )
        if auto_thumbnail:
            try:
                from .cloud_sync.processing import generate_thumbnail_for_file
                _asyncio.create_task(
                    generate_thumbnail_for_file(self._fm, result.file_id)
                )
            except Exception:
                pass
        # Rekey only when the caller used the legacy path scheme. When a
        # file_id is pinned the row is born canonical — nothing to copy.
        if auto_rekey and file_id is None:
            try:
                from .cloud_sync.backfill import rekey_one_file
                _asyncio.create_task(rekey_one_file(self._fm, result.file_id))
            except Exception:
                pass
        if on_complete is not None:
            try:
                ret = on_complete(result)
                if hasattr(ret, "__await__"):
                    _asyncio.create_task(ret)
            except Exception as e:
                from matrx_utils import vcprint
                vcprint(
                    f"[FileService.upload_simple] on_complete hook failed: {e!r}",
                    color="yellow",
                )
        return result

    # ------------------------------------------------------------------
    # Intent-aware dedup upload (Phase 2.0 strict-intent contract).
    # ------------------------------------------------------------------

    async def find_by_checksum(
        self,
        *,
        checksum: str,
        owner_id: str | None = None,
        organization_id: str | None = None,
    ) -> dict | None:
        """Look up the canonical cld_files row for a given content hash.

        Returns ``None`` if no match (or if both scope params are NULL).
        Org-scope wins when ``organization_id`` is provided. Owner-scope
        is used for personal libraries outside any org. The returned row
        is the OLDEST non-deleted, non-aliased row — the canonical
        across re-uploads.
        """
        return await self._fm.sync_engine.db.get_file_by_checksum_async(
            checksum,
            owner_id=owner_id,
            organization_id=organization_id,
        )

    async def upload_with_intent(
        self,
        content: bytes,
        *,
        intent: str,
        file_path: str,
        owner_id: str,
        organization_id: str | None = None,
        mime_type: str | None = None,
        visibility: str = "private",
        share_with: list[str] | None = None,
        share_level: str = "read",
        change_summary: str | None = None,
        metadata: dict | None = None,
        reason: str | None = None,
        auto_thumbnail: bool = True,
        auto_rekey: bool = True,
        on_complete: Any = None,
    ) -> dict:
        """Strict-intent dedup-aware upload.

        Three intents, no upsert ambiguity:

        * ``intent='create'``         — fail-loud if a duplicate exists.
          Raises ``DuplicateFileError`` (HTTP 409 mappable). The caller
          (UI) should surface the conflict and re-submit with a
          different intent.

        * ``intent='alias_existing'`` — return the existing row when a
          duplicate is found; create a new row when not. No new bytes
          are written if a duplicate is found.

        * ``intent='force_new_copy'`` — create a deliberate parallel
          copy. Requires a ``reason`` (>= 4 chars). The new row's
          ``duplicate_of_file_id`` points at the canonical, and
          ``metadata.force_new_copy_reason`` records the justification.

        Returns a dict with shape::

            {
              "outcome": "created" | "aliased" | "force_copy_created",
              "file_id": str,
              "file_path": str,
              "checksum": str,
              "duplicate_of_file_id": str | None,
              "result": SyncResult | None,   # present only when bytes
                                              # were actually written
            }

        For ``aliased`` outcomes, ``result`` is None because no write
        happened — the existing row is returned as-is.
        """
        from .dedup import (
            DedupDecision,
            UploadIntent,
            compute_checksum,
            resolve_async,
        )
        import asyncio as _asyncio

        checksum = compute_checksum(content)
        decision: DedupDecision = await resolve_async(
            self._fm.sync_engine.db,
            intent=intent,
            content=content,
            owner_id=owner_id,
            organization_id=organization_id,
            reason=reason,
            precomputed_checksum=checksum,
        )

        if decision.action == "return_existing":
            existing = decision.lookup.existing or {}
            return {
                "outcome": "aliased",
                "file_id": str(existing.get("id")),
                "file_path": existing.get("file_path"),
                "checksum": checksum,
                "duplicate_of_file_id": None,
                "result": None,
                "scope": decision.lookup.scope,
                "message": (
                    f"File with this content already exists "
                    f"(uploaded {existing.get('created_at')}). Reusing it."
                ),
            }

        # Both write_new and write_alias write bytes; the difference is
        # whether duplicate_of_file_id gets stamped on the new row.
        write_metadata = dict(metadata or {})
        if decision.action == "write_alias":
            write_metadata["force_new_copy_reason"] = decision.reason
            write_metadata["duplicate_of_file_id"] = decision.canonical_file_id

        if organization_id is not None:
            # Propagate through to the SyncEngine so the new row is
            # created in the right scope. We pass via metadata because
            # SyncEngine.managed_write_async honors organization_id from
            # metadata for placement.
            write_metadata.setdefault("organization_id", organization_id)

        sync_result = await self.sync_engine.managed_write_async(
            file_path,
            content,
            mime_type=mime_type,
            visibility=visibility,
            share_with=share_with,
            share_level=share_level,
            change_summary=change_summary,
            metadata=write_metadata,
            user_id=owner_id,
        )

        # Stamp duplicate_of_file_id on the new row when force_new_copy.
        if decision.action == "write_alias" and decision.canonical_file_id:
            await self._fm.sync_engine.db.update_file_async(
                sync_result.file_id,
                {"duplicate_of_file_id": decision.canonical_file_id},
            )

        # Best-effort post-write hooks (matching upload_simple).
        if auto_thumbnail:
            try:
                from .cloud_sync.processing import generate_thumbnail_for_file
                _asyncio.create_task(
                    generate_thumbnail_for_file(self._fm, sync_result.file_id)
                )
            except Exception:
                pass
        if auto_rekey:
            try:
                from .cloud_sync.backfill import rekey_one_file
                _asyncio.create_task(rekey_one_file(self._fm, sync_result.file_id))
            except Exception:
                pass
        if on_complete is not None:
            try:
                ret = on_complete(sync_result)
                if hasattr(ret, "__await__"):
                    _asyncio.create_task(ret)
            except Exception as e:
                from matrx_utils import vcprint
                vcprint(
                    f"[FileService.upload_with_intent] on_complete hook failed: {e!r}",
                    color="yellow",
                )

        outcome = (
            "force_copy_created"
            if decision.action == "write_alias"
            else "created"
        )
        return {
            "outcome": outcome,
            "file_id": sync_result.file_id,
            "file_path": file_path,
            "checksum": checksum,
            "duplicate_of_file_id": decision.canonical_file_id
            if decision.action == "write_alias"
            else None,
            "result": sync_result,
            "scope": decision.lookup.scope,
        }

    # ------------------------------------------------------------------
    # Range-aware streaming download.
    # ------------------------------------------------------------------

    async def open_stream(
        self,
        file_id: str,
        *,
        user_id: str,
        range_header: str | None = None,
        version: int | None = None,
        allow_inline: bool = False,
    ) -> Any:
        """Open a streaming download for a file the user has read-access to.

        Authorizes via :meth:`SyncEngine.get_authorized_record_async`, then
        delegates to :class:`DownloadStreamer` for the Range / ETag /
        Content-Disposition logic. Returns a
        :class:`matrx_utils.file_handling.cloud_sync.download_stream.StreamingResult`
        that the FastAPI router converts to ``StreamingResponse`` (or any
        other web framework's equivalent).
        """
        record = await self.sync_engine.get_authorized_record_async(
            file_id, user_id=user_id, level="read",
        )
        return await self.streamer.open_stream(
            record,
            range_header=range_header,
            version=version,
            allow_inline=allow_inline,
        )

    async def rekey_one(self, file_id: str) -> bool:
        from .cloud_sync.backfill import rekey_one_file
        return await rekey_one_file(self._fm, file_id)

    async def generate_thumbnail(self, file_id: str) -> bool:
        from .cloud_sync.processing import generate_thumbnail_for_file
        return await generate_thumbnail_for_file(self._fm, file_id)

    # ==================================================================
    # COMBINED OPERATIONS (FE-team A.1 / A.2 / A.3)
    # ==================================================================
    # Each method runs an upload / mutation / bulk-op as ONE call from
    # the FE's perspective, with best-effort atomicity:
    #   * Upload (write or mutation) always lands first.
    #   * Sub-operations (share-link create, permission grants, variant
    #     renders) run after, sequentially. Failures surface in
    #     ``errors`` on the returned envelope; we do NOT roll back the
    #     successful sub-ops.
    #   * Idempotency: when ``idempotency_key`` is set the entire bundled
    #     response is memoized in ``cld_idempotency``. Retry with the
    #     same key + same body returns the cached envelope verbatim.
    # The FE handles partial-success by reading the ``errors`` array.
    # ==================================================================

    async def upload_with_options(
        self,
        content: bytes | str | dict | list,
        *,
        file_path: str,
        owner_id: str,
        mime_type: str | None = None,
        visibility: str = "private",
        metadata: dict | None = None,
        # Bundled sub-ops:
        share: dict | None = None,                  # {"permission_level": "read"|"write", "expires_at"?: iso, "max_uses"?: int}
        permissions: list[dict] | None = None,      # [{"grantee_id", "grantee_type"?, "permission_level", "expires_at"?}]
        variants: list[str] | list[dict] | None = None,  # preset variant keys OR ImageVariant dicts
        preset: str | None = None,
        # Idempotency:
        idempotency_key: str | None = None,
        request_payload_for_idempotency: dict | None = None,
    ) -> dict:
        """Upload + share-link + permissions + variants in one call.

        Returns ``{"asset": Asset, "share_link": dict|None, "errors": [{"sub_op", "message"}]}``.
        Best-effort atomic — the upload always lands. Sub-op failures
        appear in ``errors``; the FE decides whether to retry them.

        ``idempotency_key`` memoizes the WHOLE bundled response so a
        flaky-network retry with the same key returns the same envelope.
        """
        from .cloud_sync.idempotency import IdempotencyStore, IdempotencyConflict
        from .asset_builder import build_asset_from_master

        store = IdempotencyStore(self._fm) if idempotency_key else None
        if store:
            try:
                cached = await store.lookup(
                    owner_id=owner_id,
                    key=idempotency_key,
                    endpoint="upload_with_options",
                    body=request_payload_for_idempotency,
                )
                if cached is not None:
                    return cached["response_body"]
            except IdempotencyConflict:
                raise

        errors: list[dict] = []

        # Stage 1: write the master.
        result = await self.write(
            content,
            file_path=file_path,
            mime_type=mime_type,
            visibility=visibility,
            metadata=metadata,
            user_id=owner_id,
        )
        master_record = await self.db.get_file_async(result.file_id)
        if not master_record:
            raise RuntimeError(f"Master record disappeared after write: {result.file_id}")

        # Stage 2: render variants (best-effort).
        if variants:
            try:
                # variants can be either a list of preset keys (strings)
                # OR a list of ImageVariant dicts. The asset_router uses
                # this path with custom_variants_json; we keep that
                # signature for consistency.
                from .specific_handlers.image_handler import compose_preset, SOCIAL_BASELINE
                variant_specs: list[dict] = []
                if isinstance(variants, list) and variants and isinstance(variants[0], str):
                    # treat as preset name
                    # caller can pass a single string in a list to apply one preset
                    for name in variants:
                        try:
                            _, specs = compose_preset(name)
                            variant_specs.extend(specs)
                        except KeyError:
                            errors.append({"sub_op": "variants", "message": f"unknown preset {name!r}"})
                else:
                    variant_specs = list(variants)  # type: ignore[arg-type]
                if variant_specs:
                    rendered = await self._render_variants_via_image_handler(
                        master_record, variant_specs,
                    )
                    # rendered is a dict[key, AssetVariant] — we don't
                    # need to inline them here; build_asset_from_master
                    # picks up the sibling rows from the DB.
            except Exception as e:
                errors.append({"sub_op": "variants", "message": str(e)})

        # Stage 3: share link (best-effort).
        share_link: dict | None = None
        if share:
            try:
                share_link = await self.permissions.create_share_link_async(
                    "file",
                    result.file_id,
                    permission_level=share.get("permission_level", "read"),
                    expires_at=share.get("expires_at"),
                    max_uses=share.get("max_uses"),
                    user_id=owner_id,
                )
            except Exception as e:
                errors.append({"sub_op": "share_link", "message": str(e)})

        # Stage 4: per-user permissions (best-effort).
        if permissions:
            for grant in permissions:
                try:
                    await self.db.upsert_permission_async({
                        "resource_id": result.file_id,
                        "resource_type": "file",
                        "grantee_id": grant["grantee_id"],
                        "grantee_type": grant.get("grantee_type", "user"),
                        "permission_level": grant.get("permission_level", "read"),
                        "granted_by": owner_id,
                        "expires_at": grant.get("expires_at"),
                    })
                except Exception as e:
                    errors.append({
                        "sub_op": "permission",
                        "grantee_id": grant.get("grantee_id"),
                        "message": str(e),
                    })

        # Build the canonical envelope.
        asset = await build_asset_from_master(
            self._fm, master_record, preset_name=preset,
        )

        envelope: dict = {
            "asset": asset.model_dump(),
            "share_link": share_link,
            "errors": errors,
        }

        if store:
            await store.persist(
                owner_id=owner_id,
                key=idempotency_key,
                endpoint="upload_with_options",
                body=request_payload_for_idempotency,
                status_code=200,
                response_body=envelope,
                resource_id=result.file_id,
                resource_type="file",
            )

        return envelope

    async def _render_variants_via_image_handler(
        self, master_record: dict, variants_to_render: list[dict],
    ) -> dict:
        """Internal: render image variants for a master via the registered
        image handler + persist each as a cld_files row under the
        deterministic ``{master_dir}/v/`` subfolder.

        Idempotent — delegates to :class:`VariantsService` which checks
        for ``(master_id, variant_key)`` rows in cld_files BEFORE
        invoking the image encoder. Reused variants skip the encoder
        and the S3 write entirely.
        """
        if not variants_to_render:
            return {}
        engine = self._fm.sync_engine
        if engine is None:
            return {}
        asset_variants = await engine.variants.render_async(
            master_record,
            variants_specs=variants_to_render,
            signed_ttl=3600,
        )
        # Legacy callers expect dict[str, dict] of url envelopes; keep that
        # shape for back-compat. New callers should use the variants service
        # directly to get AssetVariant pydantic objects.
        return {
            key: {
                "file_id": av.file_id,
                "url": av.url,
                "cdn_url": av.cdn_url,
                "signed_url": av.signed_url,
                "download_url": av.download_url,
            }
            for key, av in asset_variants.items()
        }

    async def mutate_file(
        self,
        file_id: str,
        *,
        user_id: str,
        # Union body — every field optional:
        name: str | None = None,
        folder: str | None = None,
        visibility: str | None = None,
        metadata: dict | None = None,
        share: dict | None = None,
        share_revoke: bool = False,
        permissions: list[dict] | None = None,
        permissions_revoke: list[dict] | None = None,
        variants: list[str] | list[dict] | None = None,
        restore_version: int | None = None,
        restore_from_trash: bool = False,
        copy_to: str | None = None,
        # Idempotency:
        idempotency_key: str | None = None,
        request_payload_for_idempotency: dict | None = None,
    ) -> dict:
        """One-shot PATCH covering every common file mutation.

        Returns ``{"asset": Asset, "share_link": dict|None, "errors": [{"sub_op", "message"}]}``.
        Best-effort atomic — every sub-op runs sequentially; failures
        accumulate in ``errors``; successful sub-ops persist.

        Sub-op order: restore_from_trash → restore_version → rename →
        move → visibility → metadata → share_revoke → share → permissions
        → permissions_revoke → variants → copy_to. The order is chosen
        so a partial failure leaves the most useful subset committed
        (e.g. a rename succeeds before a permission failure).
        """
        from .cloud_sync.idempotency import IdempotencyStore, IdempotencyConflict
        from .asset_builder import build_asset_from_master

        store = IdempotencyStore(self._fm) if idempotency_key else None
        if store:
            try:
                cached = await store.lookup(
                    owner_id=user_id,
                    key=idempotency_key,
                    endpoint=f"mutate_file:{file_id}",
                    body=request_payload_for_idempotency,
                )
                if cached is not None:
                    return cached["response_body"]
            except IdempotencyConflict:
                raise

        errors: list[dict] = []

        # Authorize once. Admin level required if visibility is changing
        # or share-link create / share-link revoke is requested; write
        # otherwise.
        required_level = (
            "admin" if (visibility or share or share_revoke) else "write"
        )
        record = await self.read_record(file_id, user_id=user_id, level=required_level)

        # Stage 0: restore from trash.
        if restore_from_trash:
            try:
                await self.restore(file_id, user_id=user_id)
                record = await self.db.get_file_async(file_id) or record
            except Exception as e:
                errors.append({"sub_op": "restore_from_trash", "message": str(e)})

        # Stage 1: restore a version.
        if restore_version is not None:
            try:
                await self.versions.restore_version_async(
                    file_id, restore_version, user_id=user_id,
                )
                record = await self.db.get_file_async(file_id) or record
            except Exception as e:
                errors.append({
                    "sub_op": "restore_version",
                    "version": restore_version,
                    "message": str(e),
                })

        # Stage 2: rename + move.
        if name is not None:
            try:
                await self.db.update_file_async(file_id, {"file_name": name})
            except Exception as e:
                errors.append({"sub_op": "rename", "message": str(e)})
        if folder is not None:
            try:
                # Resolve the folder by path; create it on demand via the
                # SQL function so the parent chain is atomic.
                client = await self.db._get_async_client()
                folder_resp = await client.rpc(
                    "ensure_folder_chain",
                    {"p_owner_id": user_id, "p_folder_path": folder},
                ).execute()
                new_folder_id = folder_resp.data
                if new_folder_id:
                    await self.db.update_file_async(file_id, {"parent_folder_id": new_folder_id})
            except Exception as e:
                errors.append({"sub_op": "move", "message": str(e)})

        # Stage 3: visibility.
        if visibility and visibility != record.get("visibility"):
            try:
                record = await self.change_visibility(
                    file_id, user_id=user_id, new_visibility=visibility,
                ) or record
                # Cascade to variants (best-effort).
                from .asset_builder import _list_existing_variants_for_master
                for v in await _list_existing_variants_for_master(self._fm, record):
                    try:
                        await self.change_visibility(
                            v["id"], user_id=user_id, new_visibility=visibility,
                        )
                    except Exception as ev:
                        errors.append({
                            "sub_op": "variant_visibility",
                            "variant_id": v["id"],
                            "message": str(ev),
                        })
            except Exception as e:
                errors.append({"sub_op": "visibility", "message": str(e)})

        # Stage 4: metadata merge.
        if metadata is not None:
            try:
                merged = {**(record.get("metadata") or {}), **metadata}
                await self.db.update_file_async(file_id, {"metadata": merged})
            except Exception as e:
                errors.append({"sub_op": "metadata", "message": str(e)})

        # Stage 5: share-link revoke (do this before share create so the
        # caller can revoke-then-recreate in one PATCH).
        if share_revoke:
            try:
                links = await self.db.list_share_links_async("file", file_id)
                for link in links or []:
                    if link.get("is_active"):
                        await self.db.deactivate_share_link_async(link["share_token"])
            except Exception as e:
                errors.append({"sub_op": "share_revoke", "message": str(e)})

        share_link: dict | None = None
        if share:
            try:
                share_link = await self.permissions.create_share_link_async(
                    "file", file_id,
                    permission_level=share.get("permission_level", "read"),
                    expires_at=share.get("expires_at"),
                    max_uses=share.get("max_uses"),
                    user_id=user_id,
                )
            except Exception as e:
                errors.append({"sub_op": "share_link", "message": str(e)})

        # Stage 6: permission grants + revokes.
        if permissions:
            for grant in permissions:
                try:
                    await self.db.upsert_permission_async({
                        "resource_id": file_id,
                        "resource_type": "file",
                        "grantee_id": grant["grantee_id"],
                        "grantee_type": grant.get("grantee_type", "user"),
                        "permission_level": grant.get("permission_level", "read"),
                        "granted_by": user_id,
                        "expires_at": grant.get("expires_at"),
                    })
                except Exception as e:
                    errors.append({
                        "sub_op": "permission",
                        "grantee_id": grant.get("grantee_id"),
                        "message": str(e),
                    })
        if permissions_revoke:
            for revoke in permissions_revoke:
                try:
                    await self.db.delete_permission_async(
                        resource_id=file_id, resource_type="file",
                        grantee_id=revoke["grantee_id"],
                        grantee_type=revoke.get("grantee_type", "user"),
                    )
                except Exception as e:
                    errors.append({
                        "sub_op": "permission_revoke",
                        "grantee_id": revoke.get("grantee_id"),
                        "message": str(e),
                    })

        # Stage 7: variants (only meaningful for image masters).
        if variants:
            try:
                from .specific_handlers.image_handler import compose_preset
                specs: list[dict] = []
                if variants and isinstance(variants[0], str):
                    for name_v in variants:
                        try:
                            _, items = compose_preset(name_v)
                            specs.extend(items)
                        except KeyError:
                            errors.append({"sub_op": "variants", "message": f"unknown preset {name_v!r}"})
                else:
                    specs = list(variants)  # type: ignore[arg-type]
                if specs:
                    await self._render_variants_via_image_handler(record, specs)
            except Exception as e:
                errors.append({"sub_op": "variants", "message": str(e)})

        # Stage 8: copy_to — duplicate the master at a new logical path.
        # The result must be surfaced in the response envelope so the FE
        # can find the new row (audit-flagged Bug B1).
        copy_result: dict | None = None
        if copy_to:
            try:
                src_bytes = await self.router.read_async(record["storage_uri"])
                cr = await self.write(
                    src_bytes,
                    file_path=copy_to,
                    mime_type=record.get("mime_type"),
                    visibility=record.get("visibility") or "private",
                    user_id=user_id,
                    metadata={"copied_from": file_id},
                )
                copy_result = {
                    "file_id": cr.file_id,
                    "file_path": copy_to,
                    "url": cr.url,
                    "cdn_url": cr.cdn_url,
                    "signed_url": cr.signed_url,
                    "download_url": cr.download_url,
                    "visibility": cr.visibility,
                    "size_bytes": cr.size_bytes,
                    "checksum": cr.checksum,
                }
            except Exception as e:
                errors.append({"sub_op": "copy_to", "message": str(e)})

        # Build the final envelope from the (now-updated) master.
        record = await self.db.get_file_async(file_id)
        asset = await build_asset_from_master(self._fm, record)

        envelope: dict = {
            "asset": asset.model_dump(),
            "share_link": share_link,
            "copy": copy_result,  # Bug B1 fix — new file_id is surfaced when copy_to was requested
            "errors": errors,
        }

        if store:
            await store.persist(
                owner_id=user_id,
                key=idempotency_key,
                endpoint=f"mutate_file:{file_id}",
                body=request_payload_for_idempotency,
                status_code=200,
                response_body=envelope,
                resource_id=file_id,
                resource_type="file",
            )

        return envelope

    async def bulk_op(
        self,
        *,
        user_id: str,
        ids: list[str],
        op: str,  # "move" | "delete" | "restore" | "visibility" | "share"
        args: dict | None = None,
        idempotency_key: str | None = None,
        request_payload_for_idempotency: dict | None = None,
    ) -> dict:
        """Bulk operation with a discriminator. Returns per-item status.

        Response shape:
            {
              "op": "delete",
              "results": [
                {"file_id": "...", "ok": true},
                {"file_id": "...", "ok": false, "error": "permission_denied"},
                ...
              ],
              "errors": [],   # operation-level (non-per-id) errors
            }
        """
        from .cloud_sync.idempotency import IdempotencyStore, IdempotencyConflict

        store = IdempotencyStore(self._fm) if idempotency_key else None
        if store:
            try:
                cached = await store.lookup(
                    owner_id=user_id,
                    key=idempotency_key,
                    endpoint=f"bulk_op:{op}",
                    body=request_payload_for_idempotency,
                )
                if cached is not None:
                    return cached["response_body"]
            except IdempotencyConflict:
                raise

        args = args or {}
        results: list[dict] = []
        op_errors: list[dict] = []

        for fid in ids:
            try:
                if op == "delete":
                    if args.get("hard"):
                        await self.hard_delete(fid, user_id=user_id)
                    else:
                        await self.soft_delete(fid, user_id=user_id)
                    results.append({"file_id": fid, "ok": True})
                elif op == "restore":
                    await self.restore(fid, user_id=user_id)
                    results.append({"file_id": fid, "ok": True})
                elif op == "move":
                    new_folder = args.get("target_folder_id")
                    record = await self.read_record(fid, user_id=user_id, level="write")
                    await self.db.update_file_async(fid, {"parent_folder_id": new_folder})
                    results.append({"file_id": fid, "ok": True})
                elif op == "visibility":
                    new_v = args["visibility"]
                    await self.change_visibility(fid, user_id=user_id, new_visibility=new_v)
                    results.append({"file_id": fid, "ok": True})
                elif op == "share":
                    link = await self.permissions.create_share_link_async(
                        "file", fid,
                        permission_level=args.get("permission_level", "read"),
                        expires_at=args.get("expires_at"),
                        max_uses=args.get("max_uses"),
                        user_id=user_id,
                    )
                    results.append({"file_id": fid, "ok": True, "share_link": link})
                else:
                    op_errors.append({"error": f"unknown_op:{op}"})
                    break
            except Exception as e:
                results.append({"file_id": fid, "ok": False, "error": str(e)})

        envelope = {"op": op, "results": results, "errors": op_errors}

        if store:
            await store.persist(
                owner_id=user_id,
                key=idempotency_key,
                endpoint=f"bulk_op:{op}",
                body=request_payload_for_idempotency,
                status_code=200,
                response_body=envelope,
                resource_id=None,
                resource_type=None,
            )

        return envelope

    # ==================================================================
    # PREVIEW + PDF-COMPRESS (FE-team E.16 / E.17)
    # ==================================================================

    async def render_preview(
        self,
        source: bytes | dict,           # bytes OR {"file_id": "..."} MediaRef
        variants: list[dict],           # [{width, height, format, quality, fit}]
        *,
        max_inline_bytes: int = 256 * 1024,
    ) -> list[dict]:
        """Render image variants WITHOUT persisting. Returns one entry per
        spec, each with:

            {
              "preset_id": str,        # echoed from the request spec
              "width": int,
              "height": int,
              "format": "jpeg"|"png"|"webp"|"avif",
              "quality": int | None,
              "size": int,             # encoded bytes
              "notes": [str],          # soft warnings from the renderer

              # Exactly ONE of the next two is present:
              "data_url": "data:image/...;base64,...",  # when size <= max_inline_bytes
              "signed_url": "https://...",              # ephemeral 5-min URL otherwise
              "expires_in": 300,                        # seconds (with signed_url)
            }

        Error entries surface as ``{"preset_id": "...", "error": "..."}``.

        ``source`` is bytes OR a MediaRef-shaped dict with ``file_id``
        (resolved via the router server-side). Used by the FE Image
        Studio preview flow so Sharp leaves the Vercel side.

        Specs format mirrors ``StudioRenderSpec`` — preset_id, width,
        height, format, quality, fit, position, background_color.
        """
        import base64
        # Resolve source bytes.
        if isinstance(source, dict):
            file_id = source.get("file_id")
            if not file_id:
                raise ValueError("preview source dict must contain file_id")
            # ACCESS GATE — a preview is a byte read; enforce access for the
            # requesting user (owner/public/shared), trusted only for internal jobs.
            record = await self.read_record_for_active_user(file_id, level="read")
            if not record:
                raise FileNotFoundError(f"File {file_id!r} not found")
            image_bytes = await self.router.read_async(record["storage_uri"])
        else:
            image_bytes = source

        # Render each spec via the image handler's studio render.
        import asyncio as _asyncio
        results: list[dict] = []
        for spec in variants:
            try:
                rendered = await _asyncio.to_thread(
                    self.image_handler.render_studio_variant, image_bytes, spec,
                )
            except Exception as e:
                results.append({
                    "preset_id": spec.get("preset_id"),
                    "error": str(e),
                })
                continue
            payload = {
                "preset_id": rendered["preset_id"],
                "width": rendered["width"],
                "height": rendered["height"],
                "format": rendered["format"],
                "quality": rendered.get("quality"),
                "size": rendered["size"],
                "fit": rendered.get("fit"),
                "position": rendered.get("position"),
                "notes": rendered.get("notes") or [],
            }
            if rendered["size"] <= max_inline_bytes:
                mime = f"image/{rendered['format'].lower()}"
                if rendered["format"].upper() == "JPEG":
                    mime = "image/jpeg"
                b64 = base64.b64encode(rendered["bytes"]).decode("ascii")
                payload["data_url"] = f"data:{mime};base64,{b64}"
            else:
                # Larger preview — stash under the canonical PREVIEWS
                # system folder (system-files/previews/...) + a 5-min
                # signed URL. No cld_files row is persisted; the
                # ephemeral object is GC'd by an S3 lifecycle rule on
                # the system-files/previews/ prefix.
                from .system_paths import PREVIEWS
                preview_filename = (
                    f"{rendered['preset_id']}-{rendered['width']}x"
                    f"{rendered['height']}.{rendered['format'].lower()}"
                )
                ephemeral_path = PREVIEWS.path(preview_filename)
                bucket = self._fm.sync_engine.config.resolve_s3_bucket()
                from matrx_utils.ctx import get_active_user_id
                uid = get_active_user_id() or "anonymous"
                full_uri = f"s3://{bucket}/{uid}/{ephemeral_path}"
                await self.router.write_async(full_uri, rendered["bytes"])
                # Build a 5-minute signed URL with inline content-type.
                url = await self.router.get_url_async(
                    full_uri,
                    expires_in=5 * 60,
                    response_content_type=f"image/{rendered['format'].lower()}",
                    response_content_disposition='inline; filename="preview.jpg"',
                )
                payload["signed_url"] = url
                payload["expires_in"] = 5 * 60
            results.append(payload)
        return results

    async def compress_pdf(
        self,
        source: bytes | dict,
        *,
        level: int = 3,
        max_size_bytes: int | None = None,
        max_inline_bytes: int = 256 * 1024,
    ) -> dict:
        """Compress a PDF WITHOUT persisting a row. Returns ``{"data_url"}``
        for small results, ``{"signed_url", "expires_in"}`` for larger.

        ``source`` is bytes OR a dict with ``file_id``. ``level`` is the
        compression tier (1 = mildest, 5 = most aggressive). Uses the
        matrx-utils PDF subsystem under the hood.
        """
        import base64
        # Resolve source bytes.
        if isinstance(source, dict):
            file_id = source.get("file_id")
            if not file_id:
                raise ValueError("compress_pdf source dict must contain file_id")
            # ACCESS GATE — enforce access for the requesting user before reading.
            record = await self.read_record_for_active_user(file_id, level="read")
            if not record:
                raise FileNotFoundError(f"File {file_id!r} not found")
            pdf_bytes = await self.router.read_async(record["storage_uri"])
        else:
            pdf_bytes = source

        # Delegate to the matrx-utils PDF handler.
        from .specific_handlers.pdf import compress_pdf_bytes_capped_async
        result = await compress_pdf_bytes_capped_async(
            pdf_bytes, level=level, max_size_bytes=max_size_bytes,
        )
        compressed = result.content
        original_size = len(pdf_bytes)
        compressed_size = len(compressed)
        ratio = round(1 - compressed_size / original_size, 4) if original_size > 0 else 0

        # Key MUST be ``reduction_ratio`` — AssetPdfCompressResponse requires
        # it; the old ``ratio`` key failed response validation and 500'd every
        # /assets/pdf-compress call. Tier metadata from CompressResult rides
        # along so callers can show what actually happened.
        payload: dict = {
            "level_requested": level,
            "level_used": result.level_used,
            "cap_satisfied": result.cap_satisfied,
            "strategy_used": result.strategy_used,
            "original_size": original_size,
            "compressed_size": compressed_size,
            "reduction_ratio": ratio,
        }
        if compressed_size <= max_inline_bytes:
            b64 = base64.b64encode(compressed).decode("ascii")
            payload["data_url"] = f"data:application/pdf;base64,{b64}"
        else:
            from .system_paths import PREVIEWS
            from matrx_utils.ctx import get_active_user_id
            uid = get_active_user_id() or "anonymous"
            bucket = self._fm.sync_engine.config.resolve_s3_bucket()
            ephemeral_path = PREVIEWS.path(f"compressed-{level}.pdf")
            full_uri = f"s3://{bucket}/{uid}/{ephemeral_path}"
            await self.router.write_async(full_uri, compressed)
            url = await self.router.get_url_async(
                full_uri,
                expires_in=5 * 60,
                response_content_type="application/pdf",
                response_content_disposition='inline; filename="compressed.pdf"',
            )
            payload["signed_url"] = url
            payload["expires_in"] = 5 * 60
        return payload


__all__ = ["FileService"]
