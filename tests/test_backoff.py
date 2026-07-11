"""Level 1: matrx_utils.backoff — compute_backoff_ms + retry_async.

compute_backoff_ms is pure; retry_async uses a recorded no-op _sleep so the
retry logic runs instantly and the backoff delays are observable.
"""
import pytest

from matrx_utils import compute_backoff_ms, retry_async
from matrx_utils import backoff as bo


# --------------------------------------------------------------------------- #
# compute_backoff_ms — semantics preserved from matrx-graph
# --------------------------------------------------------------------------- #

def test_zero_and_none_return_zero():
    assert compute_backoff_ms(1, initial_ms=0, max_ms=10_000) == 0
    assert compute_backoff_ms(3, initial_ms=500, max_ms=10_000, strategy="none") == 0


def test_fixed_linear_exponential():
    assert compute_backoff_ms(5, initial_ms=200, max_ms=10_000, strategy="fixed") == 200
    assert compute_backoff_ms(3, initial_ms=200, max_ms=10_000, strategy="linear") == 600
    # exponential: initial * 2**(attempt-1)
    assert compute_backoff_ms(1, initial_ms=200, max_ms=10_000, strategy="exponential") == 200
    assert compute_backoff_ms(2, initial_ms=200, max_ms=10_000, strategy="exponential") == 400
    assert compute_backoff_ms(4, initial_ms=200, max_ms=10_000, strategy="exponential") == 1600


def test_cap_applies():
    assert compute_backoff_ms(10, initial_ms=1000, max_ms=5000, strategy="exponential") == 5000


def test_exponential_jitter_is_within_bounds_and_capped():
    # raw = 1000 * 2**(1-1) = 1000 -> value in [500, 1500]
    for _ in range(50):
        v = compute_backoff_ms(1, initial_ms=1000, max_ms=100_000, strategy="exponential_jitter")
        assert 500 <= v <= 1500
    # cap still applies after jitter
    for _ in range(50):
        v = compute_backoff_ms(8, initial_ms=1000, max_ms=2000, strategy="exponential_jitter")
        assert v <= 2000


def test_unknown_strategy_raises():
    with pytest.raises(ValueError):
        compute_backoff_ms(1, initial_ms=100, max_ms=1000, strategy="bogus")


# --------------------------------------------------------------------------- #
# retry_async
# --------------------------------------------------------------------------- #

@pytest.fixture
def recorded_sleeps(monkeypatch):
    sleeps: list[float] = []

    async def fake_sleep(delay):
        sleeps.append(delay)

    monkeypatch.setattr(bo, "_sleep", fake_sleep)
    return sleeps


@pytest.mark.asyncio
async def test_returns_first_success_without_sleeping(recorded_sleeps):
    calls = {"n": 0}

    async def ok():
        calls["n"] += 1
        return "done"

    assert await retry_async(ok) == "done"
    assert calls["n"] == 1
    assert recorded_sleeps == []


@pytest.mark.asyncio
async def test_retries_then_succeeds(recorded_sleeps):
    calls = {"n": 0}

    async def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ConnectionError("transient")
        return "ok"

    result = await retry_async(flaky, retry_on=(ConnectionError,), initial_ms=10, max_ms=100)
    assert result == "ok"
    assert calls["n"] == 3
    assert len(recorded_sleeps) == 2  # slept before attempts 2 and 3


@pytest.mark.asyncio
async def test_reraises_after_max_attempts(recorded_sleeps):
    async def always_fail():
        raise TimeoutError("nope")

    with pytest.raises(TimeoutError):
        await retry_async(always_fail, max_attempts=2, retry_on=(TimeoutError,), initial_ms=1)
    assert len(recorded_sleeps) == 1  # one sleep between the two attempts


@pytest.mark.asyncio
async def test_does_not_retry_unlisted_exception(recorded_sleeps):
    calls = {"n": 0}

    async def wrong_bug():
        calls["n"] += 1
        raise ValueError("a real bug, not transient")

    with pytest.raises(ValueError):
        await retry_async(wrong_bug, retry_on=(ConnectionError,))
    assert calls["n"] == 1
    assert recorded_sleeps == []


@pytest.mark.asyncio
async def test_on_retry_callback_receives_attempt_exc_delay(recorded_sleeps):
    seen = []

    async def flaky():
        raise ConnectionError("x")

    def on_retry(attempt, exc, delay_ms):
        seen.append((attempt, type(exc).__name__, delay_ms))

    with pytest.raises(ConnectionError):
        await retry_async(
            flaky, max_attempts=3, retry_on=(ConnectionError,),
            initial_ms=100, max_ms=10_000, strategy="exponential", on_retry=on_retry,
        )
    assert [s[0] for s in seen] == [1, 2]          # called before retries 2 and 3
    assert seen[0][1] == "ConnectionError"
    assert seen[0][2] == 100 and seen[1][2] == 200  # exponential, no jitter


@pytest.mark.asyncio
async def test_invalid_max_attempts():
    async def f():
        return 1

    with pytest.raises(ValueError):
        await retry_async(f, max_attempts=0)
