"""Regression — hard-delete purges every S3 object (no C10 orphan leak).

The Postgres ``hard_delete_file`` RPC cascades the DB row + versions and returns
``{main, versions}`` — the storage URIs the backend must purge from S3. Before
2026-07-10, ``FileService.hard_delete`` and the matrx-ai ``cloud_file`` tool
called the raw DB fn and never purged, orphaning the main object + every version.

These tests pin the ONE primitive
``SyncEngine.hard_delete_and_purge[_async]`` (and the ``managed_delete`` paths
that route through it): the DB fn runs, and EVERY reported object is deleted from
storage. Stubs the sub-components (same pattern as test_managed_write_dedup.py).
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from matrx_utils.file_handling.cloud_sync.sync_engine import SyncEngine

USER_ID = "user-1"
FILE_ID = "file-abc"
MAIN_URI = "s3://bucket/user-1/file-abc"
VERSION_URIS = ["s3://bucket/user-1/file-abc/v1", "s3://bucket/user-1/file-abc/v2"]


def _make_engine(*, purge_return, file_record=None):
    engine = object.__new__(SyncEngine)

    router = MagicMock()
    router.delete = MagicMock(return_value=None)
    router.delete_async = AsyncMock(return_value=None)
    engine._router = router

    db = MagicMock()
    db.hard_delete_file = MagicMock(return_value=purge_return)
    db.hard_delete_file_async = AsyncMock(return_value=purge_return)
    db.soft_delete_file_async = AsyncMock(return_value=True)
    db.get_file_by_path_async = AsyncMock(return_value=file_record)
    engine._db = db

    permissions = MagicMock()
    permissions.require_async = AsyncMock(return_value=None)
    engine.permissions = permissions

    engine._resolve_user_id = MagicMock(return_value=USER_ID)  # type: ignore[method-assign]
    return engine


@pytest.mark.asyncio
async def test_hard_delete_and_purge_deletes_main_and_versions():
    engine = _make_engine(purge_return={"main": MAIN_URI, "versions": VERSION_URIS})

    await engine.hard_delete_and_purge_async(FILE_ID, MAIN_URI)

    engine._db.hard_delete_file_async.assert_awaited_once_with(FILE_ID)
    deleted = {c.args[0] for c in engine._router.delete_async.await_args_list}
    assert deleted == {MAIN_URI, *VERSION_URIS}, "main + every version must be purged"


@pytest.mark.asyncio
async def test_hard_delete_purges_main_even_if_rpc_fails():
    """DB fn raising must NOT skip purging the known main object."""
    engine = _make_engine(purge_return=None)
    engine._db.hard_delete_file_async = AsyncMock(side_effect=RuntimeError("boom"))

    await engine.hard_delete_and_purge_async(FILE_ID, MAIN_URI)

    deleted = {c.args[0] for c in engine._router.delete_async.await_args_list}
    assert MAIN_URI in deleted


@pytest.mark.asyncio
async def test_managed_delete_async_hard_routes_through_purge():
    record = {"id": FILE_ID, "owner_id": USER_ID, "file_path": "d/x.pdf", "storage_uri": MAIN_URI}
    engine = _make_engine(
        purge_return={"main": MAIN_URI, "versions": VERSION_URIS}, file_record=record
    )

    ok = await engine.managed_delete_async("d/x.pdf", user_id=USER_ID, hard_delete=True)

    assert ok is True
    deleted = {c.args[0] for c in engine._router.delete_async.await_args_list}
    assert deleted == {MAIN_URI, *VERSION_URIS}


@pytest.mark.asyncio
async def test_managed_delete_async_soft_does_not_purge():
    record = {"id": FILE_ID, "owner_id": USER_ID, "file_path": "d/x.pdf", "storage_uri": MAIN_URI}
    engine = _make_engine(purge_return=None, file_record=record)

    await engine.managed_delete_async("d/x.pdf", user_id=USER_ID, hard_delete=False)

    engine._db.soft_delete_file_async.assert_awaited_once_with(FILE_ID)
    engine._router.delete_async.assert_not_awaited()


def test_sync_hard_delete_and_purge_deletes_main_and_versions():
    engine = _make_engine(purge_return={"main": MAIN_URI, "versions": VERSION_URIS})

    engine.hard_delete_and_purge(FILE_ID, MAIN_URI)

    deleted = {c.args[0] for c in engine._router.delete.call_args_list}
    assert deleted == {MAIN_URI, *VERSION_URIS}


def test_purge_uris_dedupes_and_skips_none():
    got = SyncEngine._purge_uris_from(
        MAIN_URI, {"main": MAIN_URI, "versions": [VERSION_URIS[0], None, VERSION_URIS[0]]}
    )
    assert got == [MAIN_URI, VERSION_URIS[0]]
