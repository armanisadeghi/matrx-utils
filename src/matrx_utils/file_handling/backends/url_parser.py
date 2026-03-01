"""Cloud URL parser — converts any URL format back to (scheme, storage_path).

Python should never read private files via a URL when it has credentials.
This module lets Python receive any URL format that React might send and
immediately convert it to the authoritative storage path so the read
goes through the backend API (immune to expiry, token revocation, etc.).

Supported input formats
-----------------------

Supabase
    Public:  https://abc.supabase.co/storage/v1/object/public/bucket/path/file.ext
    Signed:  https://abc.supabase.co/storage/v1/object/sign/bucket/path/file.ext?token=...
    Native:  supabase://bucket/path/file.ext

S3 virtual-hosted URL:
    Public:  https://bucket.s3.region.amazonaws.com/key
    Presigned: same URL + ?X-Amz-Signature=...&X-Amz-Expires=...

S3 path-style URL (legacy):
    https://s3.region.amazonaws.com/bucket/key

S3 native:
    s3://bucket/key

Server native:
    server://path/file.ext

All query strings (tokens, signatures, expiry) are stripped — they are
irrelevant when reading via credentials.
"""

from __future__ import annotations

import re
from urllib.parse import urlparse, ParseResult


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

class ParsedStorageUrl:
    """Result of parsing any cloud URL or URI."""

    __slots__ = ("scheme", "storage_path", "original")

    def __init__(self, scheme: str, storage_path: str, original: str) -> None:
        self.scheme: str = scheme
        self.storage_path: str = storage_path
        self.original: str = original

    def to_native_uri(self) -> str:
        """Return the canonical native URI: scheme://storage_path."""
        return f"{self.scheme}://{self.storage_path}"

    def __repr__(self) -> str:
        return (
            f"ParsedStorageUrl(scheme={self.scheme!r}, "
            f"storage_path={self.storage_path!r})"
        )


# ---------------------------------------------------------------------------
# Supabase URL detection
# ---------------------------------------------------------------------------

# Matches the project ref in: https://<ref>.supabase.co/...
_SUPABASE_HOST_RE = re.compile(r"^[a-z0-9]+\.supabase\.co$", re.IGNORECASE)

# /storage/v1/object/public/<bucket>/<path>
# /storage/v1/object/sign/<bucket>/<path>
# /storage/v1/object/authenticated/<bucket>/<path>   (private download)
_SUPABASE_STORAGE_RE = re.compile(
    r"^/storage/v1/object/(?:public|sign|authenticated)/([^/]+)/(.+)$"
)


def _try_parse_supabase_https(parsed: ParseResult) -> ParsedStorageUrl | None:
    host = parsed.netloc.lower()
    if not _SUPABASE_HOST_RE.match(host):
        return None
    m = _SUPABASE_STORAGE_RE.match(parsed.path)
    if not m:
        return None
    bucket: str = m.group(1)
    file_path: str = m.group(2)
    return ParsedStorageUrl("supabase", f"{bucket}/{file_path}", parsed.geturl())


# ---------------------------------------------------------------------------
# S3 URL detection
# ---------------------------------------------------------------------------

# Virtual-hosted: https://<bucket>.s3[.<region>].amazonaws.com/<key>
_S3_VHOSTED_RE = re.compile(
    r"^([a-z0-9][a-z0-9\-\.]{1,61}[a-z0-9])\.s3(?:\.[a-z0-9-]+)?\.amazonaws\.com$",
    re.IGNORECASE,
)

# Path-style (legacy): https://s3[.<region>].amazonaws.com/<bucket>/<key>
_S3_PATH_STYLE_RE = re.compile(
    r"^s3(?:\.[a-z0-9-]+)?\.amazonaws\.com$",
    re.IGNORECASE,
)


def _try_parse_s3_https(parsed: ParseResult) -> ParsedStorageUrl | None:
    host = parsed.netloc.lower()

    # Virtual-hosted style: bucket-name.s3.region.amazonaws.com/key
    m = _S3_VHOSTED_RE.match(host)
    if m:
        bucket: str = m.group(1)
        key: str = parsed.path.lstrip("/")
        if not key:
            return None
        return ParsedStorageUrl("s3", f"{bucket}/{key}", parsed.geturl())

    # Path-style: s3.region.amazonaws.com/bucket/key
    if _S3_PATH_STYLE_RE.match(host):
        parts = parsed.path.lstrip("/").split("/", 1)
        if len(parts) < 2 or not parts[1]:
            return None
        return ParsedStorageUrl("s3", f"{parts[0]}/{parts[1]}", parsed.geturl())

    return None


# ---------------------------------------------------------------------------
# Native URI passthrough (s3://, supabase://, server://)
# ---------------------------------------------------------------------------

_NATIVE_SCHEMES: frozenset[str] = frozenset({"s3", "supabase", "server"})


def _try_parse_native_uri(parsed: ParseResult, raw: str) -> ParsedStorageUrl | None:
    scheme = parsed.scheme.lower()
    if scheme not in _NATIVE_SCHEMES:
        return None
    netloc: str = parsed.netloc
    path: str = parsed.path.lstrip("/")
    storage_path: str = f"{netloc}/{path}" if netloc and path else netloc or path
    return ParsedStorageUrl(scheme, storage_path, raw)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def parse_storage_url(url: str) -> ParsedStorageUrl:
    """Parse any cloud URL or URI into a (scheme, storage_path) pair.

    Raises ValueError if the URL cannot be recognised as a supported
    cloud storage URL.

    Parameters
    ----------
    url:
        Any of:
        - Supabase public/signed HTTPS URL
        - S3 virtual-hosted or path-style HTTPS URL (with or without
          presigned query params)
        - Native cloud URI (s3://, supabase://, server://)

    Returns
    -------
    ParsedStorageUrl
        .scheme        — "s3", "supabase", or "server"
        .storage_path  — "bucket/path/to/file.ext"
        .to_native_uri() — "scheme://bucket/path/to/file.ext"
    """
    # Strip query string + fragment before parsing path segments.
    # Signed URLs embed tokens/signatures there; we never need them.
    parsed: ParseResult = urlparse(url)
    scheme: str = parsed.scheme.lower()

    if scheme in ("http", "https"):
        result = _try_parse_supabase_https(parsed) or _try_parse_s3_https(parsed)
        if result is not None:
            return result
        raise ValueError(
            f"Cannot determine storage backend from HTTPS URL: {url!r}\n"
            "Expected a Supabase storage URL (*.supabase.co/storage/v1/object/...) "
            "or an S3 URL (*.s3.amazonaws.com/...)."
        )

    if scheme in _NATIVE_SCHEMES:
        result = _try_parse_native_uri(parsed, url)
        if result is not None:
            return result

    raise ValueError(
        f"Unrecognised cloud storage URL: {url!r}\n"
        f"Supported formats: Supabase HTTPS, S3 HTTPS, "
        f"or a native URI (s3://, supabase://, server://)."
    )


def is_storage_url(url: str) -> bool:
    """Return True if *url* can be parsed as a cloud storage URL."""
    try:
        parse_storage_url(url)
        return True
    except ValueError:
        return False
