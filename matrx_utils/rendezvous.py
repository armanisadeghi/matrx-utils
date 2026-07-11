"""Rendezvous — an order-independent meeting point between a producer that
makes a keyed resource real and a consumer that must act once it is real.

The problem it kills: a producer (e.g. a queued DB INSERT that commits at the
end of a request) and a consumer (e.g. a labeler that UPDATEs that row) race.
If the consumer wins, a naive "does it exist yet?" poll is fooled by
pending/uncommitted state and the write hits zero rows. Rendezvous removes the
race by caching arrival in BOTH directions:

  * Producer calls ``announce(kind, id)`` the instant the resource is COMMITTED.
    That arrival is cached for ``present_ttl`` seconds.
  * Consumer calls ``on_present(kind, id, do=...)`` at any time. If the producer
    already announced (cache hit) the work runs immediately. Otherwise the note
    is held for ``ttl`` seconds and fires the moment the producer announces.

The consumer's note has a dying act. If ``ttl`` elapses with no announcement,
the note asks a caller-supplied ``verify(kind, id)`` — a COMMITTED read of the
real store — whether the resource slipped past unannounced:

  * verify TRUE  → the producer forgot to announce (a leak in the commit hook).
                   Run the work anyway, but SCREAM a warning so the leak is found.
  * verify FALSE → the promised resource never materialised. Drop the work and
                   SCREAM a critical alarm (+ whatever the injected alarm sink
                   escalates to, e.g. a durable error row).

Everything is injectable — ``now``/``sleep`` for deterministic tests, ``spawn``
to capture fired work, ``alarm`` to route screams, ``verifier`` for a default
DB check — so the primitive is exhaustively testable without wall-clock waits.
"""

from __future__ import annotations

import asyncio
import time
from collections import OrderedDict
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from matrx_utils import vcprint

# A unit of work to run once the resource is present. A zero-arg factory that
# returns an awaitable — a factory (not a bare coroutine) so it can be created
# lazily at fire time and never "already awaited".
DoWork = Callable[[], Awaitable[Any]]
# COMMITTED existence check against the real store. (kind, id) -> is it there?
Verify = Callable[[str, str], Awaitable[bool]]
# level in {"warning", "critical", "error"}; message + structured fields.
Alarm = Callable[[str, str, dict[str, Any]], None]

_LEVEL_COLOR = {"warning": "yellow", "critical": "red", "error": "red"}


def _default_alarm(level: str, message: str, fields: dict[str, Any]) -> None:
    vcprint(message, color=_LEVEL_COLOR.get(level, "yellow"))


@dataclass
class _Waiter:
    do: DoWork
    verify: Verify | None
    deadline: float
    label: str


@dataclass
class RendezvousStats:
    fired_on_hit: int = 0
    fired_on_announce: int = 0
    fired_on_leak: int = 0
    dropped_broken: int = 0
    work_errors: int = 0
    verify_errors: int = 0


class Rendezvous:
    def __init__(
        self,
        *,
        now: Callable[[], float] = time.monotonic,
        default_ttl: float = 300.0,
        present_ttl: float = 300.0,
        sweep_interval: float = 1.0,
        alarm: Alarm = _default_alarm,
        verifier: Verify | None = None,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
        spawn: Callable[[Awaitable[Any]], Any] | None = None,
        autostart_sweeper: bool = True,
        max_present: int = 50_000,
    ) -> None:
        self._now = now
        self._default_ttl = default_ttl
        self._present_ttl = present_ttl
        self._sweep_interval = sweep_interval
        self._alarm = alarm
        self._verifier = verifier
        self._sleep = sleep
        self._spawn_override = spawn
        self._autostart = autostart_sweeper
        self._max_present = max_present

        # key = (kind, id). OrderedDict + constant present_ttl ⇒ insertion order
        # is expiry order, so the front is always the soonest-to-expire. That
        # lets announce() front-purge in O(expired) and bound memory when the
        # producer fires for rows nobody is waiting on (the common case).
        self._present: OrderedDict[tuple[str, str], float] = OrderedDict()  # key -> expiry ts
        self._waiters: dict[tuple[str, str], list[_Waiter]] = {}
        self._inflight: set[Any] = set()
        self._sweeper_task: Any = None
        self.stats = RendezvousStats()

    def configure(self, *, alarm: Alarm | None = None, verifier: Verify | None = None) -> None:
        """Host override for the sinks — e.g. escalate the critical broken-promise
        alarm to a durable error row, or supply a default committed-read verifier.
        Wired once at startup (aidream ``package_integration.py``)."""
        if alarm is not None:
            self._alarm = alarm
        if verifier is not None:
            self._verifier = verifier

    # -- producer door ------------------------------------------------------

    def announce(self, kind: str, id: str) -> None:
        """The resource is COMMITTED and real. Cache the arrival and fire any
        notes waiting on it. Idempotent — a second announce just refreshes the
        presence window; already-fired notes are gone and never re-fire."""
        key = (kind, id)
        now = self._now()
        self._present[key] = now + self._present_ttl
        self._present.move_to_end(key)
        # Front-purge expired entries (front == soonest to expire), then bound.
        while self._present:
            oldest_key = next(iter(self._present))
            if self._present[oldest_key] <= now:
                self._present.popitem(last=False)
            else:
                break
        while len(self._present) > self._max_present:
            self._present.popitem(last=False)

        waiters = self._waiters.pop(key, None)
        if waiters:
            for w in waiters:
                self.stats.fired_on_announce += 1
                self._spawn(self._run(w.do, w.label, kind, id))

    # -- consumer door ------------------------------------------------------

    def on_present(
        self,
        kind: str,
        id: str,
        do: DoWork,
        *,
        verify: Verify | None = None,
        ttl: float | None = None,
        label: str = "",
        coalesce: bool = True,
    ) -> None:
        """Run ``do`` once (kind, id) is committed-present. Fires immediately on
        a cache hit; otherwise holds the note for ``ttl`` seconds. Never blocks
        the caller and never raises out of ``do`` — failures route to ``alarm``."""
        key = (kind, id)
        now = self._now()
        expiry = self._present.get(key)
        if expiry is not None and expiry > now:
            self.stats.fired_on_hit += 1
            self._spawn(self._run(do, label, kind, id))
            return
        if expiry is not None:  # stale presence — drop it, fall through to wait
            self._present.pop(key, None)

        waiters = self._waiters.setdefault(key, [])
        if coalesce and label and any(w.label == label for w in waiters):
            return  # duplicate note for the same key+label — collapse it
        deadline = now + (ttl if ttl is not None else self._default_ttl)
        waiters.append(_Waiter(do=do, verify=verify, deadline=deadline, label=label))
        self._ensure_sweeper()

    # -- internals ----------------------------------------------------------

    def _spawn(self, coro: Awaitable[Any]) -> Any:
        if self._spawn_override is not None:
            return self._spawn_override(coro)
        task = asyncio.ensure_future(coro)
        self._inflight.add(task)
        task.add_done_callback(self._inflight.discard)
        return task

    async def _run(self, do: DoWork, label: str, kind: str, id: str) -> None:
        try:
            await do()
        except Exception as exc:  # never let a note's failure vanish
            self.stats.work_errors += 1
            self._alarm(
                "error",
                f"[Rendezvous] work {label!r} for {kind}:{id} raised: {exc!r}",
                {"kind": kind, "id": id, "label": label, "error": repr(exc)},
            )

    def _ensure_sweeper(self) -> None:
        if not self._autostart:
            return
        if self._sweeper_task is None or self._sweeper_task.done():
            self._sweeper_task = asyncio.ensure_future(self._sweeper_loop())

    async def _sweeper_loop(self) -> None:
        while self._waiters:
            await self._sleep(self._sweep_interval)
            await self.sweep()

    async def sweep(self, now: float | None = None) -> None:
        """Expire stale presence entries and resolve overdue waiters. Driven by
        the background loop in production; called directly (with a fake clock)
        in tests."""
        now = self._now() if now is None else now

        for key in [k for k, exp in self._present.items() if exp <= now]:
            self._present.pop(key, None)

        for key in list(self._waiters.keys()):
            still_waiting: list[_Waiter] = []
            for w in self._waiters[key]:
                if w.deadline <= now:
                    self._spawn(self._resolve_expired(w, key))
                else:
                    still_waiting.append(w)
            if still_waiting:
                self._waiters[key] = still_waiting
            else:
                self._waiters.pop(key, None)

    async def _resolve_expired(self, w: _Waiter, key: tuple[str, str]) -> None:
        kind, id = key
        verify = w.verify or self._verifier
        present_in_db = False
        if verify is not None:
            try:
                present_in_db = bool(await verify(kind, id))
            except Exception as exc:
                self.stats.verify_errors += 1
                self._alarm(
                    "error",
                    f"[Rendezvous] verify for {kind}:{id} raised — treating as "
                    f"NOT present: {exc!r}",
                    {"kind": kind, "id": id, "label": w.label, "error": repr(exc)},
                )
                present_in_db = False

        if present_in_db:
            self.stats.fired_on_leak += 1
            self._alarm(
                "warning",
                f"[Rendezvous] LEAK — {kind}:{id} was committed but NEVER "
                f"announced. Someone slipped past the commit hook. Running "
                f"{w.label!r} from the DB fallback; fix the producer's announce.",
                {"kind": kind, "id": id, "label": w.label},
            )
            await self._run(w.do, w.label, kind, id)
        else:
            self.stats.dropped_broken += 1
            self._alarm(
                "critical",
                f"[Rendezvous] BROKEN PROMISE — {kind}:{id} never materialised "
                f"within its window. Dropping {w.label!r}. A producer promised a "
                f"resource that never committed.",
                {"kind": kind, "id": id, "label": w.label},
            )

    # -- lifecycle / test helpers ------------------------------------------

    def is_present(self, kind: str, id: str) -> bool:
        expiry = self._present.get((kind, id))
        return expiry is not None and expiry > self._now()

    def pending_count(self, kind: str | None = None, id: str | None = None) -> int:
        if kind is not None and id is not None:
            return len(self._waiters.get((kind, id), ()))
        return sum(len(v) for v in self._waiters.values())

    async def drain(self) -> None:
        """Await all fired work (and any resolution tasks it spawned). Used by
        tests and graceful shutdown so nothing is left in-flight."""
        while self._inflight:
            await asyncio.gather(*list(self._inflight), return_exceptions=True)

    async def aclose(self) -> None:
        if self._sweeper_task is not None and not self._sweeper_task.done():
            self._sweeper_task.cancel()
            try:
                await self._sweeper_task
            except (asyncio.CancelledError, Exception):
                pass
        await self.drain()


# Process-global default instance. Hosts reconfigure the sinks (alarm, verifier)
# by constructing their own and assigning, or by injecting at call sites.
rendezvous = Rendezvous()
