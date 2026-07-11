"""Canonical HTTP — one configured async client + one transient-retry policy.

Every server-to-server / third-party-API / webhook HTTP call in the Matrx
family goes through here, so timeout, connection limits, redirect behaviour,
proxy/CA handling, and retry-on-transient are decided ONCE rather than guessed
per call site. The repo scan found 187 ad-hoc clients with inconsistent or
absent timeouts and exactly one exponential backoff in the entire codebase —
this module is that whole class's single home.

🚫 NOT for user-supplied media URLs. Fetching a user's file/URL goes through
``FileManager.resolve_media_async`` (it recognises our share-link / ``/files/{id}``
shapes and pulls bytes from S3, not from share-page HTML). A raw GET on a media
URL is the file-contract rule-1 violation that has caused live incidents. Use
this client for *our* APIs and external services, never for resolving media.

    from matrx_utils import async_client, request_with_retries, fetch_json

    async with async_client(timeout=20) as client:                  # configured client
        resp = await request_with_retries(client, "GET", url)       # retries 429/5xx + transport errors
        resp.raise_for_status()

    data = await fetch_json("https://api.example.com/v1/thing")      # one-shot -> parsed JSON

``async_client`` sets ``trust_env=True``, so the standard ``HTTPS_PROXY`` /
``SSL_CERT_FILE`` environment (proxies, custom CA bundles) is honoured
automatically — never hard-wire a proxy or disable TLS verification.
"""
from __future__ import annotations

from asyncio import sleep as _sleep
from dataclasses import dataclass, field, replace
from typing import Any

import httpx

from .backoff import compute_backoff_ms

# Sane defaults — a real timeout on every call (httpx's own default is *no*
# timeout, which is how a single hung peer wedges a worker forever).
DEFAULT_TIMEOUT = httpx.Timeout(connect=10.0, read=30.0, write=30.0, pool=10.0)
DEFAULT_LIMITS = httpx.Limits(max_connections=100, max_keepalive_connections=20)

# Status codes worth retrying: rate-limit + the transient 5xx family. A 4xx
# (other than 429) is the caller's bug — retrying it just wastes time.
_RETRY_STATUSES = frozenset({429, 500, 502, 503, 504})


@dataclass(frozen=True)
class RetryPolicy:
    """How ``request_with_retries`` retries. ``attempts`` is the TOTAL tries
    (so ``attempts=3`` == 1 try + 2 retries). Backoff is full-jitter
    exponential: ``uniform(0, min(backoff_max, backoff_base * 2**attempt))``.
    A ``backoff_base`` of 0 disables sleeping (used by tests)."""

    attempts: int = 3
    backoff_base: float = 0.5
    backoff_max: float = 10.0
    respect_retry_after: bool = True
    retry_statuses: frozenset[int] = field(default_factory=lambda: _RETRY_STATUSES)


DEFAULT_RETRY = RetryPolicy()


def async_client(**overrides: Any) -> httpx.AsyncClient:
    """A configured :class:`httpx.AsyncClient` — the one way to open a client.

    Defaults: a real timeout on every phase, pooled connections, redirects
    followed, and ``trust_env=True`` (honours ``HTTPS_PROXY`` / ``SSL_CERT_FILE``).
    Any keyword overrides the default (e.g. ``async_client(timeout=20,
    headers={...})``). Use as ``async with async_client() as client: ...``.
    """
    kwargs: dict[str, Any] = {
        "timeout": DEFAULT_TIMEOUT,
        "limits": DEFAULT_LIMITS,
        "follow_redirects": True,
        "trust_env": True,
    }
    kwargs.update(overrides)
    return httpx.AsyncClient(**kwargs)


def _backoff_delay(attempt: int, policy: RetryPolicy) -> float:
    # Delegate the math to the canonical backoff primitive (seconds out). The
    # loop is 0-indexed, so the just-failed attempt is ``attempt + 1``.
    return compute_backoff_ms(
        attempt + 1,
        initial_ms=int(policy.backoff_base * 1000),
        max_ms=int(policy.backoff_max * 1000),
    ) / 1000


def _retry_delay(resp: httpx.Response, attempt: int, policy: RetryPolicy) -> float:
    if policy.respect_retry_after:
        header = resp.headers.get("retry-after")
        if header:
            try:
                return min(policy.backoff_max, float(header))
            except ValueError:
                pass  # HTTP-date form — fall back to computed backoff
    return _backoff_delay(attempt, policy)


async def request_with_retries(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    *,
    policy: RetryPolicy = DEFAULT_RETRY,
    **kwargs: Any,
) -> httpx.Response:
    """Issue a request, retrying transient transport errors and 429/5xx.

    Returns the final :class:`httpx.Response` (the LAST one, even if still a
    retryable status — the caller decides via ``raise_for_status()``). Honours a
    numeric ``Retry-After`` on 429/503. Non-transport exceptions and
    non-retryable statuses are returned/raised immediately, never retried.
    """
    if policy.attempts < 1:
        raise ValueError("RetryPolicy.attempts must be >= 1")
    last_exc: Exception | None = None
    for attempt in range(policy.attempts):
        is_last = attempt + 1 >= policy.attempts
        try:
            resp = await client.request(method, url, **kwargs)
        except httpx.TransportError as exc:  # timeouts, connect/read/pool/network
            last_exc = exc
            if is_last:
                raise
            await _sleep(_backoff_delay(attempt, policy))
            continue
        if resp.status_code in policy.retry_statuses and not is_last:
            await _sleep(_retry_delay(resp, attempt, policy))
            continue
        return resp
    raise last_exc  # pragma: no cover  (loop always returns or raises above)


async def fetch_json(
    url: str,
    *,
    method: str = "GET",
    policy: RetryPolicy = DEFAULT_RETRY,
    client_kwargs: dict[str, Any] | None = None,
    **request_kwargs: Any,
) -> Any:
    """One-shot retried request that returns parsed JSON.

    Opens a configured client, runs ``request_with_retries``, ``raise_for_status``,
    and returns ``resp.json()``. For the common case of a single call where a
    long-lived client is overkill. Pass ``client_kwargs`` to configure the
    client (headers, auth, base_url); other kwargs go to the request.
    """
    async with async_client(**(client_kwargs or {})) as client:
        resp = await request_with_retries(client, method, url, policy=policy, **request_kwargs)
        resp.raise_for_status()
        return resp.json()


def with_overrides(policy: RetryPolicy = DEFAULT_RETRY, **changes: Any) -> RetryPolicy:
    """A copy of ``policy`` with fields replaced — e.g.
    ``with_overrides(attempts=5, backoff_base=1.0)``."""
    return replace(policy, **changes)
