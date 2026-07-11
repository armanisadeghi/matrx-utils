"""Phase 1.5 — TUS finalize_async dedup gate.

Verifies the new behaviour added in
``packages/matrx-utils/matrx_utils/file_handling/cloud_sync/transports/tus.py``:

  * S3-native full-object SHA-256 (``ChecksumAlgorithm='SHA256'`` +
    ``ChecksumType='FULL_OBJECT'`` on ``create_multipart_upload``,
    base64 ``ChecksumSHA256`` on ``complete_multipart_upload`` decoded
    to the 64-char hex form).
  * Dedup gate before the ``cld_files`` INSERT (scope-matching hit →
    delete orphan S3 object, mark inflight completed with a
    ``dedup_winner_file_id`` metadata pointer, return the canonical
    file_id; derivative writes bypass the lookup; missing checksum
    skips the lookup).
  * Race recovery on the INSERT via ``SyncEngine._is_dedup_unique_violation``.

The tests stub ``SyncEngine`` and the Supabase chainable query builder
with ``unittest.mock`` rather than spinning up a full ``SyncEngine``;
the gate's logic is independent of the surrounding plumbing.
"""

from __future__ import annotations

import base64
import hashlib
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from matrx_utils.file_handling.cloud_sync.transports.tus import (
    TUSSessionManager,
    TUSSessionRow,
)
from matrx_utils.file_handling.dedup import DedupLookupResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _checksum_b64(content: bytes) -> str:
    """S3 returns SHA-256 as base64 — match its envelope."""
    return base64.b64encode(hashlib.sha256(content).digest()).decode("ascii")


def _make_session(metadata: dict[str, Any] | None = None) -> TUSSessionRow:
    return TUSSessionRow(
        upload_id="upload-1",
        file_id="00000000-0000-0000-0000-000000000001",
        owner_id="user-1",
        file_path="docs/q1.pdf",
        bucket="test-bucket",
        key="user-1/00000000-0000-0000-0000-000000000001",
        multipart_upload_id="mpu-1",
        upload_length=1024,
        upload_offset=1024,
        visibility="private",
        mime_type="application/pdf",
        file_name="q1.pdf",
        metadata=metadata or {},
        parts=[{"PartNumber": 1, "ETag": "etag-1"}],
        status="in_progress",
    )


def _chainable_db_mock(
    *, insert_raises: BaseException | None = None,
    rpc_data: str | None = None,
) -> MagicMock:
    """Supabase-style chainable query-builder mock.

    Every method that returns a builder returns the same mock, so
    ``db.table('x').insert(...).execute()`` and friends all resolve
    through the same node. ``.execute()`` is async; everything before
    it is sync.
    """
    db_client = MagicMock()
    # File tables are accessed via client.schema("files").table("files"),
    # so .schema() must keep the chain on the same node.
    db_client.schema = MagicMock(return_value=db_client)
    db_client.table = MagicMock(return_value=db_client)
    db_client.insert = MagicMock(return_value=db_client)
    db_client.update = MagicMock(return_value=db_client)
    db_client.select = MagicMock(return_value=db_client)
    db_client.eq = MagicMock(return_value=db_client)
    db_client.maybe_single = MagicMock(return_value=db_client)
    db_client.rpc = MagicMock(return_value=db_client)
    if insert_raises is not None:
        db_client.execute = AsyncMock(side_effect=insert_raises)
    else:
        # rpc(...) returns .data; insert(...) / update(...) callers
        # discard the result. A single execute mock covers all paths.
        db_client.execute = AsyncMock(
            return_value=MagicMock(data=rpc_data)
        )
    return db_client


def _make_engine_mock(
    *,
    complete_resp: dict[str, Any] | None = None,
    head_resp: dict[str, Any] | None = None,
    db_client: MagicMock | None = None,
) -> tuple[MagicMock, MagicMock]:
    """Return (engine, s3_client) with all the seams TUSSessionManager touches."""
    engine = MagicMock()
    engine.router.is_configured.return_value = True
    s3_client = MagicMock()
    s3_client.complete_multipart_upload = MagicMock(
        return_value=complete_resp or {}
    )
    s3_client.head_object = MagicMock(
        return_value=head_resp or {"ContentLength": 1024}
    )
    s3_client.delete_object = MagicMock(return_value={})
    engine.router.s3._get_client.return_value = s3_client
    engine.config.storage_backend = "s3"
    engine.db._get_async_client = AsyncMock(
        return_value=db_client or _chainable_db_mock()
    )
    return engine, s3_client


# ---------------------------------------------------------------------------
# 1. S3 SHA-256 base64 → hex decoding
# ---------------------------------------------------------------------------


def test_checksum_b64_decodes_to_64_char_hex():
    """Sanity check the decode helper used in finalize_async."""
    content = b"hello tus world"
    b64 = _checksum_b64(content)
    raw = base64.b64decode(b64)
    assert len(raw) == 32  # SHA-256 is 32 bytes
    hex_ = raw.hex()
    assert len(hex_) == 64
    assert hex_ == hashlib.sha256(content).hexdigest()


# ---------------------------------------------------------------------------
# 2. Dedup HIT — short-circuits, deletes orphan, returns canonical file_id
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_finalize_dedup_hit_short_circuits_and_returns_canonical():
    content = b"the same content twice"
    expected_hex = hashlib.sha256(content).hexdigest()
    canonical_row = {
        "id": "11111111-1111-1111-1111-111111111111",
        "file_path": "docs/q1_canonical.pdf",
        "storage_uri": "s3://test-bucket/user-1/11111111-1111-1111-1111-111111111111",
        "size_bytes": len(content),
    }

    db_client = _chainable_db_mock()
    engine, s3_client = _make_engine_mock(
        complete_resp={"ChecksumSHA256": _checksum_b64(content)},
        head_resp={"ContentLength": len(content)},
        db_client=db_client,
    )
    mgr = TUSSessionManager(engine)

    with patch.object(mgr, "get_async", AsyncMock(return_value=_make_session())), \
         patch(
             "matrx_utils.file_handling.dedup.lookup_existing_async",
             AsyncMock(return_value=DedupLookupResult(
                 checksum=expected_hex,
                 existing=canonical_row,
                 scope="owner",
             )),
         ) as mock_lookup:
        result = await mgr.finalize_async(
            upload_id="upload-1", owner_id="user-1",
        )

    assert mock_lookup.called
    assert result.file_id == canonical_row["id"]
    assert result.checksum == expected_hex
    assert result.storage_uri == canonical_row["storage_uri"]
    # Orphan S3 object deleted.
    s3_client.delete_object.assert_called_once_with(
        Bucket="test-bucket",
        Key="user-1/00000000-0000-0000-0000-000000000001",
    )
    # No INSERT into cld_files happened — only the inflight UPDATE.
    insert_calls = [
        c for c in db_client.table.call_args_list
        if c.args and c.args[0] == "files"
    ]
    assert insert_calls == [], (
        "Dedup hit must short-circuit before the cld_files INSERT"
    )
    # The inflight row was marked completed and carries the canonical pointer.
    update_payloads = [
        c.args[0] for c in db_client.update.call_args_list
        if c.args
    ]
    assert any(
        isinstance(p, dict)
        and p.get("status") == "completed"
        and (p.get("metadata") or {}).get("dedup_winner_file_id")
        == canonical_row["id"]
        for p in update_payloads
    ), f"inflight UPDATE missing dedup pointer; saw: {update_payloads}"


# ---------------------------------------------------------------------------
# 3. Derivative bypass — metadata.parent_file_id skips the lookup
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_derivative_metadata_bypasses_dedup_lookup():
    """A blank-page render from a distinct parent PDF carries
    ``parent_file_id`` in metadata. The lookup must be skipped — two
    byte-identical derivatives of DIFFERENT parents are legitimately
    separate rows."""
    content = b"identical blank page"
    db_client = _chainable_db_mock(rpc_data=None)
    engine, _ = _make_engine_mock(
        complete_resp={"ChecksumSHA256": _checksum_b64(content)},
        head_resp={"ContentLength": len(content)},
        db_client=db_client,
    )
    mgr = TUSSessionManager(engine)
    session = _make_session(
        metadata={"parent_file_id": "parent-1", "page_number": 1}
    )

    with patch.object(mgr, "get_async", AsyncMock(return_value=session)), \
         patch(
             "matrx_utils.file_handling.dedup.lookup_existing_async",
             AsyncMock(),
         ) as mock_lookup:
        result = await mgr.finalize_async(
            upload_id="upload-1", owner_id="user-1",
        )

    assert not mock_lookup.called, (
        "Derivative writes must bypass the dedup lookup"
    )
    assert result.file_id == session.file_id
    # cld_files INSERT happened (not short-circuited).
    table_calls = [
        c.args[0] for c in db_client.table.call_args_list if c.args
    ]
    assert "files" in table_calls


# ---------------------------------------------------------------------------
# 4. Missing ChecksumSHA256 — checksum stays NULL, dedup skipped
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_missing_s3_checksum_falls_back_to_null_and_skips_lookup():
    """When S3 returns no ChecksumSHA256 (bucket/region rejected
    FULL_OBJECT), the row lands with checksum NULL and the dedup gate
    is bypassed — same behaviour as Phase 1, no regression, no
    polluted dedup space."""
    db_client = _chainable_db_mock()
    engine, _ = _make_engine_mock(
        complete_resp={},  # no ChecksumSHA256
        head_resp={"ContentLength": 1024},
        db_client=db_client,
    )
    mgr = TUSSessionManager(engine)

    with patch.object(mgr, "get_async", AsyncMock(return_value=_make_session())), \
         patch(
             "matrx_utils.file_handling.dedup.lookup_existing_async",
             AsyncMock(),
         ) as mock_lookup:
        result = await mgr.finalize_async(
            upload_id="upload-1", owner_id="user-1",
        )

    assert not mock_lookup.called
    assert result.checksum is None
    # cld_files INSERT proceeded.
    table_calls = [
        c.args[0] for c in db_client.table.call_args_list if c.args
    ]
    assert "files" in table_calls
    # The inserted row's checksum field is None.
    insert_calls = [c.args[0] for c in db_client.insert.call_args_list if c.args]
    cld_inserts = [
        r for r in insert_calls
        if isinstance(r, dict) and "checksum" in r and "file_path" in r
    ]
    assert cld_inserts and cld_inserts[0]["checksum"] is None


# ---------------------------------------------------------------------------
# 5. Invalid base64 from S3 — checksum stays NULL, dedup skipped, no crash
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_garbled_s3_checksum_does_not_crash_finalize():
    db_client = _chainable_db_mock()
    engine, _ = _make_engine_mock(
        complete_resp={"ChecksumSHA256": "not-valid-base64!!!"},
        head_resp={"ContentLength": 1024},
        db_client=db_client,
    )
    mgr = TUSSessionManager(engine)

    with patch.object(mgr, "get_async", AsyncMock(return_value=_make_session())), \
         patch(
             "matrx_utils.file_handling.dedup.lookup_existing_async",
             AsyncMock(),
         ) as mock_lookup:
        result = await mgr.finalize_async(
            upload_id="upload-1", owner_id="user-1",
        )

    # Logged a warning, checksum NULL, lookup skipped, INSERT proceeded.
    assert result.checksum is None
    assert not mock_lookup.called


# ---------------------------------------------------------------------------
# 6. Race recovery — INSERT raises unique-violation, winner is re-queried
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_insert_race_recovers_via_winner_lookup():
    """A concurrent finalize won the canonical slot between our lookup
    and our INSERT. The unique-violation is detected, the winner is
    re-queried, our S3 object is deleted, and the caller gets the
    winner's file_id."""
    content = b"raced upload"
    checksum_hex = hashlib.sha256(content).hexdigest()
    canonical_row = {
        "id": "22222222-2222-2222-2222-222222222222",
        "file_path": "docs/raced.pdf",
        "storage_uri": "s3://test-bucket/user-2/22222222-2222-2222-2222-222222222222",
        "size_bytes": len(content),
    }

    # Build a db_client whose execute path returns different values for
    # the two stages: rpc resolution first (returns None data), then
    # cld_files INSERT raises a unique violation, then inflight UPDATE
    # succeeds again.
    db_client = MagicMock()
    db_client.schema = MagicMock(return_value=db_client)
    db_client.table = MagicMock(return_value=db_client)
    db_client.insert = MagicMock(return_value=db_client)
    db_client.update = MagicMock(return_value=db_client)
    db_client.select = MagicMock(return_value=db_client)
    db_client.eq = MagicMock(return_value=db_client)
    db_client.maybe_single = MagicMock(return_value=db_client)
    db_client.rpc = MagicMock(return_value=db_client)

    unique_violation = Exception(
        "duplicate key value violates unique constraint "
        "\"cld_files_dedup_canonical\" (SQLSTATE 23505)"
    )

    call_count = {"n": 0}

    async def fake_execute(*args, **kwargs):
        call_count["n"] += 1
        # First few calls — folder rpc + maybe other reads — succeed.
        # cld_files INSERT is identified by inspecting prior .table() arg.
        last_table = db_client.table.call_args
        last_table_arg = last_table.args[0] if last_table and last_table.args else None
        last_insert = db_client.insert.call_args
        # Insert into cld_files raises the unique violation exactly once.
        if (
            last_table_arg == "files"
            and last_insert is not None
            and last_insert.args
            and isinstance(last_insert.args[0], dict)
            and last_insert.args[0].get("file_path") == "docs/q1.pdf"
        ):
            raise unique_violation
        return MagicMock(data=None)

    db_client.execute = AsyncMock(side_effect=fake_execute)

    engine, s3_client = _make_engine_mock(
        complete_resp={"ChecksumSHA256": _checksum_b64(content)},
        head_resp={"ContentLength": len(content)},
        db_client=db_client,
    )
    mgr = TUSSessionManager(engine)

    # First lookup (pre-INSERT) — miss. Second lookup (post-violation) — hit.
    lookup_responses = [
        DedupLookupResult(checksum=checksum_hex, existing=None, scope="none"),
        DedupLookupResult(
            checksum=checksum_hex, existing=canonical_row, scope="owner",
        ),
    ]
    lookup_mock = AsyncMock(side_effect=lookup_responses)

    with patch.object(mgr, "get_async", AsyncMock(return_value=_make_session())), \
         patch(
             "matrx_utils.file_handling.dedup.lookup_existing_async",
             lookup_mock,
         ):
        result = await mgr.finalize_async(
            upload_id="upload-1", owner_id="user-1",
        )

    assert result.file_id == canonical_row["id"]
    assert result.checksum == checksum_hex
    assert lookup_mock.await_count == 2
    s3_client.delete_object.assert_called_once()
