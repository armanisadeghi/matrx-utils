"""Phase 1 — managed_write_async dedup gate.

Mirrors test_tus_dedup.py for the original Phase 1 seam in
``packages/matrx-utils/matrx_utils/file_handling/cloud_sync/sync_engine.py``:

  * Brand-new ROOT inserts consult ``dedup.lookup_existing_async`` before
    the S3 PUT. A scope-matching hit short-circuits — no router write,
    no INSERT — and returns the canonical row's ``SyncResult`` with
    ``is_new=False``.
  * Derivatives (``parent_file_id`` / ``derivation_kind`` in EITHER
    kwargs OR metadata) bypass the lookup so byte-identical variants of
    distinct parents are intentionally separate rows. The metadata
    branch is the one caught by the post-flight subagent on Phase 1 —
    legacy callers stamp ``parent_file_id`` into ``metadata`` after the
    write via an UPDATE, so the dedup gate must read both signals.
  * Race recovery on the INSERT: the unique-violation on
    ``cld_files_dedup_canonical`` is detected, the winner is re-queried,
    the orphan S3 object is deleted, and the caller gets the winner's
    ``SyncResult``.

Stub the engine's sub-components rather than spinning up a real
``SyncEngine`` — the gate's logic is independent of the surrounding
DatabaseClient / PermissionsManager / VersionManager plumbing. Same
pattern as the TUS tests.
"""

from __future__ import annotations

import hashlib
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from matrx_utils.file_handling.cloud_sync.sync_engine import SyncEngine
from matrx_utils.file_handling.dedup import DedupLookupResult

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


USER_ID = "user-1"
FILE_PATH = "docs/q1.pdf"


def _make_engine(
    *,
    existing_at_path: dict[str, Any] | None = None,
    upsert_raises: BaseException | None = None,
    inserted_id: str = "new-file-id-0001",
) -> SyncEngine:
    """Build a SyncEngine without running its heavy ``__init__``.

    Replaces ``_db`` / ``_router`` / ``permissions`` / ``versions`` with
    AsyncMocks so the gate logic runs in isolation. ``object.__new__``
    sidesteps DatabaseClient construction (which would otherwise try to
    resolve Supabase credentials at import time).
    """
    engine = object.__new__(SyncEngine)
    config = MagicMock()
    config.user_id = USER_ID
    config.storage_backend = "s3"
    config.resolve_s3_bucket = MagicMock(return_value="test-bucket")
    engine._config = config

    router = MagicMock()
    router.write_async = AsyncMock(return_value=None)
    router.delete_async = AsyncMock(return_value=None)
    router.get_url_async = AsyncMock(return_value="https://cdn/test")
    engine._router = router

    db = MagicMock()
    db.get_file_by_path_async = AsyncMock(return_value=existing_at_path)
    db.upsert_file_async = (
        AsyncMock(side_effect=upsert_raises)
        if upsert_raises is not None
        else AsyncMock(
            return_value={
                "id": inserted_id,
                "owner_id": USER_ID,
                "file_path": FILE_PATH,
                "current_version": 1,
                "storage_uri": f"s3://test-bucket/{USER_ID}/{inserted_id}",
            }
        )
    )
    db.update_file_async = AsyncMock(return_value=None)
    db.upsert_permission_async = AsyncMock(return_value=None)
    db.ensure_personal_organization_async = AsyncMock(return_value="org-personal-0001")
    engine._db = db

    permissions = MagicMock()
    permissions.require_async = AsyncMock(return_value=None)
    engine.permissions = permissions

    versions = MagicMock()
    versions.record_version_async = AsyncMock(return_value=None)
    engine.versions = versions

    engine._variants_service = None
    engine._fm_ref = None

    # _ensure_folder_async returns a folder_id; the value doesn't matter
    # to the gate — only that the insert payload carries something.
    engine._ensure_folder_async = AsyncMock(  # type: ignore[method-assign]
        return_value="folder-id-x"
    )
    # build_urls_for_record_async returns the four URL flavours; the
    # gate uses them verbatim. Stub a fixed shape.
    engine.build_urls_for_record_async = AsyncMock(  # type: ignore[method-assign]
        return_value={
            "url": "https://cdn/test",
            "cdn_url": "https://cdn/test",
            "signed_url": "https://cdn/test?signed",
            "download_url": "https://cdn/test?download",
            "signed_url_expires_at": None,
        }
    )
    return engine


def _existing_row(file_id: str = "canonical-existing-0001") -> dict[str, Any]:
    return {
        "id": file_id,
        "file_path": "docs/already_here.pdf",
        "storage_uri": f"s3://test-bucket/{USER_ID}/{file_id}",
        "canonical_storage_uri": f"s3://test-bucket/{USER_ID}/{file_id}",
        "size_bytes": 12,
        "checksum": hashlib.sha256(b"prev").hexdigest(),
        "owner_id": USER_ID,
        "current_version": 3,
        "visibility": "private",
        "mime_type": "application/pdf",
    }


# ---------------------------------------------------------------------------
# 1. Dedup HIT — short-circuits before router write and DB insert
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_dedup_hit_short_circuits_and_returns_canonical():
    content = b"the same content uploaded twice"
    expected_hex = hashlib.sha256(content).hexdigest()
    canonical = _existing_row()
    engine = _make_engine()

    with patch(
        "matrx_utils.file_handling.dedup.lookup_existing_async",
        AsyncMock(
            return_value=DedupLookupResult(
                checksum=expected_hex,
                existing=canonical,
                scope="owner",
            )
        ),
    ) as lookup_mock:
        result = await engine.managed_write_async(FILE_PATH, content)

    assert lookup_mock.called
    assert result.file_id == canonical["id"]
    assert result.checksum == expected_hex
    assert result.is_new is False
    assert result.storage_uri == canonical["storage_uri"]
    # No S3 PUT.
    engine._router.write_async.assert_not_called()
    # No INSERT.
    engine._db.upsert_file_async.assert_not_called()
    # No version recorded — it's the canonical row's version, untouched.
    engine.versions.record_version_async.assert_not_called()


# ---------------------------------------------------------------------------
# 2. Dedup MISS — INSERT proceeds normally, lookup was consulted
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_dedup_miss_proceeds_to_insert():
    content = b"genuinely new content"
    expected_hex = hashlib.sha256(content).hexdigest()
    engine = _make_engine()

    with patch(
        "matrx_utils.file_handling.dedup.lookup_existing_async",
        AsyncMock(
            return_value=DedupLookupResult(
                checksum=expected_hex,
                existing=None,
                scope="none",
            )
        ),
    ) as lookup_mock:
        result = await engine.managed_write_async(FILE_PATH, content)

    assert lookup_mock.called
    assert result.is_new is True
    assert result.checksum == expected_hex
    engine._router.write_async.assert_called_once()
    engine._db.upsert_file_async.assert_called_once()
    # The insert payload carries the computed checksum so the unique
    # index can enforce future dedup decisions.
    payload = engine._db.upsert_file_async.call_args.args[0]
    assert payload["checksum"] == expected_hex
    assert payload["file_path"] == FILE_PATH
    assert payload["owner_id"] == USER_ID


# ---------------------------------------------------------------------------
# 3. Derivative bypass via kwarg — parent_file_id skips the lookup
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_parent_file_id_kwarg_bypasses_dedup_lookup():
    content = b"identical blank page bytes"
    engine = _make_engine()

    with patch(
        "matrx_utils.file_handling.dedup.lookup_existing_async",
        AsyncMock(),
    ) as lookup_mock:
        result = await engine.managed_write_async(
            FILE_PATH,
            content,
            parent_file_id="parent-pdf-1",
        )

    assert not lookup_mock.called, (
        "Derivative write (parent_file_id kwarg) must bypass dedup lookup"
    )
    assert result.is_new is True
    engine._router.write_async.assert_called_once()
    # The lineage column landed on the INSERT.
    payload = engine._db.upsert_file_async.call_args.args[0]
    assert payload.get("parent_file_id") == "parent-pdf-1"


# ---------------------------------------------------------------------------
# 4. Derivative bypass via metadata — the post-flight subagent finding
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_parent_file_id_in_metadata_bypasses_dedup_lookup():
    """Legacy promotion pattern: caller writes the row with
    ``parent_file_id`` ONLY in metadata (not as a kwarg) and follows up
    with an UPDATE that copies it to the column. Without reading
    metadata, byte-identical blank-page renders from two different PDFs
    would alias across documents — the bug the Phase 1 post-flight
    subagent caught."""
    content = b"identical blank page bytes from a different pdf"
    engine = _make_engine()

    with patch(
        "matrx_utils.file_handling.dedup.lookup_existing_async",
        AsyncMock(),
    ) as lookup_mock:
        await engine.managed_write_async(
            FILE_PATH,
            content,
            metadata={"parent_file_id": "parent-pdf-2", "page_number": 1},
        )

    assert not lookup_mock.called, (
        "Derivative write (parent_file_id in metadata) must bypass "
        "dedup lookup — otherwise blank-page renders from distinct "
        "PDFs would alias"
    )
    engine._router.write_async.assert_called_once()
    engine._db.upsert_file_async.assert_called_once()


@pytest.mark.asyncio
async def test_derivation_kind_in_metadata_bypasses_dedup_lookup():
    """``derivation_kind`` in metadata is the other half of the
    derivative signal. Variants of the same master ('thumbnail',
    'render', 'compressed') are byte-identical when the source is
    identical."""
    content = b"variant payload"
    engine = _make_engine()

    with patch(
        "matrx_utils.file_handling.dedup.lookup_existing_async",
        AsyncMock(),
    ) as lookup_mock:
        await engine.managed_write_async(
            FILE_PATH,
            content,
            metadata={"derivation_kind": "thumbnail"},
        )

    assert not lookup_mock.called
    engine._router.write_async.assert_called_once()


# ---------------------------------------------------------------------------
# 5. Existing row at the same file_path — dedup is NOT consulted
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_existing_row_update_path_does_not_consult_dedup():
    """Path-keyed update keeps "save over this file" semantics. The
    dedup check only runs for brand-new ROOT inserts — if there's
    already a row at this (owner_id, file_path), we update it
    in-place (new version). A coincidental content match elsewhere
    must NOT redirect this caller's save to that other file."""
    content = b"new version of an existing file"
    existing = _existing_row()
    existing["file_path"] = FILE_PATH
    engine = _make_engine(existing_at_path=existing)

    with patch(
        "matrx_utils.file_handling.dedup.lookup_existing_async",
        AsyncMock(),
    ) as lookup_mock:
        result = await engine.managed_write_async(FILE_PATH, content)

    assert not lookup_mock.called, (
        "Path-keyed update must not consult dedup — that would "
        "silently redirect the save to an unrelated file"
    )
    assert result.is_new is False
    assert result.file_id == existing["id"]
    engine._router.write_async.assert_called_once()
    engine._db.update_file_async.assert_called()


# ---------------------------------------------------------------------------
# 6. Race recovery — INSERT raises unique-violation, winner is re-queried
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_insert_race_recovers_via_winner_lookup():
    """A concurrent write of the same content won the canonical slot
    between our dedup lookup (miss) and our INSERT. The unique
    violation on ``cld_files_dedup_canonical`` is detected, the winner
    is re-queried, our orphan S3 object is deleted, and the caller
    gets the winner's SyncResult — same shape as a normal dedup hit."""
    content = b"raced upload bytes"
    checksum_hex = hashlib.sha256(content).hexdigest()
    winner = _existing_row(file_id="race-winner-9999")
    winner["file_path"] = "docs/canonical_raced.pdf"

    unique_violation = Exception(
        "duplicate key value violates unique constraint "
        '"cld_files_dedup_canonical" (SQLSTATE 23505)'
    )
    engine = _make_engine(upsert_raises=unique_violation)

    # Pre-INSERT lookup → miss. Post-violation lookup → winner.
    lookup_mock = AsyncMock(
        side_effect=[
            DedupLookupResult(checksum=checksum_hex, existing=None, scope="none"),
            DedupLookupResult(checksum=checksum_hex, existing=winner, scope="owner"),
        ]
    )

    with patch(
        "matrx_utils.file_handling.dedup.lookup_existing_async",
        lookup_mock,
    ):
        result = await engine.managed_write_async(FILE_PATH, content)

    assert lookup_mock.await_count == 2
    assert result.file_id == winner["id"]
    assert result.is_new is False
    assert result.checksum == checksum_hex
    # Orphan S3 object cleaned up.
    engine._router.delete_async.assert_called_once()
    # Versions row was NOT recorded — the winner already has its own.
    engine.versions.record_version_async.assert_not_called()


# ---------------------------------------------------------------------------
# 7. Race recovery — non-dedup-related insert failure is re-raised
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_unrelated_insert_failure_bubbles_up():
    """An INSERT that fails for a reason NEITHER race handler knows how
    to recover from (a non-unique DB error, FK violation, connection
    drop) must bubble up — never be silently swallowed. The orphan S3
    object we already PUT is still cleaned up on the way out (P0-1):
    a failed insert must not leak storage."""
    content = b"insert that fails for an unrelated reason"
    other_violation = Exception('foreign key violation "cld_files_some_fk" SQLSTATE 23503')
    engine = _make_engine(upsert_raises=other_violation)

    with patch(
        "matrx_utils.file_handling.dedup.lookup_existing_async",
        AsyncMock(
            return_value=DedupLookupResult(
                checksum=hashlib.sha256(content).hexdigest(),
                existing=None,
                scope="none",
            )
        ),
    ):
        with pytest.raises(Exception) as exc_info:
            await engine.managed_write_async(FILE_PATH, content)

    assert "23503" in str(exc_info.value)
    # Orphan S3 cleanup DID run — a failed insert must not leak its object.
    engine._router.delete_async.assert_called_once()
    # The winner was never read — this is not a recoverable race.
    engine.versions.record_version_async.assert_not_called()


# ---------------------------------------------------------------------------
# 8. Race recovery — (owner_id, file_path) collision converges on the winner
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_path_unique_collision_recovers_to_winner():
    """A concurrent pinned-id insert that loses the (owner_id, file_path)
    slot (e.g. two variant-render passes for the same content-deduped
    master writing the same variant path) must NOT corrupt the winner's
    primary key. It now raises 23505 on cld_files_owner_id_file_path_key;
    the loser recovers idempotently by reading the winner, returns its
    SyncResult (is_new=False), deletes its own orphan S3 object, and
    records NO version (the winner already has one)."""
    content = b"variant bytes written twice concurrently"
    winner = _existing_row(file_id="variant-winner-0001")
    path_violation = Exception(
        "duplicate key value violates unique constraint "
        '"cld_files_owner_id_file_path_key" SQLSTATE 23505'
    )
    engine = _make_engine(upsert_raises=path_violation)
    # First lookup (pre-insert) finds nothing; the post-collision read
    # returns the winning row that won the slot.
    engine._db.get_file_by_path_async = AsyncMock(side_effect=[None, winner])

    # Derivative write (variant) — bypasses the dedup lookup entirely, so
    # the ONLY recovery path is the (owner_id, file_path) handler.
    result = await engine.managed_write_async(
        FILE_PATH,
        content,
        parent_file_id="master-0001",
        derivation_kind="variant",
    )

    assert result.file_id == winner["id"]
    assert result.is_new is False
    # Orphan S3 object (our losing write) cleaned up.
    engine._router.delete_async.assert_called_once()
    # No version recorded — the winner already has its own.
    engine.versions.record_version_async.assert_not_called()
