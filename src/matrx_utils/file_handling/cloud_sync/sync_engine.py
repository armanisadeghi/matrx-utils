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
from posixpath import basename, dirname

from .config import CloudSyncConfig
from .db import DatabaseClient
from .models import SyncResult
from .permissions import PermissionsManager
from .versioning import VersionManager

logger = logging.getLogger(__name__)


class SyncEngine:
    """Orchestrates cloud storage, Postgres metadata, permissions, and versioning."""

    def __init__(self, config: CloudSyncConfig, router: object) -> None:
        self._config = config
        self._router = router  # BackendRouter
        self._db = DatabaseClient(config)
        self.permissions = PermissionsManager(self._db, config.user_id)
        self.versions = VersionManager(self._db, router, config)

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

    def _storage_uri(self, file_path: str, user_id: str | None = None) -> str:
        """Build the canonical cloud storage URI for a file path."""
        uid = user_id or self._config.user_id
        bucket = self._config.resolve_s3_bucket()
        backend = self._config.storage_backend
        return f"{backend}://{bucket}/{uid}/{file_path}"

    @staticmethod
    def _checksum(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

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

    def _ensure_folder(self, file_path: str, user_id: str) -> str | None:
        """Ensure the parent folder exists in the database, return its id."""
        folder_path = dirname(file_path)
        if not folder_path or folder_path == ".":
            return None

        existing = self._db.get_folder_by_path(user_id, folder_path)
        if existing:
            return existing["id"]

        # Ensure parent folders recursively
        parent_id = self._ensure_folder(folder_path, user_id)
        folder_name = basename(folder_path)

        result = self._db.upsert_folder({
            "owner_id": user_id,
            "folder_path": folder_path,
            "folder_name": folder_name,
            "parent_id": parent_id,
        })
        return result["id"]

    async def _ensure_folder_async(self, file_path: str, user_id: str) -> str | None:
        folder_path = dirname(file_path)
        if not folder_path or folder_path == ".":
            return None

        existing = await self._db.get_folder_by_path_async(user_id, folder_path)
        if existing:
            return existing["id"]

        parent_id = await self._ensure_folder_async(folder_path, user_id)
        folder_name = basename(folder_path)

        result = await self._db.upsert_folder_async({
            "owner_id": user_id,
            "folder_path": folder_path,
            "folder_name": folder_name,
            "parent_id": parent_id,
        })
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
            uid = user_id or self._config.user_id
            content_bytes = self._to_bytes(content)
            storage_uri = self._storage_uri(file_path, uid)

            # Upload to cloud
            self._router.write(storage_uri, content_bytes)

            # Ensure folder structure
            folder_id = self._ensure_folder(file_path, uid)

            # Compute metadata
            checksum = self._checksum(content_bytes)
            mime = mime_type or self._guess_mime(file_path)

            # Check if file exists
            existing = self._db.get_file_by_path(uid, file_path)
            if existing:
                new_version = existing["current_version"] + 1
                self._db.update_file(existing["id"], {
                    "storage_uri": storage_uri,
                    "file_size": len(content_bytes),
                    "checksum": checksum,
                    "mime_type": mime,
                    "current_version": new_version,
                    "parent_folder_id": folder_id,
                })
                file_record = {**existing, "current_version": new_version}
            else:
                file_record = self._db.upsert_file({
                    "owner_id": uid,
                    "file_path": file_path,
                    "storage_uri": storage_uri,
                    "file_name": basename(file_path),
                    "mime_type": mime,
                    "file_size": len(content_bytes),
                    "checksum": checksum,
                    "parent_folder_id": folder_id,
                })

            # Record version
            self.versions.record_version(
                file_record, content_bytes, checksum=checksum, user_id=uid
            )

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
            uid = user_id or self._config.user_id
            content_bytes = self._to_bytes(content)
            storage_uri = self._storage_uri(file_path, uid)

            await self._router.write_async(storage_uri, content_bytes)

            folder_id = await self._ensure_folder_async(file_path, uid)
            checksum = self._checksum(content_bytes)
            mime = mime_type or self._guess_mime(file_path)

            existing = await self._db.get_file_by_path_async(uid, file_path)
            if existing:
                new_version = existing["current_version"] + 1
                await self._db.update_file_async(existing["id"], {
                    "storage_uri": storage_uri,
                    "file_size": len(content_bytes),
                    "checksum": checksum,
                    "mime_type": mime,
                    "current_version": new_version,
                    "parent_folder_id": folder_id,
                })
                file_record = {**existing, "current_version": new_version}
            else:
                file_record = await self._db.upsert_file_async({
                    "owner_id": uid,
                    "file_path": file_path,
                    "storage_uri": storage_uri,
                    "file_name": basename(file_path),
                    "mime_type": mime,
                    "file_size": len(content_bytes),
                    "checksum": checksum,
                    "parent_folder_id": folder_id,
                })

            await self.versions.record_version_async(
                file_record, content_bytes, checksum=checksum, user_id=uid
            )

            logger.debug("Synced write: %s → %s", file_path, storage_uri)

        except Exception:
            logger.warning("Cloud sync failed for '%s'", file_path, exc_info=True)

    def track_delete(self, file_path: str, user_id: str | None = None) -> None:
        """Soft-delete in database and optionally remove from cloud."""
        try:
            uid = user_id or self._config.user_id
            existing = self._db.get_file_by_path(uid, file_path)
            if existing:
                self._db.soft_delete_file(existing["id"])
                logger.debug("Synced delete: %s", file_path)
        except Exception:
            logger.warning("Cloud sync delete failed for '%s'", file_path, exc_info=True)

    async def track_delete_async(self, file_path: str, user_id: str | None = None) -> None:
        try:
            uid = user_id or self._config.user_id
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
        """Run track_write in a background daemon thread."""
        t = threading.Thread(
            target=self.track_write,
            args=(file_path, content),
            kwargs={"mime_type": mime_type, "user_id": user_id},
            daemon=True,
        )
        t.start()

    def fire_and_forget_delete(
        self, file_path: str, user_id: str | None = None
    ) -> None:
        """Run track_delete in a background daemon thread."""
        t = threading.Thread(
            target=self.track_delete,
            args=(file_path,),
            kwargs={"user_id": user_id},
            daemon=True,
        )
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
        uid = user_id or self._config.user_id
        content_bytes = self._to_bytes(content)
        storage_uri = self._storage_uri(file_path, uid)

        # Upload to cloud
        self._router.write(storage_uri, content_bytes)

        # Ensure folder structure
        folder_id = self._ensure_folder(file_path, uid)

        # Compute metadata
        checksum = self._checksum(content_bytes)
        mime = mime_type or self._guess_mime(file_path)

        # Check if file exists
        existing = self._db.get_file_by_path(uid, file_path)
        is_new = existing is None

        if existing:
            # Permission check for updates on files owned by others
            if existing["owner_id"] != uid:
                self.permissions.require("file", existing["id"], "write", uid)
            new_version = existing["current_version"] + 1
            self._db.update_file(existing["id"], {
                "storage_uri": storage_uri,
                "file_size": len(content_bytes),
                "checksum": checksum,
                "mime_type": mime,
                "current_version": new_version,
                "visibility": visibility,
                "parent_folder_id": folder_id,
                "metadata": metadata or existing.get("metadata", {}),
            })
            file_record = {**existing, "current_version": new_version, "id": existing["id"]}
        else:
            file_record = self._db.upsert_file({
                "owner_id": uid,
                "file_path": file_path,
                "storage_uri": storage_uri,
                "file_name": basename(file_path),
                "mime_type": mime,
                "file_size": len(content_bytes),
                "checksum": checksum,
                "visibility": visibility,
                "parent_folder_id": folder_id,
                "metadata": metadata or {},
            })

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
                self._db.upsert_permission({
                    "resource_id": file_record["id"],
                    "resource_type": "file",
                    "grantee_id": grantee_id,
                    "grantee_type": "user",
                    "permission_level": share_level,
                    "granted_by": uid,
                })
            if visibility == "private":
                self._db.update_file(file_record["id"], {"visibility": "shared"})

        # Generate URL
        url = self._router.get_url(storage_uri, expires_in=3600)

        return SyncResult(
            file_id=file_record["id"],
            storage_uri=storage_uri,
            version_number=file_record.get("current_version", 1),
            file_size=len(content_bytes),
            checksum=checksum,
            is_new=is_new,
            url=url,
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
    ) -> SyncResult:
        """Async version of managed_write()."""
        uid = user_id or self._config.user_id
        content_bytes = self._to_bytes(content)
        storage_uri = self._storage_uri(file_path, uid)

        await self._router.write_async(storage_uri, content_bytes)

        folder_id = await self._ensure_folder_async(file_path, uid)
        checksum = self._checksum(content_bytes)
        mime = mime_type or self._guess_mime(file_path)

        existing = await self._db.get_file_by_path_async(uid, file_path)
        is_new = existing is None

        if existing:
            if existing["owner_id"] != uid:
                await self.permissions.require_async("file", existing["id"], "write", uid)
            new_version = existing["current_version"] + 1
            await self._db.update_file_async(existing["id"], {
                "storage_uri": storage_uri,
                "file_size": len(content_bytes),
                "checksum": checksum,
                "mime_type": mime,
                "current_version": new_version,
                "visibility": visibility,
                "parent_folder_id": folder_id,
                "metadata": metadata or existing.get("metadata", {}),
            })
            file_record = {**existing, "current_version": new_version, "id": existing["id"]}
        else:
            file_record = await self._db.upsert_file_async({
                "owner_id": uid,
                "file_path": file_path,
                "storage_uri": storage_uri,
                "file_name": basename(file_path),
                "mime_type": mime,
                "file_size": len(content_bytes),
                "checksum": checksum,
                "visibility": visibility,
                "parent_folder_id": folder_id,
                "metadata": metadata or {},
            })

        await self.versions.record_version_async(
            file_record,
            content_bytes,
            checksum=checksum,
            change_summary=change_summary,
            user_id=uid,
        )

        if share_with:
            for grantee_id in share_with:
                await self._db.upsert_permission_async({
                    "resource_id": file_record["id"],
                    "resource_type": "file",
                    "grantee_id": grantee_id,
                    "grantee_type": "user",
                    "permission_level": share_level,
                    "granted_by": uid,
                })
            if visibility == "private":
                await self._db.update_file_async(
                    file_record["id"], {"visibility": "shared"}
                )

        url = await self._router.get_url_async(storage_uri, expires_in=3600)

        return SyncResult(
            file_id=file_record["id"],
            storage_uri=storage_uri,
            version_number=file_record.get("current_version", 1),
            file_size=len(content_bytes),
            checksum=checksum,
            is_new=is_new,
            url=url,
        )

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
        uid = user_id or self._config.user_id
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
                raise ValueError(
                    f"Version {version} not found for '{file_path}'."
                )
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
        uid = user_id or self._config.user_id
        file_record = await self._db.get_file_by_path_async(uid, file_path)

        if not file_record:
            raise FileNotFoundError(f"File '{file_path}' not found for user '{uid}'.")

        if file_record["owner_id"] != uid:
            await self.permissions.require_async("file", file_record["id"], "read", uid)

        if version is not None:
            content = await self.versions.read_version_async(file_record["id"], version)
            if content is None:
                raise ValueError(
                    f"Version {version} not found for '{file_path}'."
                )
            return content

        return await self._router.read_async(file_record["storage_uri"])

    def managed_delete(
        self,
        file_path: str,
        *,
        user_id: str | None = None,
        hard_delete: bool = False,
    ) -> bool:
        """Delete a file (soft by default).  Requires admin access."""
        uid = user_id or self._config.user_id
        file_record = self._db.get_file_by_path(uid, file_path)
        if not file_record:
            return False

        if file_record["owner_id"] != uid:
            self.permissions.require("file", file_record["id"], "admin", uid)

        if hard_delete:
            # Remove from cloud storage
            try:
                self._router.delete(file_record["storage_uri"])
            except Exception:
                logger.warning("Failed to delete cloud object: %s", file_record["storage_uri"])

        return self._db.soft_delete_file(file_record["id"])

    async def managed_delete_async(
        self,
        file_path: str,
        *,
        user_id: str | None = None,
        hard_delete: bool = False,
    ) -> bool:
        """Async version of managed_delete()."""
        uid = user_id or self._config.user_id
        file_record = await self._db.get_file_by_path_async(uid, file_path)
        if not file_record:
            return False

        if file_record["owner_id"] != uid:
            await self.permissions.require_async("file", file_record["id"], "admin", uid)

        if hard_delete:
            try:
                await self._router.delete_async(file_record["storage_uri"])
            except Exception:
                logger.warning("Failed to delete cloud object: %s", file_record["storage_uri"])

        return await self._db.soft_delete_file_async(file_record["id"])

    # ------------------------------------------------------------------
    # Listing / querying
    # ------------------------------------------------------------------

    def list_files(
        self,
        folder_path: str | None = None,
        user_id: str | None = None,
    ) -> list[dict]:
        """List files owned by the user, optionally filtered by folder."""
        uid = user_id or self._config.user_id
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
        uid = user_id or self._config.user_id
        folder_id = None
        if folder_path:
            folder = await self._db.get_folder_by_path_async(uid, folder_path)
            folder_id = folder["id"] if folder else "__nonexistent__"
        return await self._db.list_files_async(uid, folder_id)

    def list_folders(
        self,
        parent_path: str | None = None,
        user_id: str | None = None,
    ) -> list[dict]:
        uid = user_id or self._config.user_id
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
        uid = user_id or self._config.user_id
        parent_id = None
        if parent_path:
            parent = await self._db.get_folder_by_path_async(uid, parent_path)
            parent_id = parent["id"] if parent else "__nonexistent__"
        return await self._db.list_folders_async(uid, parent_id)

    def get_file_info(self, file_path: str, user_id: str | None = None) -> dict | None:
        """Get file metadata from the database."""
        uid = user_id or self._config.user_id
        return self._db.get_file_by_path(uid, file_path)

    async def get_file_info_async(
        self, file_path: str, user_id: str | None = None
    ) -> dict | None:
        uid = user_id or self._config.user_id
        return await self._db.get_file_by_path_async(uid, file_path)

    def get_file_url(
        self,
        file_path: str,
        expires_in: int = 3600,
        user_id: str | None = None,
    ) -> str:
        """Get a signed URL for a tracked file, with permission check."""
        uid = user_id or self._config.user_id
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
        uid = user_id or self._config.user_id
        file_record = await self._db.get_file_by_path_async(uid, file_path)
        if not file_record:
            raise FileNotFoundError(f"File '{file_path}' not found for user '{uid}'.")
        if file_record["owner_id"] != uid:
            await self.permissions.require_async("file", file_record["id"], "read", uid)
        return await self._router.get_url_async(
            file_record["storage_uri"], expires_in=expires_in
        )
