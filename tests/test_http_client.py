"""Level 1: matrx_utils.http_client — configured client + transient-retry policy.

No network: ``httpx.MockTransport`` drives the handler, ``backoff_base=0`` plus a
recorded no-op ``_sleep`` make the retry logic deterministic and instant.
"""
import httpx
import pytest

from matrx_utils import (
    DEFAULT_RETRY,
    RetryPolicy,
    async_client,
    fetch_json,
    request_with_retries,
    with_overrides,
)
from matrx_utils import http_client as hc


@pytest.fixture
def recorded_sleeps(monkeypatch):
    sleeps: list[float] = []

    async def fake_sleep(delay):
        sleeps.append(delay)

    monkeypatch.setattr(hc, "_sleep", fake_sleep)
    return sleeps


def _client_with(handler):
    return async_client(transport=httpx.MockTransport(handler))


# --------------------------------------------------------------------------- #
# async_client defaults
# --------------------------------------------------------------------------- #

@pytest.mark.asyncio
async def test_async_client_defaults_and_overrides():
    async with async_client() as c:
        assert c.follow_redirects is True
    async with async_client(follow_redirects=False) as c:
        assert c.follow_redirects is False  # caller override wins over the default


# --------------------------------------------------------------------------- #
# request_with_retries
# --------------------------------------------------------------------------- #

@pytest.mark.asyncio
async def test_retries_transient_5xx_then_succeeds(recorded_sleeps):
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        return httpx.Response(200, json={"ok": True}) if calls["n"] >= 3 else httpx.Response(503)

    async with _client_with(handler) as client:
        resp = await request_with_retries(
            client, "GET", "https://x/y", policy=RetryPolicy(attempts=3, backoff_base=0)
        )
    assert resp.status_code == 200
    assert calls["n"] == 3
    assert len(recorded_sleeps) == 2  # slept between the three attempts


@pytest.mark.asyncio
async def test_returns_final_response_when_exhausted(recorded_sleeps):
    def handler(request):
        return httpx.Response(503)

    async with _client_with(handler) as client:
        resp = await request_with_retries(
            client, "GET", "https://x/y", policy=RetryPolicy(attempts=2, backoff_base=0)
        )
    assert resp.status_code == 503  # returned, not raised
    assert len(recorded_sleeps) == 1


@pytest.mark.asyncio
async def test_does_not_retry_client_error(recorded_sleeps):
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        return httpx.Response(404)

    async with _client_with(handler) as client:
        resp = await request_with_retries(
            client, "GET", "https://x/y", policy=RetryPolicy(attempts=3, backoff_base=0)
        )
    assert resp.status_code == 404
    assert calls["n"] == 1
    assert recorded_sleeps == []  # a 4xx is the caller's bug — never retried


@pytest.mark.asyncio
async def test_retries_transport_error_then_succeeds(recorded_sleeps):
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        if calls["n"] == 1:
            raise httpx.ConnectError("boom", request=request)
        return httpx.Response(200, json={"ok": 1})

    async with _client_with(handler) as client:
        resp = await request_with_retries(
            client, "GET", "https://x/y", policy=RetryPolicy(attempts=2, backoff_base=0)
        )
    assert resp.status_code == 200
    assert calls["n"] == 2


@pytest.mark.asyncio
async def test_transport_error_reraised_when_exhausted(recorded_sleeps):
    def handler(request):
        raise httpx.ConnectError("down", request=request)

    async with _client_with(handler) as client:
        with pytest.raises(httpx.ConnectError):
            await request_with_retries(
                client, "GET", "https://x/y", policy=RetryPolicy(attempts=2, backoff_base=0)
            )


@pytest.mark.asyncio
async def test_honors_numeric_retry_after(recorded_sleeps):
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(429, headers={"Retry-After": "2"})
        return httpx.Response(200)

    async with _client_with(handler) as client:
        resp = await request_with_retries(
            client, "GET", "https://x/y", policy=RetryPolicy(attempts=2, backoff_base=0)
        )
    assert resp.status_code == 200
    assert recorded_sleeps == [2.0]  # the header, not the (zero) backoff


@pytest.mark.asyncio
async def test_invalid_attempts_raises():
    async with _client_with(lambda r: httpx.Response(200)) as client:
        with pytest.raises(ValueError):
            await request_with_retries(client, "GET", "https://x", policy=RetryPolicy(attempts=0))


# --------------------------------------------------------------------------- #
# fetch_json + with_overrides
# --------------------------------------------------------------------------- #

@pytest.mark.asyncio
async def test_fetch_json_returns_parsed_body(recorded_sleeps):
    transport = httpx.MockTransport(lambda r: httpx.Response(200, json={"hello": "world"}))
    data = await fetch_json("https://x/y", client_kwargs={"transport": transport})
    assert data == {"hello": "world"}


@pytest.mark.asyncio
async def test_fetch_json_raises_on_error_status(recorded_sleeps):
    transport = httpx.MockTransport(lambda r: httpx.Response(404))
    with pytest.raises(httpx.HTTPStatusError):
        await fetch_json("https://x/y", client_kwargs={"transport": transport})


def test_with_overrides_does_not_mutate_default():
    p = with_overrides(attempts=5, backoff_base=1.0)
    assert (p.attempts, p.backoff_base) == (5, 1.0)
    assert DEFAULT_RETRY.attempts == 3  # frozen original untouched
