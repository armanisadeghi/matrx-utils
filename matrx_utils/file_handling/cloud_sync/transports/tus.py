"""TUS resumable upload state machine.

Pure storage-layer logic — no FastAPI, no HTTP. The host wraps this with
a thin protocol-marshaling layer that parses TUS headers, maps typed
errors to HTTP status codes, and runs auth + quota pre-flight.

Operations (5):

- :meth:`TUSSessionManager.create_async`   — allocate S3 multipart + insert inflight row
- :meth:`TUSSessionManager.get_async`      — load inflight row (for HEAD's Upload-Offset)
- :meth:`TUSSessionManager.append_async`   — append one chunk (one S3 part)
- :meth:`TUSSessionManager.finalize_async` — complete multipart + insert cld_files row
- :meth:`TUSSessionManager.abort_async`    — abort multipart + mark inflight row aborted

All operations are idempotent on retry — replaying ``create_async`` with
the same ``(owner_id, idempotency_key)`` returns the in-progress row's
state rather than creating a duplicate; replaying ``abort_async`` after
abort succeeds is a no-op. The state lives in ``cld_uploads_inflight``
(packaged migration ``005_tus_uploads_realtime.sql``).
"""

from __future__ import annotations

import asyncio
import base64
import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from matrx_utils import vcprint

from ..db import T_FILES, T_UPLOADS, afiles_table

if TYPE_CHECKING:
    from ..sync_engine import SyncEngine

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tunables. Hosts override at construction time.
# ---------------------------------------------------------------------------

DEFAULT_MAX_SIZE = 5 * 1024 * 1024 * 1024  # 5 GB
DEFAULT_MIN_PART_BYTES = 5 * 1024 * 1024  # S3 multipart minimum (5 MiB)
DEFAULT_MAX_PATCH_BYTES = 256 * 1024 * 1024  # 256 MiB — memory ceiling per PATCH


# ---------------------------------------------------------------------------
# Result + row dataclasses. Typed so callers don't pass dicts around.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TUSCreateResult:
    upload_id: str
    file_id: str
    upload_offset: int  # always 0 for fresh; non-zero for idempotency replay
    upload_length: int
    is_replay: bool = False  # True when an idempotency-key matched an existing row


@dataclass(frozen=True)
class TUSSessionRow:
    upload_id: str
    file_id: str
    owner_id: str
    file_path: str
    bucket: str
    key: str
    multipart_upload_id: str
    upload_length: int
    upload_offset: int
    visibility: str
    mime_type: str | None
    file_name: str
    metadata: dict[str, Any] = field(default_factory=dict)
    parts: list[dict[str, Any]] = field(default_factory=list)
    status: str = "in_progress"


@dataclass(frozen=True)
class TUSAppendResult:
    new_offset: int
    is_final: bool


@dataclass(frozen=True)
class TUSFinalizeResult:
    file_id: str
    file_path: str
    size_bytes: int
    checksum: str | None
    storage_uri: str


# ---------------------------------------------------------------------------
# Typed errors. The router maps these to HTTP status codes.
# ---------------------------------------------------------------------------


class TUSError(Exception):
    """Base class for the TUS state-machine errors."""


class UploadNotFound(TUSError):
    """``upload_id`` doesn't match an in-progress inflight row."""


class UploadCompleted(TUSError):
    """Operation attempted on an upload that is already completed/aborted."""


class OffsetMismatch(TUSError):
    """Client's Upload-Offset disagrees with the server's tracked offset."""

    def __init__(self, server_offset: int, client_offset: int) -> None:
        self.server_offset = server_offset
        self.client_offset = client_offset
        super().__init__(f"Server has {server_offset}; client sent {client_offset}")


class PartTooSmall(TUSError):
    """A non-final PATCH was below the S3 multipart minimum part size."""


class ExceedsLength(TUSError):
    """Append would push the offset past the declared Upload-Length."""


class PatchTooLarge(TUSError):
    """Single PATCH exceeded the configured per-chunk memory ceiling."""


class S3NotConfigured(TUSError):
    """The S3 backend is not wired — TUS requires multipart upload."""


class S3Failure(TUSError):
    """An S3 multipart operation failed; ``cause`` carries the boto exception."""

    def __init__(self, op: str, cause: Exception) -> None:
        self.op = op
        self.cause = cause
        super().__init__(f"S3 {op} failed: {cause!r}")


# ---------------------------------------------------------------------------
# Manager.
# ---------------------------------------------------------------------------


def _utcnow_iso() -> str:
    return datetime.now(UTC).isoformat()


def _row_to_session(row: dict[str, Any]) -> TUSSessionRow:
    return TUSSessionRow(
        upload_id=row["id"],
        file_id=row["file_id"],
        owner_id=row["owner_id"],
        file_path=row["file_path"],
        bucket=row["bucket"],
        key=row["key"],
        multipart_upload_id=row["multipart_upload_id"],
        upload_length=int(row["upload_length"]),
        upload_offset=int(row["upload_offset"]),
        visibility=row.get("visibility") or "private",
        mime_type=row.get("mime_type"),
        file_name=row.get("file_name") or "",
        metadata=dict(row.get("metadata") or {}),
        parts=list(row.get("parts") or []),
        status=row.get("status") or "in_progress",
    )


class TUSSessionManager:
    """Portable TUS state machine.

    Construct via :attr:`SyncEngine.tus` or directly when wiring a custom
    upload pipeline. The manager owns all S3 multipart ops + every
    ``cld_uploads_inflight`` write; callers handle the TUS protocol
    (headers, status codes), auth, and quota policy.
    """

    def __init__(
        self,
        engine: SyncEngine,
        *,
        max_size: int = DEFAULT_MAX_SIZE,
        min_part_bytes: int = DEFAULT_MIN_PART_BYTES,
        max_patch_bytes: int = DEFAULT_MAX_PATCH_BYTES,
    ) -> None:
        self._engine = engine
        self.max_size = max_size
        self.min_part_bytes = min_part_bytes
        self.max_patch_bytes = max_patch_bytes

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    async def create_async(
        self,
        *,
        owner_id: str,
        file_path: str,
        upload_length: int,
        mime_type: str | None = None,
        visibility: str = "private",
        metadata: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> TUSCreateResult:
        if upload_length < 0 or upload_length > self.max_size:
            raise ExceedsLength(f"upload_length {upload_length} exceeds max {self.max_size}")

        db = self._engine.db
        db_client = await db._get_async_client()

        # Idempotency replay: an in-progress row with the same key wins.
        if idempotency_key:
            try:
                resp = (
                    await afiles_table(db_client, T_UPLOADS)
                    .select("id,file_id,upload_offset,upload_length")
                    .eq("owner_id", owner_id)
                    .eq("idempotency_key", idempotency_key)
                    .eq("status", "in_progress")
                    .maybe_single()
                    .execute()
                )
                existing = resp.data if resp else None
            except Exception:
                existing = None
            if existing:
                return TUSCreateResult(
                    upload_id=existing["id"],
                    file_id=existing["file_id"],
                    upload_offset=int(existing["upload_offset"]),
                    upload_length=int(existing["upload_length"]),
                    is_replay=True,
                )

        # Resolve bucket. Public assets land in the CDN-fronted public bucket.
        if not self._engine.router.is_configured("s3"):
            raise S3NotConfigured("S3 backend is not configured")
        backend = self._engine.router.s3

        file_id = str(uuid.uuid4())
        bucket = self._engine.config.resolve_s3_bucket()
        if visibility == "public":
            from ..cdn import public_bucket

            bucket = public_bucket() or bucket

        # Canonical key — owner-scoped + file-id. No rekey backfill needed.
        key = f"{owner_id}/{file_id}"

        s3_client = backend._get_client()
        # Phase 1.5 — open the multipart with FULL_OBJECT SHA-256 so
        # complete_multipart_upload returns the real SHA-256 of the
        # original bytes (not the composite per-part hash). That's the
        # value we need to drive dedup; the composite hash is chunk-shape
        # dependent and would dedup nothing.
        mpu_kw: dict[str, Any] = {
            "Bucket": bucket,
            "Key": key,
            "ChecksumAlgorithm": "SHA256",
            "ChecksumType": "FULL_OBJECT",
        }
        if mime_type:
            mpu_kw["ContentType"] = mime_type
        try:
            mpu = await asyncio.to_thread(s3_client.create_multipart_upload, **mpu_kw)
        except TypeError:
            # Older boto3 that doesn't know ChecksumType=FULL_OBJECT.
            # Degrade to composite checksum mode — finalize will skip the
            # dedup lookup (checksum stays NULL) rather than write a
            # bogus value. Same fallback shape as the Phase 1 behaviour
            # this PR replaces.
            mpu_kw.pop("ChecksumType", None)
            mpu_kw.pop("ChecksumAlgorithm", None)
            try:
                mpu = await asyncio.to_thread(s3_client.create_multipart_upload, **mpu_kw)
            except Exception as e:
                raise S3Failure("create_multipart_upload", e)
        except Exception as e:
            raise S3Failure("create_multipart_upload", e)

        upload_id = str(uuid.uuid4())
        # Best-effort derive a filename from the path tail.
        file_name = (file_path.rsplit("/", 1)[-1]) or file_id
        # Strip the two header-supplied keys we promote to first-class columns.
        clean_metadata = {
            k: v for k, v in (metadata or {}).items() if k not in ("filename", "filepath")
        }
        row: dict[str, Any] = {
            "id": upload_id,
            "owner_id": owner_id,
            "file_id": file_id,
            "file_path": file_path,
            "bucket": bucket,
            "key": key,
            "multipart_upload_id": mpu["UploadId"],
            "upload_length": upload_length,
            "upload_offset": 0,
            "visibility": visibility,
            "mime_type": mime_type,
            "file_name": file_name,
            "metadata": clean_metadata,
            "parts": [],
            "status": "in_progress",
        }
        if idempotency_key:
            row["idempotency_key"] = idempotency_key

        try:
            await afiles_table(db_client, T_UPLOADS).insert(row).execute()
        except Exception as e:
            # Don't leak the S3 multipart on insert failure.
            try:
                await asyncio.to_thread(
                    s3_client.abort_multipart_upload,
                    Bucket=bucket,
                    Key=key,
                    UploadId=mpu["UploadId"],
                )
            except Exception:
                pass
            raise S3Failure("inflight_insert", e)

        return TUSCreateResult(
            upload_id=upload_id,
            file_id=file_id,
            upload_offset=0,
            upload_length=upload_length,
            is_replay=False,
        )

    # ------------------------------------------------------------------
    # Get
    # ------------------------------------------------------------------

    async def get_async(
        self,
        *,
        upload_id: str,
        owner_id: str,
    ) -> TUSSessionRow | None:
        db_client = await self._engine.db._get_async_client()
        try:
            resp = (
                await afiles_table(db_client, T_UPLOADS)
                .select("*")
                .eq("id", upload_id)
                .eq("owner_id", owner_id)
                .maybe_single()
                .execute()
            )
        except Exception:
            return None
        if not resp or not resp.data:
            return None
        return _row_to_session(resp.data)

    # ------------------------------------------------------------------
    # Append
    # ------------------------------------------------------------------

    async def append_async(
        self,
        *,
        upload_id: str,
        owner_id: str,
        body: bytes,
        client_offset: int,
    ) -> TUSAppendResult:
        session = await self.get_async(upload_id=upload_id, owner_id=owner_id)
        if not session:
            raise UploadNotFound(f"Upload {upload_id!r} not found for owner")
        if session.status != "in_progress":
            raise UploadCompleted(f"Upload {upload_id!r} status={session.status!r}")

        if len(body) > self.max_patch_bytes:
            raise PatchTooLarge(f"PATCH body {len(body)}B exceeds max {self.max_patch_bytes}B")

        if client_offset != session.upload_offset:
            raise OffsetMismatch(session.upload_offset, client_offset)

        new_offset = session.upload_offset + len(body)
        if new_offset > session.upload_length:
            raise ExceedsLength(
                f"Adding {len(body)}B would exceed declared length {session.upload_length}"
            )

        is_final = new_offset == session.upload_length
        if not is_final and len(body) < self.min_part_bytes:
            raise PartTooSmall(f"Non-final chunk must be >= {self.min_part_bytes}B")

        if not self._engine.router.is_configured("s3"):
            raise S3NotConfigured("S3 backend is not configured")
        s3_client = self._engine.router.s3._get_client()

        # One PATCH = one S3 part.
        part_number = len(session.parts) + 1
        try:
            part_resp = await asyncio.to_thread(
                s3_client.upload_part,
                Bucket=session.bucket,
                Key=session.key,
                UploadId=session.multipart_upload_id,
                PartNumber=part_number,
                Body=body,
            )
        except Exception as e:
            raise S3Failure("upload_part", e)

        new_parts = list(session.parts) + [{"PartNumber": part_number, "ETag": part_resp["ETag"]}]
        db_client = await self._engine.db._get_async_client()
        await (
            afiles_table(db_client, T_UPLOADS)
            .update(
                {
                    "upload_offset": new_offset,
                    "parts": new_parts,
                    "updated_at": _utcnow_iso(),
                }
            )
            .eq("id", upload_id)
            .execute()
        )
        return TUSAppendResult(new_offset=new_offset, is_final=is_final)

    # ------------------------------------------------------------------
    # Finalize
    # ------------------------------------------------------------------

    async def finalize_async(
        self,
        *,
        upload_id: str,
        owner_id: str,
        extra_metadata: dict[str, Any] | None = None,
    ) -> TUSFinalizeResult:
        """Complete the S3 multipart, insert the cld_files row, mark inflight done.

        ``extra_metadata`` is merged on top of the inflight row's metadata
        (e.g. request_id, fingerprint hash). Host callers stamp request-
        scoped context this way without the manager needing to know what
        AppContext looks like.
        """
        session = await self.get_async(upload_id=upload_id, owner_id=owner_id)
        if not session:
            raise UploadNotFound(f"Upload {upload_id!r} not found for owner")
        if session.status != "in_progress":
            raise UploadCompleted(f"Upload {upload_id!r} status={session.status!r}")

        if not self._engine.router.is_configured("s3"):
            raise S3NotConfigured("S3 backend is not configured")
        s3_client = self._engine.router.s3._get_client()

        try:
            complete_resp = await asyncio.to_thread(
                s3_client.complete_multipart_upload,
                Bucket=session.bucket,
                Key=session.key,
                UploadId=session.multipart_upload_id,
                MultipartUpload={"Parts": session.parts},
            )
        except Exception as e:
            raise S3Failure("complete_multipart_upload", e)

        # Phase 1.5 — full-object SHA-256 from S3, captured server-side.
        # create_async opened the multipart with
        # ``ChecksumAlgorithm='SHA256', ChecksumType='FULL_OBJECT'`` so the
        # complete response carries the real SHA-256 of the original bytes
        # (base64-encoded). Decode to the 64-char hex form the rest of the
        # dedup system uses. If S3 didn't return one (older bucket config
        # that refused FULL_OBJECT — see the TypeError fallback in
        # create_async), checksum stays NULL and this row is excluded from
        # the dedup canonical index, same as Phase 1.
        checksum: str | None = None
        checksum_b64 = (
            complete_resp.get("ChecksumSHA256") if isinstance(complete_resp, dict) else None
        )
        if checksum_b64:
            try:
                checksum = base64.b64decode(checksum_b64).hex()
            except Exception:
                logger.warning(
                    "tus.finalize: invalid ChecksumSHA256 from S3 (%r); "
                    "row will land with checksum NULL",
                    checksum_b64,
                )
                checksum = None

        # Defensive HEAD — authoritative size after S3 confirms.
        try:
            head = await asyncio.to_thread(
                s3_client.head_object,
                Bucket=session.bucket,
                Key=session.key,
            )
            actual_size = int(head.get("ContentLength") or session.upload_offset)
        except Exception:
            actual_size = session.upload_offset

        backend_name = self._engine.config.storage_backend
        storage_uri = f"{backend_name}://{session.bucket}/{session.key}"
        # Canonical key == native key for TUS uploads — no rekey backfill.

        file_path = session.file_path

        merged_metadata = dict(session.metadata)
        if extra_metadata:
            for k, v in extra_metadata.items():
                merged_metadata.setdefault(k, v)

        # Phase 1.5 — content-hash dedup gate. Mirrors the gate inside
        # ``SyncEngine.managed_write_async``: brand-new ROOT inserts consult
        # the canonical row first; a scope-matching hit short-circuits
        # (delete the just-assembled S3 object, point the inflight row at
        # the canonical file_id, no cld_files INSERT). Derivative writes
        # (parent_file_id / derivation_kind in metadata) bypass the lookup
        # so variants of distinct parents don't alias.
        org_id_for_dedup = merged_metadata.get("organization_id")
        is_derivative_write = (
            merged_metadata.get("parent_file_id") is not None
            or merged_metadata.get("derivation_kind") is not None
        )
        if checksum and not is_derivative_write:
            from matrx_utils.file_handling.dedup import lookup_existing_async

            dedup_lookup = await lookup_existing_async(
                self._engine.db,
                checksum=checksum,
                owner_id=owner_id,
                organization_id=org_id_for_dedup,
            )
            if dedup_lookup.has_duplicate and dedup_lookup.existing is not None:
                return await self._finalize_dedup_hit_async(
                    session=session,
                    upload_id=upload_id,
                    existing_row=dedup_lookup.existing,
                    checksum=checksum,
                    actual_size=actual_size,
                )

        # Resolve parent folder chain (use the existing RPC). Only matters
        # for the INSERT path — dedup hits skip this above.
        db_client = await self._engine.db._get_async_client()
        parent_path = "/".join(file_path.split("/")[:-1])
        parent_id: str | None = None
        if parent_path:
            try:
                r = await db_client.rpc(
                    "ensure_folder_chain",
                    {"p_owner_id": owner_id, "p_folder_path": parent_path},
                ).execute()
                parent_id = r.data if isinstance(r.data, str) else None
            except Exception:
                parent_id = None

        new_row = {
            "id": session.file_id,
            # files.files owner column is the canonical `created_by` (the
            # 2026 DB canonicalization renamed owner_id). This is a DIRECT
            # files insert that bypasses DatabaseClient.upsert_file's
            # owner_id->created_by shim, so write the canonical column here.
            "created_by": owner_id,
            "file_path": file_path,
            "storage_uri": storage_uri,
            # canonical_storage_uri not written — consolidated into storage_uri
            # by migration 007 (storage_uri is already the canonical file_id URI).
            "file_name": session.file_name,
            "mime_type": session.mime_type,
            "size_bytes": actual_size,
            "checksum": checksum,
            "visibility": session.visibility,
            "parent_folder_id": parent_id,
            "metadata": merged_metadata,
        }
        try:
            await afiles_table(db_client, T_FILES).insert(new_row).execute()
        except Exception as insert_exc:
            # Race: a concurrent TUS finalize (or managed_write_async) of
            # the same content won the canonical slot between our lookup
            # and this INSERT. Recover by re-querying for the winner,
            # deleting the orphan S3 object we just assembled, and
            # returning the winner's identity. Mirrors the recovery in
            # ``SyncEngine.managed_write_async``.
            from ..sync_engine import SyncEngine

            if (
                not is_derivative_write
                and checksum
                and SyncEngine._is_dedup_unique_violation(insert_exc)
            ):
                from matrx_utils.file_handling.dedup import lookup_existing_async

                winner_lookup = await lookup_existing_async(
                    self._engine.db,
                    checksum=checksum,
                    owner_id=owner_id,
                    organization_id=org_id_for_dedup,
                )
                if winner_lookup.has_duplicate and winner_lookup.existing is not None:
                    return await self._finalize_dedup_hit_async(
                        session=session,
                        upload_id=upload_id,
                        existing_row=winner_lookup.existing,
                        checksum=checksum,
                        actual_size=actual_size,
                    )
            raise S3Failure("cld_files_insert", insert_exc)

        # Shielded inflight transition. Without the shield, a client
        # disconnect between cld_files INSERT and this UPDATE leaves the
        # inflight row 'in_progress' while a perfectly good cld_files row
        # exists — the TUS cleanup loop would later abort an
        # already-completed upload. Phase 2 doctrine: cancellation cannot
        # split a two-write commit. See PHASE_1_LESSONS_LEARNED.md §1.
        await asyncio.shield(
            afiles_table(db_client, T_UPLOADS)
            .update(
                {
                    "upload_offset": actual_size,
                    "status": "completed",
                    "updated_at": _utcnow_iso(),
                }
            )
            .eq("id", upload_id)
            .execute()
        )

        # Best-effort thumbnail. The processor handles "not a thumbnailable
        # mime" / "no s3" / etc. internally — we don't propagate its errors.
        try:
            from ..processing import generate_thumbnail_for_file

            asyncio.create_task(generate_thumbnail_for_file(self._engine.fm, session.file_id))
        except Exception:
            pass

        return TUSFinalizeResult(
            file_id=session.file_id,
            file_path=file_path,
            size_bytes=actual_size,
            checksum=checksum,
            storage_uri=storage_uri,
        )

    # ------------------------------------------------------------------
    # Dedup hit — shared finish path used by both the pre-INSERT lookup
    # and the post-INSERT race recovery.
    # ------------------------------------------------------------------

    async def _finalize_dedup_hit_async(
        self,
        *,
        session: TUSSessionRow,
        upload_id: str,
        existing_row: dict[str, Any],
        checksum: str,
        actual_size: int,
    ) -> TUSFinalizeResult:
        """Wrap up a TUS upload that matched an already-existing canonical row.

        The just-assembled S3 object is orphaned (it's identical to the
        canonical row's storage_uri by definition), so we delete it.
        The inflight row gets marked completed with a metadata pointer at
        the canonical file_id so the audit trail records what happened.
        No cld_files INSERT — caller uses the returned canonical file_id.
        """
        if self._engine.router.is_configured("s3"):
            s3_client = self._engine.router.s3._get_client()
            try:
                await asyncio.to_thread(
                    s3_client.delete_object,
                    Bucket=session.bucket,
                    Key=session.key,
                )
            except Exception:
                logger.warning(
                    "tus.finalize: orphan S3 cleanup failed for %s/%s after dedup hit",
                    session.bucket,
                    session.key,
                    exc_info=True,
                )

        canonical_id = str(existing_row["id"])
        canonical_storage_uri = (
            existing_row.get("canonical_storage_uri") or existing_row.get("storage_uri") or ""
        )

        # Shielded inflight transition — see the comment in finalize_async
        # above on why this can't be split by a client disconnect.
        db_client = await self._engine.db._get_async_client()
        await asyncio.shield(
            afiles_table(db_client, T_UPLOADS)
            .update(
                {
                    "upload_offset": actual_size,
                    "status": "completed",
                    "metadata": {
                        **session.metadata,
                        "dedup_winner_file_id": canonical_id,
                        "dedup_checksum": checksum,
                    },
                    "updated_at": _utcnow_iso(),
                }
            )
            .eq("id", upload_id)
            .execute()
        )

        return TUSFinalizeResult(
            file_id=canonical_id,
            file_path=existing_row.get("file_path") or session.file_path,
            size_bytes=int(existing_row.get("size_bytes") or actual_size),
            checksum=checksum,
            storage_uri=canonical_storage_uri,
        )

    # ------------------------------------------------------------------
    # Abort
    # ------------------------------------------------------------------

    async def abort_async(self, *, upload_id: str, owner_id: str) -> None:
        """Abort the multipart + mark the row aborted. Idempotent.

        Returns silently when the upload is already completed/aborted or
        doesn't exist — the protocol layer maps "no in-progress row" to
        a 404 itself.
        """
        session = await self.get_async(upload_id=upload_id, owner_id=owner_id)
        if not session or session.status != "in_progress":
            raise UploadNotFound(f"Upload {upload_id!r} not in progress")

        if self._engine.router.is_configured("s3"):
            try:
                await asyncio.to_thread(
                    self._engine.router.s3._get_client().abort_multipart_upload,
                    Bucket=session.bucket,
                    Key=session.key,
                    UploadId=session.multipart_upload_id,
                )
            except Exception as e:
                vcprint(
                    f"[tus.abort] s3 abort failed (continuing): {e!r}",
                    color="yellow",
                )

        db_client = await self._engine.db._get_async_client()
        await (
            afiles_table(db_client, T_UPLOADS)
            .update({"status": "aborted", "updated_at": _utcnow_iso()})
            .eq("id", upload_id)
            .execute()
        )


__all__ = [
    "TUSSessionManager",
    "TUSSessionRow",
    "TUSCreateResult",
    "TUSAppendResult",
    "TUSFinalizeResult",
    "TUSError",
    "UploadCompleted",
    "UploadNotFound",
    "OffsetMismatch",
    "PartTooSmall",
    "ExceedsLength",
    "PatchTooLarge",
    "S3Failure",
    "S3NotConfigured",
    "DEFAULT_MAX_SIZE",
    "DEFAULT_MIN_PART_BYTES",
    "DEFAULT_MAX_PATCH_BYTES",
]
