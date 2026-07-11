"""Event-loop lag watchdog — the loud detection backstop for loop blocking.

The asyncio event loop is single-threaded. If ANY coroutine runs a long
synchronous/CPU-bound section directly on the loop (PyMuPDF parsing, a tight
hashing loop, a blocking DB driver call, a blocking SDK generator, ``time.sleep``),
the WHOLE process freezes: no request is served, no DB connection can be
acquired, heartbeats stop. On 2026-06-04 an 82s synchronous PDF
``page_classification`` detector held the loop and the entire production server
went dark for minutes — and nothing detected or reported it. The pool-acquire
timeouts in the logs were a *symptom*; the loop itself was frozen, so even
acquiring an idle connection timed out.

How it works (and why the design matters)
------------------------------------------
The detection MUST run on a **separate OS thread**, never on the loop. A tiny
``_heartbeat`` coroutine on the loop stamps ``_last_beat`` every ``interval``;
a dedicated daemon thread (``_monitor``) reads that stamp and measures how
stale it is. When a blocking section holds the loop, the heartbeat cannot run,
so ``_last_beat`` goes stale by exactly the block duration — that staleness is
direct, quantitative proof the loop is stalled *right now*.

Critically, because the monitor lives on its own thread, it can call
``sys._current_frames()`` for the loop thread **while the loop is still
blocked** and capture the stack of the actual culprit. (A previous version ran
the detector as a loop coroutine; it could only wake *after* the block
released, so every captured stack pointed uselessly back at the watchdog
itself — garbage that taught us nothing. Never put the detector back on the
loop.)

It is a *detector*, not a fixer: the structural fix is to never run blocking
work on the loop (offload to a thread). This watchdog is the alarm that fires
when that discipline is violated anywhere, now or in the future.

Standalone: depends only on stdlib + ``vcprint``. Start it from your app's
startup (e.g. FastAPI ``lifespan``); stop it on shutdown.
"""

from __future__ import annotations

import asyncio
import hashlib
import sys
import threading
import time
import traceback
from collections.abc import Callable
from typing import Any

from matrx_utils.fancy_prints import vcprint


def _default_reporter(message: str) -> None:
    vcprint(message, color="red")


def _stall_signature(name: str, stack_text: str | None) -> str:
    """Stable fingerprint for a stall, derived from its captured stack.

    Lets a consumer deduplicate repeated stalls with the same blocking
    call-site (capturing one durable record per distinct blocker per process
    run) instead of flooding the sink. Uses the file:line of each frame —
    ignoring the source text — so jitter in the rendered line doesn't change
    the fingerprint.
    """
    if not stack_text:
        return f"{name}:no-stack"
    sites = [line.strip() for line in stack_text.split("\n") if line.lstrip().startswith("File ")]
    digest = hashlib.sha1(("\n".join(sites)).encode("utf-8")).hexdigest()[:16]
    return f"{name}:{digest}"


class EventLoopLagWatchdog:
    """Background task that flags event-loop stalls.

    Parameters
    ----------
    interval:
        Seconds between probes. The watchdog sleeps this long, then checks how
        late it woke. Smaller = finer detection at a tiny cost. Default 0.5s.
    warn_threshold:
        Seconds of measured lag above which a stall is reported. Default 1.0s
        — well below anything a human would notice but far above normal jitter.
    capture_stack:
        When True, a stall report includes the captured stack of the loop
        thread sampled *while it is still blocked* — it points straight at the
        blocking call. Sampling happens from the monitor thread, so this is the
        real culprit, not the watchdog's own frames.
    reporter:
        Callable that receives the formatted multi-line report string. Defaults
        to a red ``vcprint`` banner. Inject your own to also route to logging /
        an error sink.
    name:
        Label included in reports — useful when multiple processes log to one
        place.
    """

    def __init__(
        self,
        interval: float = 0.5,
        warn_threshold: float = 1.0,
        capture_stack: bool = True,
        reporter: Callable[[str], None] | None = None,
        on_stall: Callable[[dict[str, Any]], None] | None = None,
        name: str = "event-loop",
    ) -> None:
        self.interval = max(0.05, float(interval))
        self.warn_threshold = max(0.1, float(warn_threshold))
        self.capture_stack = capture_stack
        self._reporter = reporter or _default_reporter
        # Optional structured hook: receives a dict per stall so a host can
        # route it to a durable sink (e.g. record_error → system_error). Kept
        # as an injected callback so this foundation package stays standalone.
        self._on_stall = on_stall
        self.name = name
        # Heartbeat coroutine on the loop; monitor on its own OS thread.
        self._task: asyncio.Task | None = None
        self._monitor_thread: threading.Thread | None = None
        # Loop-thread heartbeat (monotonic seconds). The monitor compares this
        # against the wall clock to measure how long the loop has been frozen.
        self._last_beat = 0.0
        # Threading stop signal — the monitor thread cannot await an asyncio
        # Event, so coordination is via this plain Event plus the heartbeat.
        self._stop = threading.Event()
        # Identify the loop (main) thread so the monitor dumps the right stack.
        self._loop_thread_id = threading.get_ident()
        self._worst_lag_ms = 0.0
        self._stall_count = 0

    @property
    def worst_lag_ms(self) -> float:
        return self._worst_lag_ms

    @property
    def stall_count(self) -> int:
        return self._stall_count

    def start(self) -> asyncio.Task:
        if self._task is not None and not self._task.done():
            return self._task
        self._stop.clear()
        self._loop_thread_id = threading.get_ident()
        self._last_beat = time.monotonic()
        # Heartbeat lives on the loop; monitor lives on its own thread.
        self._task = asyncio.create_task(self._heartbeat(), name=f"loop-lag-watchdog:{self.name}")
        self._monitor_thread = threading.Thread(
            target=self._monitor,
            name=f"loop-lag-watchdog-monitor:{self.name}",
            daemon=True,
        )
        self._monitor_thread.start()
        vcprint(
            f"[Loop Watchdog] Watching '{self.name}' (warn > {self.warn_threshold:.1f}s)",
            color="green",
        )
        return self._task

    async def stop(self) -> None:
        self._stop.set()
        task = self._task
        if task is not None:
            try:
                await asyncio.wait_for(asyncio.shield(task), timeout=self.interval * 4)
            except (TimeoutError, asyncio.CancelledError):
                task.cancel()
            self._task = None
        thread = self._monitor_thread
        if thread is not None:
            # The monitor thread sleeps in short slices and checks _stop, so a
            # generous join is safe; never block shutdown forever on it.
            await asyncio.to_thread(thread.join, self.interval * 4)
            self._monitor_thread = None

    async def _heartbeat(self) -> None:
        """Stamp ``_last_beat`` every ``interval`` while alive.

        This is the ONLY part that runs on the loop. It does no work beyond a
        timestamp write, so it can never itself be the blocker. When the loop
        is frozen by someone else, this coroutine simply can't run, and
        ``_last_beat`` goes stale — which is exactly the signal the monitor
        thread is watching for.
        """
        while not self._stop.is_set():
            self._last_beat = time.monotonic()
            try:
                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                break
        vcprint(f"[Loop Watchdog] Stopped '{self.name}'", color="yellow")

    def _monitor(self) -> None:
        """Detect + sample from a dedicated OS thread (never the loop).

        Tracks a simple two-state machine so each distinct stall is reported
        exactly once, with the real lag duration and the loop-thread stack
        captured *during* the freeze:

        - healthy → if staleness crosses ``warn_threshold``, capture the loop
          stack immediately (the loop is still blocked) and enter the stall.
        - stalled → keep tracking the worst lag; when the heartbeat resumes
          (staleness drops back below threshold) the stall has ended — report
          it with the full measured duration and the captured stack.
        """
        in_stall = False
        stall_lag_ms = 0.0
        stall_stack: str | None = None
        # Poll faster than the heartbeat so detection latency is small and the
        # captured stack lands solidly inside the blocking section.
        poll = min(self.interval, 0.25)
        while not self._stop.wait(poll):
            lag = time.monotonic() - self._last_beat
            if not in_stall:
                if lag > self.warn_threshold:
                    in_stall = True
                    stall_lag_ms = lag * 1000.0
                    # Sample NOW — the loop thread is frozen mid-block, so this
                    # frame is the actual culprit.
                    stall_stack = self._capture_loop_stack() if self.capture_stack else None
            else:
                # Still frozen: track the worst lag seen during this stall.
                stall_lag_ms = max(stall_lag_ms, lag * 1000.0)
                if lag <= self.warn_threshold:
                    # Heartbeat resumed → the loop recovered. Report the stall
                    # once, now that we know its full duration.
                    self._stall_count += 1
                    self._worst_lag_ms = max(self._worst_lag_ms, stall_lag_ms)
                    self._report_stall(stall_lag_ms, stall_stack)
                    in_stall = False
                    stall_stack = None
        # If we are mid-stall at shutdown, still report what we measured.
        if in_stall:
            self._stall_count += 1
            self._worst_lag_ms = max(self._worst_lag_ms, stall_lag_ms)
            self._report_stall(stall_lag_ms, stall_stack)

    def _capture_loop_stack(self) -> str | None:
        frame = sys._current_frames().get(self._loop_thread_id)
        if frame is None:
            return None
        return "".join(traceback.format_stack(frame, limit=40))

    def _report_stall(self, lag_ms: float, stack_text: str | None) -> None:
        lines = [
            "",
            "=" * 80,
            f"Matrx Loop Watchdog  |  EVENT LOOP STALLED ('{self.name}')",
            f"  The asyncio event loop was blocked for ~{lag_ms:.0f}ms.",
            "  While blocked the ENTIRE process is frozen: no requests served,",
            "  no DB connections acquired, no heartbeats. This is a bug — some",
            "  coroutine ran a synchronous/CPU-bound section directly on the loop.",
            "  Fix: offload that work to a thread (asyncio.to_thread /",
            "  run_in_cpu_executor). Do NOT just raise the watchdog threshold.",
            f"  Stall #{self._stall_count} this process; worst so far {self._worst_lag_ms:.0f}ms.",
        ]
        if stack_text:
            lines.append("-" * 80)
            lines.append("  Loop-thread stack captured DURING the freeze (the culprit):")
            for entry in stack_text.rstrip("\n").split("\n"):
                lines.append("    " + entry)
        elif self.capture_stack:
            lines.append("-" * 80)
            lines.append("  (loop-thread stack unavailable — loop recovered before sampling)")
        lines.append("=" * 80)
        lines.append("")
        report = "\n".join(lines)
        try:
            self._reporter(report)
        except Exception:
            # The watchdog must never take down the process it guards.
            pass
        if self._on_stall is not None:
            try:
                self._on_stall(
                    {
                        "name": self.name,
                        "lag_ms": lag_ms,
                        "stall_count": self._stall_count,
                        "worst_lag_ms": self._worst_lag_ms,
                        "warn_threshold_ms": self.warn_threshold * 1000.0,
                        "stack": stack_text,
                        "signature": _stall_signature(self.name, stack_text),
                        "report": report,
                    }
                )
            except Exception:
                # Structured capture is best-effort, same contract as the
                # console reporter: never take down the guarded process.
                pass


def start_loop_lag_watchdog(
    interval: float = 0.5,
    warn_threshold: float = 1.0,
    capture_stack: bool = True,
    reporter: Callable[[str], None] | None = None,
    on_stall: Callable[[dict[str, Any]], None] | None = None,
    name: str = "event-loop",
) -> EventLoopLagWatchdog:
    """Create and start an :class:`EventLoopLagWatchdog` on the running loop.

    Must be called from within a running event loop (e.g. a FastAPI
    ``lifespan`` handler). Returns the watchdog so the caller can ``await
    watchdog.stop()`` on shutdown and read ``worst_lag_ms`` / ``stall_count``.

    ``on_stall`` is an optional structured hook invoked once per stall with a
    dict (name, lag_ms, stack, signature, …) so a host can persist each stall
    to a durable, reviewable sink. Best-effort and never-raising.
    """
    watchdog = EventLoopLagWatchdog(
        interval=interval,
        warn_threshold=warn_threshold,
        capture_stack=capture_stack,
        reporter=reporter,
        on_stall=on_stall,
        name=name,
    )
    watchdog.start()
    return watchdog


__all__ = [
    "EventLoopLagWatchdog",
    "start_loop_lag_watchdog",
]
