"""Canonical ``data:`` URI handling — encode / decode / detect / strip, one way.

The repo hand-rolls this ~10+ times: ``f"data:{mime};base64,{b64}"`` to build,
``startswith("data:image")`` + ``split(",",1)[1]`` to strip, ad-hoc ``;base64,``
checks to detect. Each copy handles a slightly different subset (base64 only, no
mime parse, no non-base64 form), so they disagree at the edges. This is the one
home — RFC 2397 aware (base64 *and* percent-encoded forms, mime extraction).

    from matrx_utils import encode_data_uri, decode_data_uri, is_data_uri, strip_data_uri

    uri = encode_data_uri(png_bytes, "image/png")     # "data:image/png;base64,iVBOR..."
    data, mime = decode_data_uri(uri)                  # (b"\\x89PNG...", "image/png")
    payload = strip_data_uri(maybe_uri)                # base64/payload string, prefix removed
"""
from __future__ import annotations

import base64
from urllib.parse import unquote_to_bytes


def is_data_uri(value: object) -> bool:
    """True if ``value`` is a ``data:`` URI string (has the scheme and a comma)."""
    return isinstance(value, str) and value.startswith("data:") and "," in value[:512]


def encode_data_uri(data: bytes, mime: str) -> str:
    """Bytes → a base64 ``data:`` URI: ``data:<mime>;base64,<b64>``."""
    return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"


def decode_data_uri(value: str) -> tuple[bytes, str | None]:
    """Decode a ``data:`` URI to ``(bytes, mime)``.

    Handles both the base64 form (``;base64,``) and the percent-encoded form,
    and returns the declared mime type (``None`` when the URI omits it). Raises
    ``ValueError`` on a non-``data:`` value or a missing comma — never guesses.
    """
    if not isinstance(value, str) or not value.startswith("data:"):
        raise ValueError("not a data URI (missing 'data:' scheme)")
    header, comma, payload = value[len("data:"):].partition(",")
    if not comma:
        raise ValueError("malformed data URI (missing ',' separator)")
    is_b64 = header.endswith(";base64")
    meta = header[: -len(";base64")] if is_b64 else header
    mime = (meta.split(";", 1)[0] or None)  # drop ;charset=…; an empty mediatype → None
    data = base64.b64decode(payload) if is_b64 else unquote_to_bytes(payload)
    return data, mime


def strip_data_uri(value: str) -> str:
    """Return the payload after the comma when ``value`` is a ``data:`` URI, else

    ``value`` unchanged — the "drop the ``data:image/...;base64,`` prefix, keep the
    base64 string" idiom, made safe (passthrough for a bare base64 string).
    """
    if isinstance(value, str) and value.startswith("data:"):
        _, comma, payload = value.partition(",")
        if comma:
            return payload
    return value
