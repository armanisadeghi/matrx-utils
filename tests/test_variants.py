"""Forcing-function tests for the matrx-utils variant primitive.

``render_variant_async`` is the single primitive that turns
``(master_file_id, variant_key)`` into a deterministic, idempotent,
encoder-injected derived file. These tests pin two properties:

1. **Encoder injection works without matrx-ai installed.** A test-local
   encoder is registered for a fake family and the renderer must call it.
2. **Idempotency.** A second call for the same ``(master, key)`` must
   hit the cached row and NOT re-invoke the encoder. This is what makes
   the lazy ``MediaRef.vision_class`` resolver safe to call on every
   request — the cost of a hit is one DB lookup.

We use an in-memory FakeSyncEngine (DB + storage) — the system under
test (``render_variant_async``) is exercised end-to-end. Every
forcing-function check pins behaviour the renderer itself must produce.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from matrx_utils.file_handling.cloud_sync.models import SyncResult
from matrx_utils.file_handling.cloud_sync.variants import (
    get_variant_encoder,
    has_variant_encoder,
    register_variant_encoder,
    render_variant_async,
    variant_file_path,
)


# ---------------------------------------------------------------------------
# In-memory fakes (stub the dependencies; SUT is render_variant_async)
# ---------------------------------------------------------------------------


@dataclass
class _Row:
    id: str
    owner_id: str
    file_path: str
    storage_uri: str
    mime_type: str
    file_size: int
    visibility: str = "private"
    metadata: dict[str, Any] = field(default_factory=dict)


class _FakeDB:
    def __init__(self) -> None:
        self.by_id: dict[str, _Row] = {}
        self.by_owner_path: dict[tuple[str, str], _Row] = {}

    async def get_file_async(self, file_id: str) -> dict | None:
        row = self.by_id.get(file_id)
        return _row_to_dict(row) if row else None

    async def get_file_by_path_async(self, owner: str, path: str) -> dict | None:
        row = self.by_owner_path.get((owner, path))
        return _row_to_dict(row) if row else None


def _row_to_dict(row: _Row) -> dict:
    return {
        "id": row.id,
        "owner_id": row.owner_id,
        "file_path": row.file_path,
        "storage_uri": row.storage_uri,
        "mime_type": row.mime_type,
        "file_size": row.file_size,
        "visibility": row.visibility,
        "metadata": row.metadata,
    }


class _FakeRouter:
    def __init__(self, storage: dict[str, bytes]) -> None:
        self._storage = storage
        self.read_calls: list[str] = []

    async def read_async(self, storage_uri: str) -> bytes:
        self.read_calls.append(storage_uri)
        return self._storage[storage_uri]

    async def get_url_async(
        self,
        storage_uri: str,
        *,
        expires_in: int = 3600,
        response_content_disposition: str | None = None,
        response_content_type: str | None = None,
    ) -> str:
        return f"https://fake.cdn/{storage_uri}?ttl={expires_in}"


class _FakeSyncEngine:
    def __init__(self) -> None:
        self._storage: dict[str, bytes] = {}
        self._db = _FakeDB()
        self._router = _FakeRouter(self._storage)
        self.write_calls: list[tuple[str, int, str | None]] = []

    # Mirror the real SyncEngine's public accessors used by render_variant_async.
    @property
    def db(self) -> _FakeDB:
        return self._db

    @property
    def router(self) -> _FakeRouter:
        return self._router

    async def build_urls_for_record_async(self, record: dict) -> dict[str, Any]:
        uri = record["storage_uri"]
        return {
            "url": f"https://fake.cdn/{uri}",
            "cdn_url": None,
            "signed_url": f"https://fake.cdn/{uri}?signed=1",
            "download_url": f"https://fake.cdn/{uri}?download=1",
            "signed_url_expires_at": None,
        }

    async def managed_write_async(
        self,
        file_path: str,
        content: bytes,
        *,
        mime_type: str | None = None,
        visibility: str = "private",
        user_id: str | None = None,
        metadata: dict | None = None,
    ) -> SyncResult:
        owner = user_id or "test-owner"
        self.write_calls.append((file_path, len(content), mime_type))
        existing = self._db.by_owner_path.get((owner, file_path))
        if existing:
            existing.storage_uri = f"s3://bucket/{file_path}"
            existing.file_size = len(content)
            existing.mime_type = mime_type or existing.mime_type
            existing.metadata = metadata or existing.metadata
            self._storage[existing.storage_uri] = content
            return SyncResult(
                file_id=existing.id,
                storage_uri=existing.storage_uri,
                version_number=2,
                file_size=existing.file_size,
                is_new=False,
                url=f"https://fake.cdn/{existing.storage_uri}",
            )
        new_id = f"fake-uuid-{len(self._db.by_id) + 1}"
        storage_uri = f"s3://bucket/{file_path}"
        row = _Row(
            id=new_id,
            owner_id=owner,
            file_path=file_path,
            storage_uri=storage_uri,
            mime_type=mime_type or "application/octet-stream",
            file_size=len(content),
            visibility=visibility,
            metadata=metadata or {},
        )
        self._db.by_id[new_id] = row
        self._db.by_owner_path[(owner, file_path)] = row
        self._storage[storage_uri] = content
        return SyncResult(
            file_id=new_id,
            storage_uri=storage_uri,
            version_number=1,
            file_size=len(content),
            is_new=True,
            url=f"https://fake.cdn/{storage_uri}",
        )


class _FakeFileManager:
    def __init__(self) -> None:
        self.sync_engine = _FakeSyncEngine()

    def _require_sync_engine(self) -> _FakeSyncEngine:
        return self.sync_engine


@pytest.fixture
def fm_with_master() -> tuple[_FakeFileManager, str, bytes]:
    fm = _FakeFileManager()
    master_bytes = b"\xff\xd8" + b"\x00" * 1000 + b"\xff\xd9"  # fake JPEG
    se = fm.sync_engine
    row = _Row(
        id="master-1",
        owner_id="user-42",
        file_path="screens/abc/master.jpg",
        storage_uri="s3://bucket/screens/abc/master.jpg",
        mime_type="image/jpeg",
        file_size=len(master_bytes),
    )
    se._db.by_id[row.id] = row
    se._db.by_owner_path[(row.owner_id, row.file_path)] = row
    se._storage[row.storage_uri] = master_bytes
    return fm, row.id, master_bytes


@pytest.fixture(autouse=True)
def _restore_encoders():
    """Snapshot/restore the encoder registry around each test."""
    from matrx_utils.file_handling.cloud_sync import variants as v_mod

    snapshot = dict(v_mod._ENCODERS)
    yield
    v_mod._ENCODERS.clear()
    v_mod._ENCODERS.update(snapshot)


def test_register_variant_encoder_stores_and_lookups(fm_with_master) -> None:
    """A registered encoder is reachable through the public lookup API."""
    fm, _, _ = fm_with_master

    def _enc(master: bytes, key: str) -> tuple[bytes, str]:
        return b"out", "image/jpeg"

    register_variant_encoder("test_family", _enc)
    assert has_variant_encoder("test_family")
    assert get_variant_encoder("test_family") is _enc


@pytest.mark.asyncio
async def test_render_variant_invokes_injected_encoder_on_miss(fm_with_master) -> None:
    """Cache miss must call the encoder exactly once with the master bytes
    and the variant key. The encoder return value must shape the row."""
    fm, master_id, master_bytes = fm_with_master
    calls: list[tuple[bytes, str]] = []

    def _enc(master: bytes, key: str) -> tuple[bytes, str]:
        calls.append((master, key))
        return b"X" * 42, "image/jpeg"

    register_variant_encoder("vision", _enc)

    info = await render_variant_async(
        fm, master_id, variant_key="anthropic_opus_hires", family="vision"
    )

    assert calls == [(master_bytes, "anthropic_opus_hires")]
    assert info["is_new"] is True
    assert info["mime_type"] == "image/jpeg"
    assert info["size_bytes"] == 42
    assert info["file_path"] == "screens/abc/v/anthropic_opus_hires.jpg"
    assert info["metadata"] == {
        "derived_from": master_id,
        "variant_family": "vision",
        "variant_key": "anthropic_opus_hires",
    }


@pytest.mark.asyncio
async def test_render_variant_is_idempotent(fm_with_master) -> None:
    """Second call for the same (master, key) hits the cached row. The
    encoder must NOT be invoked the second time — that's the cache. The
    forcing function: if idempotency breaks, encoder call count is 2."""
    fm, master_id, _ = fm_with_master
    calls: list[str] = []

    def _enc(master: bytes, key: str) -> tuple[bytes, str]:
        calls.append(key)
        return b"X" * 99, "image/jpeg"

    register_variant_encoder("vision", _enc)

    info1 = await render_variant_async(
        fm, master_id, variant_key="anthropic_sonnet_default", family="vision"
    )
    info2 = await render_variant_async(
        fm, master_id, variant_key="anthropic_sonnet_default", family="vision"
    )

    assert len(calls) == 1, f"encoder invoked {len(calls)} times — expected 1"
    assert info1["file_id"] == info2["file_id"]
    assert info1["is_new"] is True
    assert info2["is_new"] is False
    # Storage write count: the second call must NOT have written.
    write_paths = [c[0] for c in fm.sync_engine.write_calls]
    assert write_paths.count("screens/abc/v/anthropic_sonnet_default.jpg") == 1


@pytest.mark.asyncio
async def test_render_variant_different_keys_render_independently(fm_with_master) -> None:
    fm, master_id, _ = fm_with_master
    calls: list[str] = []

    def _enc(master: bytes, key: str) -> tuple[bytes, str]:
        calls.append(key)
        return b"Y" * 17, "image/jpeg"

    register_variant_encoder("vision", _enc)

    a = await render_variant_async(fm, master_id, variant_key="openai_high", family="vision")
    b = await render_variant_async(fm, master_id, variant_key="openai_low", family="vision")

    assert calls == ["openai_high", "openai_low"]
    assert a["file_id"] != b["file_id"]
    assert a["file_path"].endswith("openai_high.jpg")
    assert b["file_path"].endswith("openai_low.jpg")


@pytest.mark.asyncio
async def test_render_variant_raises_when_no_encoder_registered(fm_with_master) -> None:
    fm, master_id, _ = fm_with_master
    # No encoder registered for "missing_family"
    assert not has_variant_encoder("missing_family")
    with pytest.raises(RuntimeError, match="no variant encoder registered"):
        await render_variant_async(
            fm, master_id, variant_key="anything", family="missing_family"
        )


@pytest.mark.asyncio
async def test_render_variant_raises_for_unknown_master(fm_with_master) -> None:
    fm, _, _ = fm_with_master
    register_variant_encoder("vision", lambda b, k: (b"x", "image/jpeg"))
    with pytest.raises(FileNotFoundError):
        await render_variant_async(
            fm, "no-such-master-id", variant_key="anthropic_opus_hires", family="vision"
        )


@pytest.mark.asyncio
async def test_render_variant_uses_explicit_encoder_override(fm_with_master) -> None:
    """The ``encoder=`` kwarg overrides the family-registered one. Useful
    for one-off renders without polluting the registry."""
    fm, master_id, _ = fm_with_master
    register_variant_encoder("vision", lambda b, k: (b"WRONG", "image/jpeg"))

    def _override(master: bytes, key: str) -> tuple[bytes, str]:
        return b"OVERRIDDEN", "image/png"

    info = await render_variant_async(
        fm,
        master_id,
        variant_key="custom_key",
        family="vision",
        encoder=_override,
    )
    assert info["size_bytes"] == len(b"OVERRIDDEN")
    assert info["mime_type"] == "image/png"
    assert info["file_path"].endswith("custom_key.png")


@pytest.mark.asyncio
async def test_render_variant_supports_async_encoder(fm_with_master) -> None:
    fm, master_id, _ = fm_with_master

    async def _async_enc(master: bytes, key: str) -> tuple[bytes, str]:
        return b"ASYNC", "image/webp"

    register_variant_encoder("vision", _async_enc)
    info = await render_variant_async(
        fm, master_id, variant_key="async_test", family="vision"
    )
    assert info["mime_type"] == "image/webp"
    assert info["file_path"].endswith("async_test.webp")


def test_variant_file_path_is_deterministic() -> None:
    """The variant path is derived from the master path and the key.
    A regression here would silently leak variants into the wrong folder."""
    assert (
        variant_file_path("screens/abc/master.jpg", "anthropic_opus_hires", "jpg")
        == "screens/abc/v/anthropic_opus_hires.jpg"
    )
    assert variant_file_path("master.jpg", "k", "jpg") == "v/k.jpg"
    assert (
        variant_file_path("a/b/c/d/master.png", "openai_high", "webp")
        == "a/b/c/d/v/openai_high.webp"
    )
