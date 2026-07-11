import re

_DATA_URL_RE = re.compile(r"^data:([^;,\s]+)(?:;[^,]*)?,", re.IGNORECASE)
_BASE64_CHARSET_RE = re.compile(r"^[A-Za-z0-9+/=_-]+$")
_JWT_RE = re.compile(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$")
_BEARER_RE = re.compile(r"^(Bearer\s+)(\S+)(.*)$", re.IGNORECASE | re.DOTALL)

_BLOB_KEY_PATTERNS = (
    "base64",
    "b64",
    "image_data",
    "pdf_data",
    "audio_data",
    "video_data",
    "data_url",
    "dataurl",
)

_SECRET_KEY_PATTERNS = (
    "authorization",
    "auth_token",
    "access_token",
    "refresh_token",
    "bearer",
    "cookie",
    "api_key",
    "apikey",
    "secret",
    "password",
    "jwt",
)

BLOB_MIN_LEN = 200
SECRET_MIN_LEN = 40


def _key_matches(key, patterns):
    if not isinstance(key, str):
        return False
    k = key.lower()
    return any(p in k for p in patterns)


def _truncate_blob(value):
    n = len(value)
    m = _DATA_URL_RE.match(value)
    if m:
        mime = m.group(1)
        return f"<data:{mime};base64 truncated, {n} chars>"
    return f"<base64 truncated, {n} chars>"


def _truncate_jwt(value):
    parts = value.split(".")
    head = parts[0][:24] + "…" if len(parts[0]) > 24 else parts[0]
    return f"<jwt truncated, {len(value)} chars, header={head}>"


def _truncate_secret(value):
    n = len(value)
    head = value[:8]
    return f"{head}…<+{n - 8} chars>"


def _looks_like_data_url(value):
    return value.startswith("data:") and ";base64," in value[:120]


def _looks_like_base64(value):
    if len(value) < BLOB_MIN_LEN:
        return False
    if "\n" in value or " " in value or "\t" in value:
        return False
    return bool(_BASE64_CHARSET_RE.match(value))


def _looks_like_jwt(value):
    if len(value) < SECRET_MIN_LEN or len(value) > 8192:
        return False
    return bool(_JWT_RE.match(value))


def _process_string(value, key, *, truncate_blobs, truncate_secrets, truncate_text):
    n = len(value)

    if truncate_blobs:
        if _looks_like_data_url(value) and n >= BLOB_MIN_LEN:
            return _truncate_blob(value)
        if _key_matches(key, _BLOB_KEY_PATTERNS) and n >= BLOB_MIN_LEN:
            return _truncate_blob(value)
        if _looks_like_base64(value):
            return _truncate_blob(value)

    if truncate_secrets:
        bm = _BEARER_RE.match(value)
        if bm and len(bm.group(2)) >= SECRET_MIN_LEN:
            return f"{bm.group(1)}{_truncate_secret(bm.group(2))}{bm.group(3)}"
        if _looks_like_jwt(value):
            return _truncate_jwt(value)
        if _key_matches(key, _SECRET_KEY_PATTERNS) and n >= SECRET_MIN_LEN:
            return _truncate_secret(value)

    if truncate_text and n > truncate_text:
        return f"{value[:truncate_text]}…<+{n - truncate_text} chars>"

    return value


def shorten_for_print(
    data,
    *,
    truncate_blobs=True,
    truncate_secrets=True,
    truncate_text=None,
):
    """
    Return a NEW basic-types tree with large blobs / secrets replaced by short markers.
    Input is never mutated. Cycle-safe via id() tracking.
    Intended to run AFTER to_matrx_json (input must be basic types: dict / list / str / int / float / bool / None).
    """
    seen = set()

    def walk(node, key=None):
        if isinstance(node, str):
            return _process_string(
                node,
                key,
                truncate_blobs=truncate_blobs,
                truncate_secrets=truncate_secrets,
                truncate_text=truncate_text,
            )
        if isinstance(node, dict):
            oid = id(node)
            if oid in seen:
                return "<cycle>"
            seen.add(oid)
            try:
                return {k: walk(v, key=k) for k, v in node.items()}
            finally:
                seen.discard(oid)
        if isinstance(node, list):
            oid = id(node)
            if oid in seen:
                return "<cycle>"
            seen.add(oid)
            try:
                return [walk(v, key=key) for v in node]
            finally:
                seen.discard(oid)
        return node

    return walk(data)


def shorten_string_for_print(
    value,
    *,
    truncate_blobs=True,
    truncate_secrets=True,
    truncate_text=None,
):
    if not isinstance(value, str):
        return value
    return _process_string(
        value,
        None,
        truncate_blobs=truncate_blobs,
        truncate_secrets=truncate_secrets,
        truncate_text=truncate_text,
    )
