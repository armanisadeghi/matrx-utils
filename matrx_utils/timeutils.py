"""Time handling — the single way to read "now" and (de)serialize timestamps.

One opinion: every timestamp in the Matrx family is **timezone-aware UTC**,
serialized as ISO-8601. ``utcnow()`` replaces the deprecated
``datetime.utcnow()`` (which returns a NAIVE datetime — a latent bug the instant
it's compared against an aware one and raises ``TypeError``). ``parse_iso``
always returns an aware UTC datetime (tolerating a trailing ``Z``), so a parsed
value can be compared to ``utcnow()`` without a guard. ``to_iso`` always emits
UTC. Never scatter ``datetime.now()`` / bare ``fromisoformat`` — import here.

    from matrx_utils import utcnow, parse_iso, to_iso
    started = utcnow()
    when = parse_iso("2026-06-24T00:00:00Z")   # aware, UTC
    stamp = to_iso(when)                        # "2026-06-24T00:00:00+00:00"
"""
from __future__ import annotations

import datetime as _dt

UTC = _dt.timezone.utc


def utcnow() -> _dt.datetime:
    """Current time as a timezone-aware UTC datetime (never naive)."""
    return _dt.datetime.now(UTC)


def parse_iso(value: str) -> _dt.datetime:
    """Parse an ISO-8601 string to an aware UTC datetime.

    Tolerates a trailing ``Z`` (``2026-06-24T00:00:00Z``). A value carrying no
    timezone is assumed UTC and stamped aware; an aware value is converted to
    UTC. The result is ALWAYS aware, so comparing it to ``utcnow()`` never
    raises. Propagates ``ValueError`` from the stdlib on malformed input.
    """
    text = value.strip()
    if text[-1:] in ("Z", "z"):
        text = text[:-1] + "+00:00"
    parsed = _dt.datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def to_iso(value: _dt.datetime) -> str:
    """Serialize a datetime to an ISO-8601 UTC string. Naive input is assumed UTC."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).isoformat()
