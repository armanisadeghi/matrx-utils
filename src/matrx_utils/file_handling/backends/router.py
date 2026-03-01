"""BackendRouter — URI scheme detection, URL parsing, retry, and dispatch.

Supported URI schemes (native)
------------------------------
    s3://bucket/path/to/file.ext
    supabase://bucket/path/to/file.ext
    server://path/to/file.ext

Supported HTTPS URLs (auto-converted to native, then read via credentials)
---------------------------------------------------------------------------
    Supabase public:  https://<ref>.supabase.co/storage/v1/object/public/bucket/path
    Supabase signed:  https://<ref>.supabase.co/storage/v1/object/sign/bucket/path?token=...
    S3 virtual-host:  https://bucket.s3.region.amazonaws.com/key[?X-Amz-Signature=...]
    S3 path-style:    https://s3.region.amazonaws.com/bucket/key

Retry policy
------------
    read() and write() automatically retry on transient failures:
        - Up to MAX_RETRIES attempts total (default 3)
        - Exponential backoff: 0.5 s, 1 s, 2 s
        - Retried: network errors, HTTP 429, HTTP 5xx
        - NOT retried: HTTP 403, HTTP 404, ValueError, RuntimeError
          (these are logic / config errors, not transient)

BackendRouter is lazily initialised — backend instances are created on
first use so that import-time costs and misconfigured-but-unused backends
do not cause errors.
"""

from __future__ import annotations

import time
import logging
from urllib.parse import urlparse

from .base_backend import StorageBackend
from .s3_backend import S3Backend
from .supabase_backend import SupabaseBackend
from .server_backend import ServerBackend
from .url_parser import parse_storage_url, is_storage_url

logger = logging.getLogger(__name__)

CLOUD_SCHEMES: frozenset[str] = frozenset({"s3", "supabase", "server"})

_MAX_RETRIES: int = 3
_RETRY_BACKOFF: tuple[float, ...] = (0.5, 1.0, 2.0)

# Error message fragments that indicate a transient failure worth retrying.
# Permanent errors (403, 404, bad path, not-configured) are never retried.
_TRANSIENT_FRAGMENTS: tuple[str, ...] = (
    "timeout",
    "timed out",
    "connection",
    "network",
    "throttl",
    "rate limit",
    "503",
    "502",
    "500",
    "429",
    "temporarily unavailable",
    "service unavailable",
    "internal server error",
)

_PERMANENT_FRAGMENTS: tuple[str, ...] = (
    "403",
    "404",
    "forbidden",
    "not found",
    "nosuchkey",
    "nosuchbucket",
    "access denied",
    "not configured",
    "invalid",
    "no such",
)


def _is_transient(exc: Exception) -> bool:
    """Return True if *exc* looks like a transient failure worth retrying."""
    msg = str(exc).lower()
    # Permanent errors take priority — never retry these.
    for fragment in _PERMANENT_FRAGMENTS:
        if fragment in msg:
            return False
    for fragment in _TRANSIENT_FRAGMENTS:
        if fragment in msg:
            return True
    # ConnectionError and TimeoutError subclasses are always transient.
    return isinstance(exc, (ConnectionError, TimeoutError, OSError))


def _url_seconds_remaining(url: str) -> float | None:
    """Return seconds until *url* expires, or None if it has no expiry.

    Reads expiry purely from the URL itself — no network call, no secret key.

    Supabase signed URLs: JWT token in ?token= query param; read 'exp' claim.
    S3 presigned URLs: X-Amz-Date + X-Amz-Expires in query params.
    Public/unknown URLs: return None (treat as non-expiring).
    """
    import time
    import base64
    import json as _json
    from urllib.parse import urlparse, parse_qs
    from datetime import datetime, timezone

    parsed = urlparse(url)
    qs = parse_qs(parsed.query)

    # Supabase signed URL — JWT token
    token_parts = qs.get("token", [""])[0]
    if token_parts:
        parts = token_parts.split(".")
        if len(parts) == 3:
            try:
                padding = 4 - len(parts[1]) % 4
                payload = _json.loads(
                    base64.urlsafe_b64decode(parts[1] + "=" * padding)
                )
                exp = payload.get("exp")
                if exp:
                    return float(exp) - time.time()
            except Exception:
                pass

    # S3 presigned URL — X-Amz-Date + X-Amz-Expires
    amz_date = qs.get("X-Amz-Date", [""])[0]
    amz_expires = qs.get("X-Amz-Expires", [""])[0]
    if amz_date and amz_expires:
        try:
            issued = datetime.strptime(amz_date, "%Y%m%dT%H%M%SZ").replace(
                tzinfo=timezone.utc
            )
            expires_at = issued.timestamp() + int(amz_expires)
            return expires_at - time.time()
        except Exception:
            pass

    return None  # no expiry information found


def _with_retry(fn, *args, **kwargs):
    """Call *fn* with retry/backoff on transient errors.

    On a permanent error (403, 404, not-configured, etc.) the exception
    is re-raised immediately without any retry.
    """
    last_exc: Exception | None = None
    for attempt in range(_MAX_RETRIES):
        try:
            return fn(*args, **kwargs)
        except (ValueError, RuntimeError) as exc:
            # Config / logic errors — never retry.
            raise
        except Exception as exc:
            if not _is_transient(exc):
                raise
            last_exc = exc
            if attempt < _MAX_RETRIES - 1:
                delay = _RETRY_BACKOFF[min(attempt, len(_RETRY_BACKOFF) - 1)]
                logger.warning(
                    "Transient error on attempt %d/%d (%s). Retrying in %.1fs…",
                    attempt + 1,
                    _MAX_RETRIES,
                    exc,
                    delay,
                )
                time.sleep(delay)
    raise last_exc  # type: ignore[misc]


async def _with_retry_async(fn, *args, **kwargs):
    """Async version of _with_retry — same policy, awaits the coroutine."""
    last_exc: Exception | None = None
    for attempt in range(_MAX_RETRIES):
        try:
            return await fn(*args, **kwargs)
        except (ValueError, RuntimeError):
            raise
        except Exception as exc:
            if not _is_transient(exc):
                raise
            last_exc = exc
            if attempt < _MAX_RETRIES - 1:
                import asyncio
                delay = _RETRY_BACKOFF[min(attempt, len(_RETRY_BACKOFF) - 1)]
                logger.warning(
                    "Transient error on attempt %d/%d (%s). Retrying in %.1fs…",
                    attempt + 1,
                    _MAX_RETRIES,
                    exc,
                    delay,
                )
                await asyncio.sleep(delay)
    raise last_exc  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Module-level helpers (kept for backward compat)
# ---------------------------------------------------------------------------

def is_cloud_uri(path: str) -> bool:
    """Return True if *path* is a native cloud URI (s3://, supabase://, server://)
    OR an HTTPS URL pointing at a recognised cloud storage provider."""
    if "://" not in path:
        return False
    scheme = path.split("://", 1)[0].lower()
    if scheme in CLOUD_SCHEMES:
        return True
    if scheme in ("http", "https"):
        return is_storage_url(path)
    return False


def parse_uri(uri: str) -> tuple[str, str]:
    """Parse a native cloud URI and return (scheme, path-without-scheme).

    For HTTPS URLs use parse_storage_url() from url_parser instead.

    Examples
    --------
    >>> parse_uri("s3://my-bucket/reports/jan.json")
    ('s3', 'my-bucket/reports/jan.json')
    >>> parse_uri("supabase://avatars/user1.png")
    ('supabase', 'avatars/user1.png')
    >>> parse_uri("server://uploads/file.txt")
    ('server', 'uploads/file.txt')
    """
    parsed = urlparse(uri)
    scheme = parsed.scheme.lower()
    if scheme not in CLOUD_SCHEMES:
        raise ValueError(
            f"Unrecognised cloud URI scheme '{scheme}' in '{uri}'. "
            f"Supported schemes: {sorted(CLOUD_SCHEMES)}"
        )
    netloc = parsed.netloc
    path = parsed.path.lstrip("/")
    full_path = f"{netloc}/{path}" if netloc and path else netloc or path
    return scheme, full_path


class BackendRouter:
    """Holds one lazily-created instance of each cloud backend and routes
    read/write/delete/append/get_url/list_files/read_url calls to the
    correct one, with automatic retry on transient failures.
    """

    def __init__(self) -> None:
        self._s3: S3Backend | None = None
        self._supabase: SupabaseBackend | None = None
        self._server: ServerBackend | None = None

    # ------------------------------------------------------------------
    # Lazy backend accessors
    # ------------------------------------------------------------------

    @property
    def s3(self) -> S3Backend:
        if self._s3 is None:
            self._s3 = S3Backend()
        return self._s3

    @property
    def supabase(self) -> SupabaseBackend:
        if self._supabase is None:
            self._supabase = SupabaseBackend()
        return self._supabase

    @property
    def server(self) -> ServerBackend:
        if self._server is None:
            self._server = ServerBackend()
        return self._server

    # ------------------------------------------------------------------
    # Internal dispatch
    # ------------------------------------------------------------------

    def _resolve(self, uri: str) -> tuple[StorageBackend, str]:
        """Return (backend, storage_path) for any URI or HTTPS URL."""
        parsed_scheme = uri.split("://", 1)[0].lower() if "://" in uri else ""

        if parsed_scheme in ("http", "https"):
            result = parse_storage_url(uri)
            scheme: str = result.scheme
            path: str = result.storage_path
        else:
            scheme, path = parse_uri(uri)

        backends: dict[str, StorageBackend] = {
            "s3": self.s3,
            "supabase": self.supabase,
            "server": self.server,
        }
        return backends[scheme], path

    # ------------------------------------------------------------------
    # Public routing API — mirrors StorageBackend interface
    # ------------------------------------------------------------------

    def read(self, uri: str) -> bytes:
        """Read bytes from *uri* with automatic retry on transient errors."""
        backend, path = self._resolve(uri)
        return _with_retry(backend.read, path)

    def write(self, uri: str, content: bytes | str, **kwargs) -> bool:
        """Write *content* to *uri* with automatic retry on transient errors."""
        backend, path = self._resolve(uri)
        return _with_retry(backend.write, path, content, **kwargs)

    def append(self, uri: str, content: bytes | str) -> bool:
        backend, path = self._resolve(uri)
        return _with_retry(backend.append, path, content)

    def delete(self, uri: str) -> bool:
        backend, path = self._resolve(uri)
        return backend.delete(path)

    def get_url(self, uri: str, expires_in: int = 3600) -> str:
        backend, path = self._resolve(uri)
        return backend.get_url(path, expires_in=expires_in)

    def list_files(self, uri_prefix: str = "") -> list[str]:
        if not uri_prefix:
            raise ValueError(
                "list_files() requires a URI prefix with a scheme, "
                "e.g. 's3://bucket/folder/' or 'supabase://bucket/'."
            )
        backend, path = self._resolve(uri_prefix)
        raw: list[str] = backend.list_files(path)
        scheme = uri_prefix.split("://", 1)[0].lower()
        return [f"{scheme}://{item}" for item in raw]

    # ------------------------------------------------------------------
    # read_url — the "React sent me a URL" entry point
    # ------------------------------------------------------------------

    def read_url(self, url: str) -> bytes:
        """Read bytes from any URL format that a client might send.

        Unlike read(), this method accepts HTTPS URLs (public, signed,
        presigned) in addition to native cloud URIs. The URL is parsed
        back to a (backend, storage_path) pair and the file is fetched
        using server-side credentials — token expiry, signature
        validity, and URL format are all irrelevant.

        Supported inputs
        ----------------
        - supabase://bucket/path/file.ext
        - s3://bucket/path/file.ext
        - https://<ref>.supabase.co/storage/v1/object/public/bucket/path
        - https://<ref>.supabase.co/storage/v1/object/sign/bucket/path?token=...
        - https://bucket.s3.region.amazonaws.com/key[?X-Amz-Signature=...]
        - https://s3.region.amazonaws.com/bucket/key

        Raises
        ------
        ValueError
            If the URL cannot be recognised as a supported storage URL.
        RuntimeError
            If the relevant backend is not configured (missing credentials).
        """
        return _with_retry(self._read_url_once, url)

    def _read_url_once(self, url: str) -> bytes:
        backend, path = self._resolve(url)
        return backend.read(path)

    # ------------------------------------------------------------------
    # Status helpers
    # ------------------------------------------------------------------

    def is_configured(self, scheme: str) -> bool:
        """Return True if the backend for *scheme* is ready to use."""
        scheme = scheme.lower()
        if scheme == "s3":
            return self.s3.is_configured()
        if scheme == "supabase":
            return self.supabase.is_configured()
        if scheme == "server":
            return self.server.is_configured()
        raise ValueError(f"Unknown scheme '{scheme}'.")

    def configured_backends(self) -> list[str]:
        """Return the list of scheme names for all configured backends."""
        result: list[str] = []
        if self.s3.is_configured():
            result.append("s3")
        if self.supabase.is_configured():
            result.append("supabase")
        if self.server.is_configured():
            result.append("server")
        return result

    # ------------------------------------------------------------------
    # Async routing API
    # ------------------------------------------------------------------

    async def read_async(self, uri: str) -> bytes:
        """Non-blocking read. Use in FastAPI routes and all async contexts."""
        backend, path = self._resolve(uri)
        return await _with_retry_async(backend.read_async, path)

    async def write_async(self, uri: str, content: bytes | str, **kwargs) -> bool:
        """Non-blocking write."""
        backend, path = self._resolve(uri)
        return await _with_retry_async(backend.write_async, path, content, **kwargs)

    async def append_async(self, uri: str, content: bytes | str) -> bool:
        backend, path = self._resolve(uri)
        return await _with_retry_async(backend.append_async, path, content)

    async def delete_async(self, uri: str) -> bool:
        backend, path = self._resolve(uri)
        return await backend.delete_async(path)

    async def get_url_async(self, uri: str, expires_in: int = 3600) -> str:
        backend, path = self._resolve(uri)
        return await backend.get_url_async(path, expires_in=expires_in)

    async def list_files_async(self, uri_prefix: str = "") -> list[str]:
        if not uri_prefix:
            raise ValueError(
                "list_files_async() requires a URI prefix with a scheme."
            )
        backend, path = self._resolve(uri_prefix)
        raw: list[str] = await backend.list_files_async(path)
        scheme = uri_prefix.split("://", 1)[0].lower()
        return [f"{scheme}://{item}" for item in raw]

    async def read_url_async(self, url: str) -> bytes:
        """Non-blocking read from any URL format a client might send."""
        return await _with_retry_async(self._read_url_once_async, url)

    async def _read_url_once_async(self, url: str) -> bytes:
        backend, path = self._resolve(url)
        return await backend.read_async(path)

    # ------------------------------------------------------------------
    # ensure_url — smart URL refresh without unnecessary network calls
    # ------------------------------------------------------------------

    def ensure_url(self, url: str, expires_in: int = 3600) -> str:
        """Return a guaranteed-valid URL for a cloud file.

        Logic (zero network calls when URL is still fresh):
        1. If *url* is a native cloud URI (s3://, supabase://) — generate
           a fresh signed URL directly. No expiry check needed.
        2. If *url* is a Supabase signed URL — decode the JWT payload and
           read the 'exp' claim without any network call or secret key.
           Return the original URL if it has ≥ *buffer_seconds* remaining.
        3. If *url* is an S3 presigned URL — read X-Amz-Date + X-Amz-Expires
           from the query string. Return the original if still valid.
        4. If *url* is a public (non-expiring) HTTPS URL — return it as-is.
        5. If expired (or unrecognised format) — parse to storage path,
           generate a fresh signed URL via backend credentials, return it.

        Parameters
        ----------
        url:
            Any URL or URI for a cloud file.
        expires_in:
            Expiry for the *new* URL when one needs to be generated (seconds).
        """
        from .url_parser import parse_storage_url
        import time

        # Native URIs have no expiry — generate a fresh signed URL
        parsed_scheme = url.split("://", 1)[0].lower() if "://" in url else ""
        if parsed_scheme in CLOUD_SCHEMES:
            result = parse_storage_url(url)
            backend, path = self._resolve(url)
            return backend.get_url(path, expires_in=expires_in)

        # HTTPS URL — check if it carries expiry information
        remaining = _url_seconds_remaining(url)
        if remaining is None:
            # Public / non-expiring URL — return as-is
            return url
        if remaining > 60:
            # More than 60 s left — safe to use as-is
            return url

        # Expired or about to expire — regenerate via credentials
        result = parse_storage_url(url)
        backend, path = self._resolve(result.to_native_uri())
        return backend.get_url(path, expires_in=expires_in)

    async def ensure_url_async(self, url: str, expires_in: int = 3600) -> str:
        """Async version of ensure_url()."""
        from .url_parser import parse_storage_url

        parsed_scheme = url.split("://", 1)[0].lower() if "://" in url else ""
        if parsed_scheme in CLOUD_SCHEMES:
            backend, path = self._resolve(url)
            return await backend.get_url_async(path, expires_in=expires_in)

        remaining = _url_seconds_remaining(url)
        if remaining is None:
            return url
        if remaining > 60:
            return url

        result = parse_storage_url(url)
        backend, path = self._resolve(result.to_native_uri())
        return await backend.get_url_async(path, expires_in=expires_in)
