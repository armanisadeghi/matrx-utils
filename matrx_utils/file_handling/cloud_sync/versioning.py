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


def _is_version_unique_violation(exc: BaseException) -> bool:
    """True iff ``exc`` is a Postgres 23505 on the (file_id, version_number) key.

    Two concurrent writers of the same variant (e.g. a TUS-finalize
    thumbnail task racing a backfill pass) can both archive version N of
    the same file and both INSERT (file_id, version_number). The DB unique
    index rejects the loser. Because version content is deterministic for a
    given byte sequence, the loser's row is identical to the winner's — the
    collision is benign and re-recording is a no-op.
    """
    msg = str(exc).lower()
    if "23505" not in msg and "unique" not in msg and "duplicate key" not in msg:
        return False
    return "cld_file_versions_file_id_version_number_key" in msg or (
        "file_id" in msg and "version_number" in msg
    )


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
        version_row = self._db.create_version(
            {
                "file_id": file_record["id"],
                "version_number": version_number,
                "storage_uri": version_uri,
                "size_bytes": len(content),
                "checksum": checksum,
                "created_by": user_id or file_record.get("owner_id"),
                "change_summary": change_summary,
            }
        )

        logger.debug("Recorded version %d for file %s", version_number, file_record["id"])
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

        try:
            version_row = await self._db.create_version_async(
                {
                    "file_id": file_record["id"],
                    "version_number": version_number,
                    "storage_uri": version_uri,
                    "size_bytes": len(content),
                    "checksum": checksum,
                    "created_by": user_id or file_record.get("owner_id"),
                    "change_summary": change_summary,
                }
            )
        except Exception as exc:
            if not _is_version_unique_violation(exc):
                raise
            # Benign concurrent re-record — the row is already present with
            # identical (deterministic) content. Return the winner's row.
            logger.debug(
                "Version %d for file %s already recorded (concurrent write); treating as no-op",
                version_number,
                file_record["id"],
            )
            existing = await self._db.get_version_async(file_record["id"], version_number)
            return existing or {
                "file_id": file_record["id"],
                "version_number": version_number,
                "storage_uri": version_uri,
            }

        logger.debug("Recorded version %d for file %s", version_number, file_record["id"])
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
            raise ValueError(f"Version {version_number} not found for file '{file_id}'.")

        # Read old version bytes
        content = self._router.read(old_version["storage_uri"])

        # Write to current location
        self._router.write(file_record["storage_uri"], content)

        # Bump version number
        new_version_number = file_record["current_version"] + 1
        updated = self._db.update_file(
            file_id,
            {
                "current_version": new_version_number,
                "size_bytes": len(content),
                "checksum": old_version.get("checksum"),
            },
        )

        # Record the restore as a new version
        self._db.create_version(
            {
                "file_id": file_id,
                "version_number": new_version_number,
                "storage_uri": self._version_uri(
                    file_id, new_version_number, basename(file_record["file_path"])
                ),
                "size_bytes": len(content),
                "checksum": old_version.get("checksum"),
                "created_by": user_id or file_record.get("owner_id"),
                "change_summary": f"Restored from version {version_number}",
            }
        )

        # Store the restore version bytes
        restore_uri = self._version_uri(
            file_id, new_version_number, basename(file_record["file_path"])
        )
        self._router.write(restore_uri, content)

        logger.info(
            "Restored file %s to version %d (now version %d)",
            file_id,
            version_number,
            new_version_number,
        )
        return updated or file_record

    async def restore_version_async(
        self,
        file_id: str,
        version_number: int,
        user_id: str | None = None,
    ) -> dict:
        """Restore an older version as the current file (async, with rollback).

        State machine:
            1. Load file + target version. Refuse if file is soft-deleted
               or the target version row is missing.
            2. Read old bytes from S3. Refuse if the version backup is
               also missing in storage.
            3. Allocate the new version_number atomically via
               ``bump_version`` (no race on (file_id, version_number)).
            4. Write old bytes to BOTH the new versioned URI AND the
               current storage_uri. If either write fails, roll back the
               version-number bump and raise.
            5. Insert the cld_file_versions row pointing at the new
               versioned URI.
            6. On any DB write failure post-S3, the inconsistency is
               recoverable (S3 has the bytes, DB row is the only thing
               missing) — log loudly so an operator can repair.
        """
        file_record = await self._db.get_file_async(file_id)
        if not file_record:
            raise ValueError(f"File '{file_id}' not found or soft-deleted.")

        old_version = await self._db.get_version_async(file_id, version_number)
        if not old_version:
            raise ValueError(f"Version {version_number} not found for file '{file_id}'.")

        # Stage 1: read old bytes — refuses early if the version backup
        # was hard-deleted from S3 (so we never lose the current file).
        try:
            content = await self._router.read_async(old_version["storage_uri"])
        except Exception as e:
            raise ValueError(
                f"Cannot restore: version {version_number} backup is missing "
                f"from cloud storage ({e})."
            ) from e

        # Stage 2: atomic version bump.
        try:
            client = await self._db._get_async_client()
            r = await client.rpc("bump_version", {"p_file_id": file_id}).execute()
            new_version_number = int(r.data) if r.data is not None else None
        except Exception:
            new_version_number = None
        if not new_version_number:
            # Fallback to the old non-atomic increment.
            new_version_number = file_record["current_version"] + 1

        new_version_uri = self._version_uri(
            file_id, new_version_number, basename(file_record["file_path"])
        )

        # Stage 3: write to versioned location FIRST (ensures backup
        # exists before we touch live).
        try:
            await self._router.write_async(new_version_uri, content)
        except Exception as e:
            # No state changes yet — DB row not created, current bytes intact.
            raise RuntimeError(f"restore failed at versioned-write: {e}") from e

        # Stage 4: write to current location.
        try:
            await self._router.write_async(file_record["storage_uri"], content)
        except Exception as e:
            # Try to roll back the version bump (best-effort).
            logger.error(
                "restore live-write failed for file %s; attempting version rollback: %s",
                file_id,
                e,
                exc_info=True,
            )
            try:
                await self._db.update_file_async(
                    file_id,
                    {
                        "current_version": file_record["current_version"],
                    },
                )
            except Exception:
                logger.error("rollback of current_version also failed", exc_info=True)
            raise RuntimeError(f"restore failed at live-write: {e}") from e

        # Stage 5: update file metadata (size + checksum from old version).
        try:
            updated = await self._db.update_file_async(
                file_id,
                {
                    "size_bytes": len(content),
                    "checksum": old_version.get("checksum"),
                },
            )
        except Exception:
            logger.warning(
                "restore: file metadata update failed for %s (S3 already restored); inconsistency recoverable",
                file_id,
                exc_info=True,
            )
            updated = file_record

        # Stage 6: record the new version row.
        try:
            await self._db.create_version_async(
                {
                    "file_id": file_id,
                    "version_number": new_version_number,
                    "storage_uri": new_version_uri,
                    "size_bytes": len(content),
                    "checksum": old_version.get("checksum"),
                    "created_by": user_id or file_record.get("owner_id"),
                    "change_summary": f"Restored from version {version_number}",
                }
            )
        except Exception:
            logger.warning(
                "restore: version-row insert failed for file %s v%d (S3 written); operator should repair",
                file_id,
                new_version_number,
                exc_info=True,
            )

        # Invalidate byte cache so subsequent reads see the restored content.
        try:
            from matrx_utils.file_handling.cloud_sync.byte_cache import get_byte_cache

            get_byte_cache().invalidate(file_id)
        except Exception:
            pass

        logger.info(
            "Restored file %s to version %d (now version %d)",
            file_id,
            version_number,
            new_version_number,
        )
        return updated or {
            **file_record,
            "current_version": new_version_number,
            "size_bytes": len(content),
        }
