"""Version manager for the cloud sync layer.

Tracks file version history in Postgres and stores previous versions
in cloud storage alongside the current file.

Storage layout::

    s3://bucket/user-id/reports/q1.json           ← current (always latest)
    s3://bucket/user-id/.versions/file-uuid/v1/q1.json  ← version 1
    s3://bucket/user-id/.versions/file-uuid/v2/q1.json  ← version 2
    ...

Usage::

    vm = VersionManager(db, router, config)

    # Called automatically by SyncEngine — records a new version
    version = vm.record_version(file_record, content_bytes, checksum)

    # List all versions of a file
    versions = vm.list_versions(file_id)

    # Restore a previous version as current
    result = vm.restore_version(file_id, version_number=2)
"""

from __future__ import annotations

import logging
from posixpath import basename

from .config import CloudSyncConfig
from .db import DatabaseClient

logger = logging.getLogger(__name__)


class VersionManager:
    """Manages file version history: recording, listing, and restoring."""

    def __init__(
        self,
        db: DatabaseClient,
        router: object,  # BackendRouter — imported lazily to avoid cycles
        config: CloudSyncConfig,
    ) -> None:
        self._db = db
        self._router = router
        self._config = config

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _version_uri(self, file_id: str, version_number: int, file_name: str) -> str:
        """Build the storage URI for a specific version."""
        bucket = self._config.resolve_s3_bucket()
        prefix = self._config.version_storage_prefix
        backend = self._config.storage_backend
        return f"{backend}://{bucket}/{prefix}/{file_id}/v{version_number}/{file_name}"

    # ------------------------------------------------------------------
    # Record a new version
    # ------------------------------------------------------------------

    def record_version(
        self,
        file_record: dict,
        content: bytes,
        checksum: str | None = None,
        change_summary: str | None = None,
        user_id: str | None = None,
    ) -> dict:
        """Archive the current version and record it in the versions table.

        Called by SyncEngine after a successful write.  The content has
        already been written to the "current" storage_uri; this method
        copies it to the versioned location and creates the DB record.

        Returns the new version row.
        """
        version_number = file_record.get("current_version", 1)
        file_name = basename(file_record["file_path"])
        version_uri = self._version_uri(file_record["id"], version_number, file_name)

        # Store version bytes
        self._router.write(version_uri, content)

        # Create version record
        version_row = self._db.create_version({
            "file_id": file_record["id"],
            "version_number": version_number,
            "storage_uri": version_uri,
            "file_size": len(content),
            "checksum": checksum,
            "created_by": user_id or file_record.get("owner_id"),
            "change_summary": change_summary,
        })

        logger.debug(
            "Recorded version %d for file %s", version_number, file_record["id"]
        )
        return version_row

    async def record_version_async(
        self,
        file_record: dict,
        content: bytes,
        checksum: str | None = None,
        change_summary: str | None = None,
        user_id: str | None = None,
    ) -> dict:
        """Async version of record_version()."""
        version_number = file_record.get("current_version", 1)
        file_name = basename(file_record["file_path"])
        version_uri = self._version_uri(file_record["id"], version_number, file_name)

        await self._router.write_async(version_uri, content)

        version_row = await self._db.create_version_async({
            "file_id": file_record["id"],
            "version_number": version_number,
            "storage_uri": version_uri,
            "file_size": len(content),
            "checksum": checksum,
            "created_by": user_id or file_record.get("owner_id"),
            "change_summary": change_summary,
        })

        logger.debug(
            "Recorded version %d for file %s", version_number, file_record["id"]
        )
        return version_row

    # ------------------------------------------------------------------
    # List versions
    # ------------------------------------------------------------------

    def list_versions(self, file_id: str) -> list[dict]:
        """Return all versions of a file, newest first."""
        return self._db.list_versions(file_id)

    async def list_versions_async(self, file_id: str) -> list[dict]:
        return await self._db.list_versions_async(file_id)

    # ------------------------------------------------------------------
    # Get a specific version
    # ------------------------------------------------------------------

    def get_version(self, file_id: str, version_number: int) -> dict | None:
        """Return the metadata for a specific version."""
        return self._db.get_version(file_id, version_number)

    async def get_version_async(self, file_id: str, version_number: int) -> dict | None:
        return await self._db.get_version_async(file_id, version_number)

    def read_version(self, file_id: str, version_number: int) -> bytes | None:
        """Read the file content of a specific version from cloud storage."""
        version = self._db.get_version(file_id, version_number)
        if not version:
            return None
        return self._router.read(version["storage_uri"])

    async def read_version_async(self, file_id: str, version_number: int) -> bytes | None:
        version = await self._db.get_version_async(file_id, version_number)
        if not version:
            return None
        return await self._router.read_async(version["storage_uri"])

    # ------------------------------------------------------------------
    # Restore a previous version
    # ------------------------------------------------------------------

    def restore_version(
        self,
        file_id: str,
        version_number: int,
        user_id: str | None = None,
    ) -> dict:
        """Restore a previous version as the current file.

        - Reads the old version's bytes from cloud storage.
        - Writes them to the file's current storage_uri.
        - Bumps current_version on the file record.
        - Records the restore as a new version entry.

        Returns the updated file record.
        """
        file_record = self._db.get_file(file_id)
        if not file_record:
            raise ValueError(f"File '{file_id}' not found.")

        old_version = self._db.get_version(file_id, version_number)
        if not old_version:
            raise ValueError(
                f"Version {version_number} not found for file '{file_id}'."
            )

        # Read old version bytes
        content = self._router.read(old_version["storage_uri"])

        # Write to current location
        self._router.write(file_record["storage_uri"], content)

        # Bump version number
        new_version_number = file_record["current_version"] + 1
        updated = self._db.update_file(file_id, {
            "current_version": new_version_number,
            "file_size": len(content),
            "checksum": old_version.get("checksum"),
        })

        # Record the restore as a new version
        self._db.create_version({
            "file_id": file_id,
            "version_number": new_version_number,
            "storage_uri": self._version_uri(
                file_id, new_version_number, basename(file_record["file_path"])
            ),
            "file_size": len(content),
            "checksum": old_version.get("checksum"),
            "created_by": user_id or file_record.get("owner_id"),
            "change_summary": f"Restored from version {version_number}",
        })

        # Store the restore version bytes
        restore_uri = self._version_uri(
            file_id, new_version_number, basename(file_record["file_path"])
        )
        self._router.write(restore_uri, content)

        logger.info(
            "Restored file %s to version %d (now version %d)",
            file_id, version_number, new_version_number,
        )
        return updated or file_record

    async def restore_version_async(
        self,
        file_id: str,
        version_number: int,
        user_id: str | None = None,
    ) -> dict:
        """Async version of restore_version()."""
        file_record = await self._db.get_file_async(file_id)
        if not file_record:
            raise ValueError(f"File '{file_id}' not found.")

        old_version = await self._db.get_version_async(file_id, version_number)
        if not old_version:
            raise ValueError(
                f"Version {version_number} not found for file '{file_id}'."
            )

        content = await self._router.read_async(old_version["storage_uri"])
        await self._router.write_async(file_record["storage_uri"], content)

        new_version_number = file_record["current_version"] + 1
        updated = await self._db.update_file_async(file_id, {
            "current_version": new_version_number,
            "file_size": len(content),
            "checksum": old_version.get("checksum"),
        })

        restore_uri = self._version_uri(
            file_id, new_version_number, basename(file_record["file_path"])
        )
        await self._router.write_async(restore_uri, content)

        await self._db.create_version_async({
            "file_id": file_id,
            "version_number": new_version_number,
            "storage_uri": restore_uri,
            "file_size": len(content),
            "checksum": old_version.get("checksum"),
            "created_by": user_id or file_record.get("owner_id"),
            "change_summary": f"Restored from version {version_number}",
        })

        logger.info(
            "Restored file %s to version %d (now version %d)",
            file_id, version_number, new_version_number,
        )
        return updated or file_record
