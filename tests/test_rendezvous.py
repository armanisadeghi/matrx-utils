"""Exhaustive contract tests for matrx_utils.rendezvous.Rendezvous.

The primitive is a two-door meeting point (producer ``announce`` /
consumer ``on_present``) that must behave identically regardless of arrival
order, and must resolve every held note exactly once — via cache hit, via
announcement, via a DB-fallback "leak" run, or via a "broken promise" drop.

These tests cover the FULL cross-product:

  arrival order      × { producer-first, consumer-first, simultaneous }
  presence lifetime  × { fresh hit, boundary, expired }
  waiter resolution  × { announce, leak (verify TRUE), broken (verify FALSE),
                         no-verifier, verify raises }
  work outcome       × { success, raises }
  misc               × { coalesce, per-call ttl, idempotent announce,
                         multi-waiter, default verifier, boundaries }

A deterministic FakeClock lets us test a 5-minute TTL in zero wall-clock time;
two integration tests exercise the REAL background sweeper on a tiny TTL.
"""

from __future__ import annotations

import asyncio

from matrx_utils.rendezvous import Rendezvous


# --------------------------------------------------------------------------
# Test scaffolding
# --------------------------------------------------------------------------


class FakeClock:
    def __init__(self, t: float = 1000.0) -> None:
        self.t = t

    def __call__(self) -> float:
        return self.t

    def advance(self, dt: float) -> None:
        self.t += dt


def make_rv(**overrides):
    """A rendezvous with a manual clock and a captured alarm sink. The
    background sweeper is OFF — tests drive ``sweep()`` explicitly so timing is
    exact and deterministic."""
    clock = FakeClock()
    alarms: list[tuple[str, str, dict]] = []

    def alarm(level, message, fields):
        alarms.append((level, message, fields))

    params = dict(
        now=clock,
        alarm=alarm,
        autostart_sweeper=False,
        default_ttl=5.0,
        present_ttl=5.0,
    )
    params.update(overrides)
    return Rendezvous(**params), clock, alarms


def make_work(ran: list[str], name: str = "w", raises: Exception | None = None):
    async def do():
        if raises is not None:
            raise raises
        ran.append(name)

    return do


def make_verify(result: bool, *, calls: list | None = None, raises: Exception | None = None):
    async def verify(kind, id):
        if calls is not None:
            calls.append((kind, id))
        if raises is not None:
            raise raises
        return result

    return verify


def levels(alarms) -> list[str]:
    return [a[0] for a in alarms]


# --------------------------------------------------------------------------
# 1. Order independence — the whole point
# --------------------------------------------------------------------------


async def test_producer_first_then_consumer_hits_immediately():
    rv, _clock, alarms = make_rv()
    ran: list[str] = []

    rv.announce("Conversation", "abc")
    rv.on_present("Conversation", "abc", make_work(ran))
    await rv.drain()

    assert ran == ["w"]
    assert rv.stats.fired_on_hit == 1
    assert alarms == []


async def test_consumer_first_then_producer_fires_on_announce():
    rv, _clock, alarms = make_rv()
    ran: list[str] = []

    rv.on_present("Conversation", "abc", make_work(ran))
    assert rv.pending_count() == 1
    await rv.drain()
    assert ran == []  # nothing yet — boss hasn't arrived

    rv.announce("Conversation", "abc")
    await rv.drain()

    assert ran == ["w"]
    assert rv.stats.fired_on_announce == 1
    assert rv.pending_count() == 0
    assert alarms == []


async def test_announce_with_no_waiters_just_caches_presence():
    rv, _clock, alarms = make_rv()
    rv.announce("Conversation", "abc")
    assert rv.is_present("Conversation", "abc")
    assert rv.pending_count() == 0
    assert alarms == []


# --------------------------------------------------------------------------
# 2. Presence lifetime — fresh hit, boundary, expiry
# --------------------------------------------------------------------------


async def test_presence_hit_just_before_expiry():
    rv, clock, _alarms = make_rv(present_ttl=5.0)
    ran: list[str] = []
    rv.announce("K", "1")  # expiry = 1005.0
    clock.advance(4.999)
    rv.on_present("K", "1", make_work(ran))
    await rv.drain()
    assert ran == ["w"]
    assert rv.stats.fired_on_hit == 1


async def test_presence_miss_exactly_at_expiry_becomes_waiter():
    rv, clock, _alarms = make_rv(present_ttl=5.0)
    ran: list[str] = []
    rv.announce("K", "1")  # expiry = 1005.0
    clock.advance(5.0)  # now == expiry -> expired (expiry > now is False)
    rv.on_present("K", "1", make_work(ran))
    await rv.drain()
    assert ran == []  # no hit
    assert rv.pending_count() == 1
    assert not rv.is_present("K", "1")


async def test_expired_presence_then_reannounce_fires_waiter():
    rv, clock, alarms = make_rv(present_ttl=5.0, default_ttl=100.0)
    ran: list[str] = []
    rv.announce("K", "1")
    clock.advance(10.0)  # presence gone
    rv.on_present("K", "1", make_work(ran))  # becomes a waiter
    await rv.drain()
    assert ran == []
    rv.announce("K", "1")  # boss comes back
    await rv.drain()
    assert ran == ["w"]
    assert alarms == []


# --------------------------------------------------------------------------
# 3. Waiter expiry resolution — leak / broken / no-verifier
# --------------------------------------------------------------------------


async def test_waiter_expiry_verify_true_runs_with_leak_warning():
    rv, clock, alarms = make_rv(default_ttl=5.0)
    ran: list[str] = []
    calls: list = []
    rv.on_present("K", "1", make_work(ran), verify=make_verify(True, calls=calls))

    clock.advance(5.0)
    await rv.sweep()
    await rv.drain()

    assert ran == ["w"]  # slipped by, but we still did the work
    assert calls == [("K", "1")]  # the DB fallback fired
    assert rv.stats.fired_on_leak == 1
    assert levels(alarms) == ["warning"]  # HELL TO PAY, yellow edition


async def test_waiter_expiry_verify_false_drops_with_critical_alarm():
    rv, clock, alarms = make_rv(default_ttl=5.0)
    ran: list[str] = []
    rv.on_present("K", "1", make_work(ran), verify=make_verify(False))

    clock.advance(5.0)
    await rv.sweep()
    await rv.drain()

    assert ran == []  # broken promise — work dropped
    assert rv.stats.dropped_broken == 1
    assert levels(alarms) == ["critical"]  # terminal goes RED


async def test_waiter_expiry_without_any_verifier_is_broken_promise():
    rv, clock, alarms = make_rv(default_ttl=5.0, verifier=None)
    ran: list[str] = []
    rv.on_present("K", "1", make_work(ran))  # no per-call verify either

    clock.advance(5.0)
    await rv.sweep()
    await rv.drain()

    assert ran == []
    assert rv.stats.dropped_broken == 1
    assert levels(alarms) == ["critical"]


async def test_default_verifier_used_when_waiter_omits_one():
    rv, clock, alarms = make_rv(default_ttl=5.0, verifier=make_verify(True))
    ran: list[str] = []
    rv.on_present("K", "1", make_work(ran))  # relies on the injected default

    clock.advance(5.0)
    await rv.sweep()
    await rv.drain()

    assert ran == ["w"]
    assert rv.stats.fired_on_leak == 1
    assert levels(alarms) == ["warning"]


# --------------------------------------------------------------------------
# 4. Waiter deadline boundaries
# --------------------------------------------------------------------------


async def test_waiter_not_resolved_before_deadline():
    rv, clock, alarms = make_rv(default_ttl=5.0)
    ran: list[str] = []
    rv.on_present("K", "1", make_work(ran), verify=make_verify(False))

    clock.advance(4.999)
    await rv.sweep()
    await rv.drain()

    assert rv.pending_count() == 1  # still waiting
    assert alarms == []
    assert ran == []


async def test_waiter_resolved_exactly_at_deadline():
    rv, clock, alarms = make_rv(default_ttl=5.0)
    ran: list[str] = []
    rv.on_present("K", "1", make_work(ran), verify=make_verify(True))

    clock.advance(5.0)  # deadline == now -> resolves (deadline <= now)
    await rv.sweep()
    await rv.drain()

    assert rv.pending_count() == 0
    assert ran == ["w"]


async def test_per_call_ttl_overrides_default():
    rv, clock, alarms = make_rv(default_ttl=100.0)
    ran: list[str] = []
    rv.on_present("K", "1", make_work(ran), verify=make_verify(False), ttl=2.0)

    clock.advance(1.999)
    await rv.sweep()
    await rv.drain()
    assert rv.pending_count() == 1  # 2s window not up yet

    clock.advance(0.001)  # now at 2.0
    await rv.sweep()
    await rv.drain()
    assert rv.stats.dropped_broken == 1


async def test_present_ttl_independent_of_wait_ttl():
    # A short presence window but a long wait window.
    rv, clock, alarms = make_rv(present_ttl=3.0, default_ttl=100.0)
    ran: list[str] = []
    rv.announce("K", "1")
    clock.advance(4.0)  # presence expired (3s), but consumer arrives late
    rv.on_present("K", "1", make_work(ran))  # -> waiter, not hit
    assert rv.pending_count() == 1
    await rv.drain()
    assert ran == []


# --------------------------------------------------------------------------
# 5. Multiple waiters on one key
# --------------------------------------------------------------------------


async def test_multiple_waiters_all_fire_on_announce():
    rv, _clock, alarms = make_rv()
    ran: list[str] = []
    rv.on_present("K", "1", make_work(ran, "a"), label="a")
    rv.on_present("K", "1", make_work(ran, "b"), label="b")
    assert rv.pending_count("K", "1") == 2

    rv.announce("K", "1")
    await rv.drain()

    assert sorted(ran) == ["a", "b"]
    assert rv.stats.fired_on_announce == 2
    assert alarms == []


async def test_multiple_waiters_resolve_independently_on_expiry():
    rv, clock, alarms = make_rv(default_ttl=5.0)
    ran: list[str] = []
    rv.on_present("K", "1", make_work(ran, "leak"), verify=make_verify(True), label="leak")
    rv.on_present("K", "1", make_work(ran, "gone"), verify=make_verify(False), label="gone")

    clock.advance(5.0)
    await rv.sweep()
    await rv.drain()

    assert ran == ["leak"]  # only the one whose row slipped by
    assert rv.stats.fired_on_leak == 1
    assert rv.stats.dropped_broken == 1
    assert sorted(levels(alarms)) == ["critical", "warning"]


async def test_waiters_on_different_keys_are_isolated():
    rv, _clock, alarms = make_rv()
    ran: list[str] = []
    rv.on_present("K", "1", make_work(ran, "one"), label="one")
    rv.on_present("K", "2", make_work(ran, "two"), label="two")

    rv.announce("K", "1")
    await rv.drain()

    assert ran == ["one"]
    assert rv.pending_count("K", "2") == 1


# --------------------------------------------------------------------------
# 6. Work + verify failure never vanish
# --------------------------------------------------------------------------


async def test_work_that_raises_routes_to_error_alarm():
    rv, _clock, alarms = make_rv()
    rv.announce("K", "1")
    rv.on_present("K", "1", make_work([], raises=ValueError("boom")))
    await rv.drain()

    assert rv.stats.work_errors == 1
    assert levels(alarms) == ["error"]


async def test_verify_that_raises_is_treated_as_not_present():
    rv, clock, alarms = make_rv(default_ttl=5.0)
    ran: list[str] = []
    rv.on_present(
        "K", "1", make_work(ran), verify=make_verify(False, raises=RuntimeError("db down"))
    )

    clock.advance(5.0)
    await rv.sweep()
    await rv.drain()

    assert ran == []  # unknown -> fail closed -> dropped
    assert rv.stats.verify_errors == 1
    assert rv.stats.dropped_broken == 1
    assert levels(alarms) == ["error", "critical"]


# --------------------------------------------------------------------------
# 7. Coalescing + idempotency
# --------------------------------------------------------------------------


async def test_duplicate_label_coalesces_to_one_note():
    rv, _clock, _alarms = make_rv()
    ran: list[str] = []
    rv.on_present("K", "1", make_work(ran, "a"), label="dup")
    rv.on_present("K", "1", make_work(ran, "b"), label="dup")
    assert rv.pending_count("K", "1") == 1

    rv.announce("K", "1")
    await rv.drain()
    assert ran == ["a"]  # only the first survived


async def test_coalesce_disabled_keeps_both():
    rv, _clock, _alarms = make_rv()
    ran: list[str] = []
    rv.on_present("K", "1", make_work(ran, "a"), label="dup", coalesce=False)
    rv.on_present("K", "1", make_work(ran, "b"), label="dup", coalesce=False)
    assert rv.pending_count("K", "1") == 2


async def test_empty_label_is_never_coalesced():
    rv, _clock, _alarms = make_rv()
    ran: list[str] = []
    rv.on_present("K", "1", make_work(ran, "a"))
    rv.on_present("K", "1", make_work(ran, "b"))
    assert rv.pending_count("K", "1") == 2


async def test_repeated_announce_does_not_refire_consumed_waiter():
    rv, _clock, _alarms = make_rv()
    ran: list[str] = []
    rv.on_present("K", "1", make_work(ran))
    rv.announce("K", "1")
    rv.announce("K", "1")
    rv.announce("K", "1")
    await rv.drain()
    assert ran == ["w"]  # fired exactly once
    assert rv.stats.fired_on_announce == 1


# --------------------------------------------------------------------------
# 8. Introspection helpers
# --------------------------------------------------------------------------


async def test_is_present_reflects_expiry():
    rv, clock, _alarms = make_rv(present_ttl=5.0)
    assert not rv.is_present("K", "1")
    rv.announce("K", "1")
    assert rv.is_present("K", "1")
    clock.advance(5.0)
    assert not rv.is_present("K", "1")


async def test_pending_count_scopes_by_key():
    rv, _clock, _alarms = make_rv()
    rv.on_present("K", "1", make_work([]), label="a")
    rv.on_present("K", "1", make_work([]), label="b")
    rv.on_present("K", "2", make_work([]), label="c")
    assert rv.pending_count("K", "1") == 2
    assert rv.pending_count("K", "2") == 1
    assert rv.pending_count() == 3


# --------------------------------------------------------------------------
# 8b. Memory safety — presence cache is bounded even with no waiters
# --------------------------------------------------------------------------


async def test_present_cache_is_capped_by_max_present():
    rv, _clock, _alarms = make_rv(present_ttl=1000.0, max_present=3)
    for i in range(10):
        rv.announce("K", str(i))
    # Only the most-recent 3 survive; the oldest were evicted.
    assert sum(rv.is_present("K", str(i)) for i in range(10)) == 3
    assert rv.is_present("K", "9")
    assert not rv.is_present("K", "0")


async def test_announce_front_purges_expired_presence():
    rv, clock, _alarms = make_rv(present_ttl=5.0, max_present=1000)
    rv.announce("K", "old")  # expiry 1005
    clock.advance(6.0)  # 'old' now expired
    rv.announce("K", "new")  # purges 'old' off the front
    assert not rv.is_present("K", "old")
    assert rv.is_present("K", "new")


# --------------------------------------------------------------------------
# 9. Integration — the REAL background sweeper on a tiny TTL
#    (mimics a 5-minute window in ~50 ms, exactly as requested)
# --------------------------------------------------------------------------


async def test_integration_real_sweeper_leak_path():
    alarms: list = []
    rv = Rendezvous(
        default_ttl=0.05,
        present_ttl=0.05,
        sweep_interval=0.01,
        verifier=make_verify(True),  # the row "slipped by"
        alarm=lambda lvl, msg, f: alarms.append(lvl),
    )
    ran: list[str] = []
    rv.on_present("K", "1", make_work(ran))  # boss never announces
    await asyncio.sleep(0.15)  # let the real sweeper wake and resolve
    await rv.drain()
    await rv.aclose()

    assert ran == ["w"]
    assert alarms == ["warning"]


async def test_integration_real_sweeper_announce_beats_expiry():
    alarms: list = []
    rv = Rendezvous(
        default_ttl=1.0,
        present_ttl=1.0,
        sweep_interval=0.01,
        verifier=make_verify(False),
        alarm=lambda lvl, msg, f: alarms.append(lvl),
    )
    ran: list[str] = []
    rv.on_present("K", "1", make_work(ran))
    await asyncio.sleep(0.02)
    rv.announce("K", "1")  # boss arrives well within the window
    await rv.drain()
    await rv.aclose()

    assert ran == ["w"]
    assert alarms == []  # no leak, no broken promise
    assert rv.stats.fired_on_announce == 1


async def test_integration_real_sweeper_broken_promise():
    alarms: list = []
    rv = Rendezvous(
        default_ttl=0.05,
        present_ttl=0.05,
        sweep_interval=0.01,
        verifier=make_verify(False),  # never materialised
        alarm=lambda lvl, msg, f: alarms.append(lvl),
    )
    ran: list[str] = []
    rv.on_present("K", "1", make_work(ran))
    await asyncio.sleep(0.15)
    await rv.drain()
    await rv.aclose()

    assert ran == []
    assert alarms == ["critical"]
