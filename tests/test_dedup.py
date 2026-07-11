"""
Tests for the dedup module — strict-intent contract for content-hash-
based file deduplication.

Covers the three intents (``create``, ``alias_existing``,
``force_new_copy``), the checksum computation primitives, the policy
resolver, and the end-to-end async wrapper against a fake DB.
"""

from __future__ import annotations

import io

import pytest


from matrx_utils.file_handling.dedup import (  # noqa: E402
    DedupDecision,
    DedupLookupResult,
    DuplicateFileError,
    InvalidIntentError,
    MissingReasonError,
    UploadIntent,
    VALID_INTENTS,
    coerce_intent,
    compute_checksum,
    compute_checksum_stream,
    resolve_async,
    resolve_dedup_policy,
    validate_force_new_copy_reason,
)


# ── compute_checksum ─────────────────────────────────────────────────────


def test_compute_checksum_known_vector():
    # Standard SHA-256 of "hello world"
    assert compute_checksum(b"hello world") == (
        "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
    )


def test_compute_checksum_empty():
    # SHA-256 of empty bytes
    assert compute_checksum(b"") == (
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )


def test_compute_checksum_accepts_bytearray_and_memoryview():
    payload = bytearray(b"sample content")
    h1 = compute_checksum(payload)
    h2 = compute_checksum(memoryview(payload))
    h3 = compute_checksum(bytes(payload))
    assert h1 == h2 == h3


def test_compute_checksum_rejects_str():
    with pytest.raises(TypeError):
        compute_checksum("hello world")  # type: ignore[arg-type]


def test_compute_checksum_stream_matches_bytes():
    payload = b"x" * (1024 * 1024 * 2 + 17)  # > 2 MiB to exercise buffering
    direct = compute_checksum(payload)
    streamed = compute_checksum_stream(io.BytesIO(payload))
    assert direct == streamed


# ── coerce_intent ────────────────────────────────────────────────────────


def test_coerce_intent_strings():
    assert coerce_intent("create") is UploadIntent.CREATE
    assert coerce_intent("alias_existing") is UploadIntent.ALIAS_EXISTING
    assert coerce_intent("force_new_copy") is UploadIntent.FORCE_NEW_COPY


def test_coerce_intent_enum_passthrough():
    assert coerce_intent(UploadIntent.CREATE) is UploadIntent.CREATE


def test_coerce_intent_none_raises():
    with pytest.raises(InvalidIntentError):
        coerce_intent(None)


def test_coerce_intent_unknown_raises():
    with pytest.raises(InvalidIntentError) as exc:
        coerce_intent("upsert")
    assert "unknown intent" in str(exc.value)


def test_valid_intents_matches_enum():
    assert VALID_INTENTS == {i.value for i in UploadIntent}


# ── validate_force_new_copy_reason ───────────────────────────────────────


def test_reason_required():
    with pytest.raises(MissingReasonError):
        validate_force_new_copy_reason(None)
    with pytest.raises(MissingReasonError):
        validate_force_new_copy_reason("")
    with pytest.raises(MissingReasonError):
        validate_force_new_copy_reason("   ")


def test_reason_too_short():
    with pytest.raises(MissingReasonError):
        validate_force_new_copy_reason("ok")


def test_reason_strips_whitespace():
    assert validate_force_new_copy_reason("  legitimate reason  ") == (
        "legitimate reason"
    )


# ── resolve_dedup_policy ─────────────────────────────────────────────────


SAMPLE_CHECKSUM = (
    "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
)


def _no_dupe() -> DedupLookupResult:
    return DedupLookupResult(checksum=SAMPLE_CHECKSUM, existing=None, scope="none")


def _with_dupe(scope: str = "org") -> DedupLookupResult:
    return DedupLookupResult(
        checksum=SAMPLE_CHECKSUM,
        existing={
            "id": "11111111-1111-1111-1111-111111111111",
            "file_path": "documents/report.pdf",
            "created_at": "2026-05-01T00:00:00Z",
        },
        scope=scope,
    )


def test_policy_create_no_dupe_writes_new():
    decision = resolve_dedup_policy(UploadIntent.CREATE, _no_dupe(), reason=None)
    assert decision.action == "write_new"
    assert decision.canonical_file_id is None


def test_policy_create_with_dupe_raises():
    with pytest.raises(DuplicateFileError) as exc:
        resolve_dedup_policy(UploadIntent.CREATE, _with_dupe(), reason=None)
    err = exc.value
    assert err.existing_file_id == "11111111-1111-1111-1111-111111111111"
    assert err.scope == "org"
    payload = err.to_dict()
    assert payload["error"] == "duplicate_file"
    assert payload["status_code"] == 409
    assert "alias_existing" in payload["allowed_intents"]
    assert "force_new_copy" in payload["allowed_intents"]
    assert payload["existing_path"] == "documents/report.pdf"


def test_policy_alias_existing_with_dupe_returns_existing():
    decision = resolve_dedup_policy(
        UploadIntent.ALIAS_EXISTING, _with_dupe("org"), reason=None
    )
    assert decision.action == "return_existing"
    assert decision.canonical_file_id == "11111111-1111-1111-1111-111111111111"


def test_policy_alias_existing_no_dupe_writes_new():
    decision = resolve_dedup_policy(
        UploadIntent.ALIAS_EXISTING, _no_dupe(), reason=None
    )
    assert decision.action == "write_new"
    assert decision.canonical_file_id is None


def test_policy_force_new_copy_with_dupe_writes_alias():
    decision = resolve_dedup_policy(
        UploadIntent.FORCE_NEW_COPY,
        _with_dupe(),
        reason="client wants an isolated copy",
    )
    assert decision.action == "write_alias"
    assert decision.canonical_file_id == "11111111-1111-1111-1111-111111111111"
    assert decision.reason == "client wants an isolated copy"


def test_policy_force_new_copy_no_dupe_degenerates_to_write_new():
    decision = resolve_dedup_policy(
        UploadIntent.FORCE_NEW_COPY,
        _no_dupe(),
        reason="legitimate explanation",
    )
    # No dupe to alias — fall through to a normal create.
    assert decision.action == "write_new"
    assert decision.canonical_file_id is None
    # Reason still recorded in the decision.
    assert decision.reason == "legitimate explanation"


def test_policy_force_new_copy_requires_reason():
    with pytest.raises(MissingReasonError):
        resolve_dedup_policy(UploadIntent.FORCE_NEW_COPY, _with_dupe(), reason=None)


# ── End-to-end resolve_async with a fake DB ─────────────────────────────


class _FakeDB:
    """Minimal stand-in for CloudSyncDB.get_file_by_checksum_async."""

    def __init__(self, existing_by_checksum: dict[str, dict] | None = None):
        self.existing_by_checksum = existing_by_checksum or {}
        self.calls: list[tuple] = []

    async def get_file_by_checksum_async(
        self,
        checksum: str,
        *,
        owner_id: str | None = None,
        organization_id: str | None = None,
    ):
        self.calls.append((checksum, owner_id, organization_id))
        return self.existing_by_checksum.get(checksum)


@pytest.mark.asyncio
async def test_resolve_async_create_no_dupe():
    db = _FakeDB()
    decision = await resolve_async(
        db,
        intent="create",
        content=b"new file content",
        owner_id="u1",
        organization_id=None,
    )
    assert decision.action == "write_new"
    # The DB was consulted with the right scope.
    assert len(db.calls) == 1
    checksum, owner, org = db.calls[0]
    assert owner == "u1" and org is None
    assert checksum == compute_checksum(b"new file content")


@pytest.mark.asyncio
async def test_resolve_async_create_with_dupe_raises():
    content = b"already-uploaded content"
    checksum = compute_checksum(content)
    db = _FakeDB(
        existing_by_checksum={
            checksum: {
                "id": "22222222-2222-2222-2222-222222222222",
                "file_path": "existing.pdf",
                "created_at": "2026-04-01T00:00:00Z",
            }
        }
    )
    with pytest.raises(DuplicateFileError):
        await resolve_async(
            db,
            intent="create",
            content=content,
            owner_id="u1",
            organization_id="org-xyz",
        )


@pytest.mark.asyncio
async def test_resolve_async_alias_returns_existing():
    content = b"shared content"
    checksum = compute_checksum(content)
    db = _FakeDB(
        existing_by_checksum={
            checksum: {
                "id": "33333333-3333-3333-3333-333333333333",
                "file_path": "team/shared.pdf",
                "created_at": "2026-04-01T00:00:00Z",
            }
        }
    )
    decision = await resolve_async(
        db,
        intent="alias_existing",
        content=content,
        owner_id="u1",
        organization_id="org-xyz",
    )
    assert decision.action == "return_existing"
    assert decision.canonical_file_id == "33333333-3333-3333-3333-333333333333"
    assert decision.lookup.scope == "org"


@pytest.mark.asyncio
async def test_resolve_async_force_new_copy_with_reason():
    content = b"already-uploaded content"
    checksum = compute_checksum(content)
    db = _FakeDB(
        existing_by_checksum={
            checksum: {
                "id": "44444444-4444-4444-4444-444444444444",
                "file_path": "old.pdf",
                "created_at": "2026-04-01T00:00:00Z",
            }
        }
    )
    decision = await resolve_async(
        db,
        intent="force_new_copy",
        content=content,
        owner_id="u1",
        organization_id="org-xyz",
        reason="client X requires a separate version",
    )
    assert decision.action == "write_alias"
    assert decision.canonical_file_id == "44444444-4444-4444-4444-444444444444"
    assert decision.reason == "client X requires a separate version"


@pytest.mark.asyncio
async def test_resolve_async_force_new_copy_missing_reason_raises():
    content = b"abc"
    db = _FakeDB(
        existing_by_checksum={
            compute_checksum(content): {
                "id": "55555555-5555-5555-5555-555555555555",
                "file_path": "f.pdf",
                "created_at": "2026-04-01T00:00:00Z",
            }
        }
    )
    with pytest.raises(MissingReasonError):
        await resolve_async(
            db,
            intent="force_new_copy",
            content=content,
            owner_id="u1",
            organization_id=None,
            reason="",
        )


@pytest.mark.asyncio
async def test_resolve_async_precomputed_checksum_skips_rehashing():
    content = b"large payload"
    precomputed = compute_checksum(content)
    db = _FakeDB()
    decision = await resolve_async(
        db,
        intent="create",
        content=content,
        owner_id="u1",
        organization_id=None,
        precomputed_checksum=precomputed,
    )
    assert decision.action == "write_new"
    # The DB was consulted with the precomputed hash.
    assert db.calls[0][0] == precomputed


@pytest.mark.asyncio
async def test_resolve_async_unknown_intent_raises():
    db = _FakeDB()
    with pytest.raises(InvalidIntentError):
        await resolve_async(
            db,
            intent="upsert",
            content=b"x",
            owner_id="u1",
            organization_id=None,
        )


# ── Error envelope shape (used by HTTP layer) ───────────────────────────


def test_duplicate_file_error_envelope_has_required_fields():
    err = DuplicateFileError(
        checksum=SAMPLE_CHECKSUM,
        existing_file_id="abc",
        existing_path="foo.pdf",
        existing_created_at="2026-05-01T00:00:00Z",
        scope="org",
    )
    payload = err.to_dict()
    required = {
        "error",
        "status_code",
        "message",
        "existing_file_id",
        "existing_path",
        "existing_created_at",
        "scope",
        "checksum",
        "allowed_intents",
    }
    assert required.issubset(payload.keys())
    assert payload["status_code"] == 409
