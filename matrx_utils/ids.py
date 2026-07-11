"""Identifier generation — the single way to mint an id in the Matrx family.

``new_id()`` returns a fresh opaque id; ``new_id("req")`` returns a typed,
prefixed id (``req_<uuid>``). Centralizing this means the underlying scheme can
change in ONE place — e.g. uuid4 → a time-sortable uuid7 for index locality —
without touching the hundreds of ``str(uuid.uuid4())`` call sites it replaces.

    from matrx_utils import new_id
    request_id = new_id("req")     # "req_3f2c4d6e-...."
    row_id = new_id()              # "3f2c4d6e-...." (drop-in for str(uuid.uuid4()))
"""
from __future__ import annotations

import uuid


def new_uuid() -> uuid.UUID:
    """A fresh random :class:`uuid.UUID` (uuid4) object."""
    return uuid.uuid4()


def new_id(prefix: str | None = None, *, sep: str = "_") -> str:
    """A fresh unique id as a string.

    ``new_id()`` -> the standard dashed uuid4 string (a drop-in replacement for
    ``str(uuid.uuid4())``). ``new_id("req")`` -> ``"req_<uuid>"`` — a typed id
    whose prefix names the resource class. ``prefix`` must be non-empty when
    given; pass ``sep`` to override the ``_`` joiner.
    """
    base = str(uuid.uuid4())
    if prefix is None:
        return base
    if not prefix:
        raise ValueError("prefix must be a non-empty string (omit it for a bare id)")
    return f"{prefix}{sep}{base}"


def new_hex(length: int | None = None) -> str:
    """A fresh uuid4 as compact hex (no dashes) — the canonical short id.

    ``new_hex()`` -> 32 hex chars; ``new_hex(8)`` -> the first 8 (replaces the
    scattered ``uuid4().hex[:8]`` / ``str(uuid4()).replace("-","")[:8]`` idiom).
    Truncating discards entropy — below ~16 chars collisions become realistic,
    so only truncate for human-facing / low-cardinality labels, never for keys
    that must be globally unique.
    """
    full = uuid.uuid4().hex
    if length is None:
        return full
    if length <= 0:
        raise ValueError("length must be a positive number of hex chars")
    return full[:length]
