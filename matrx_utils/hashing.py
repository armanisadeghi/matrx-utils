"""Deterministic content hashing — the single way to turn data into a stable key.

Every dedup key, idempotency key, cache key, and content-address in the Matrx
family MUST come from here. The duplication this kills is the hand-rolled
``hashlib.sha256(json.dumps(x, sort_keys=True).encode()).hexdigest()`` scattered
across the codebase: tiny differences between copies (``separators``,
``default=str``, key ordering of *nested* objects) silently produce *different*
digests for the *same* data, which quietly corrupts dedup / idempotency. One
canonical serialization removes that whole failure class.

``stable_json`` is byte-faithful to the most-correct existing copy
(``file_handling/cloud_sync/idempotency.py``), so migrating those call sites to
``stable_hash`` does NOT change any already-emitted key.

    from matrx_utils import stable_hash
    key = stable_hash({"user": uid, "op": "ingest", "doc": doc_id})   # idempotency key
    short = stable_hash(spec, length=16)                              # short cache key
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable

_DEFAULT_ALGO = "sha256"


def stable_json(obj: Any) -> str:
    """Canonical, deterministic JSON encoding of any JSON-ish object.

    Sorted keys (at every depth), compact separators, and ``default=str`` so
    non-JSON scalars (``datetime`` / ``UUID`` / ``Decimal`` / enums) encode
    instead of raising. This is the one pre-hash serialization — same input
    always yields the same string, regardless of dict construction order.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def _truncate(digest: str, length: int | None) -> str:
    if length is None:
        return digest
    if length <= 0:
        raise ValueError("length must be a positive number of hex chars")
    return digest[:length]


def stable_hash(obj: Any, *, algo: str = _DEFAULT_ALGO, length: int | None = None) -> str:
    """Deterministic hex digest of any JSON-serializable object.

    The canonical key for dedup / idempotency / caching / content-addressing.
    ``length`` truncates the hex digest (e.g. ``length=16`` for a short key);
    ``algo`` is any ``hashlib`` algorithm name.
    """
    return _truncate(hashlib.new(algo, stable_json(obj).encode("utf-8")).hexdigest(), length)


def hash_text(text: str, *, algo: str = _DEFAULT_ALGO, length: int | None = None) -> str:
    """Hex digest of a string (UTF-8 encoded). For already-serialized text / URLs."""
    return _truncate(hashlib.new(algo, text.encode("utf-8")).hexdigest(), length)


def hash_bytes(data: bytes, *, algo: str = _DEFAULT_ALGO, length: int | None = None) -> str:
    """Hex digest of raw bytes. For in-memory file content / binary blobs."""
    return _truncate(hashlib.new(algo, data).hexdigest(), length)


def hash_chunks(chunks: Iterable[bytes], *, algo: str = _DEFAULT_ALGO, length: int | None = None) -> str:
    """Hex digest of a stream of byte chunks — hashes incrementally, never

    buffering the whole payload. For large files read in pieces.
    """
    h = hashlib.new(algo)
    for chunk in chunks:
        h.update(chunk)
    return _truncate(h.hexdigest(), length)
