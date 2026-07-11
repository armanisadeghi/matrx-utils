"""In-flight request registry — request correlation for thread-based probes.

The event-loop watchdog (``loop_watchdog.py``) samples the loop-thread stack
from a *separate OS thread* while the loop is frozen. That stack tells us
*what code* stalled, but it has no access to the loop's ``ContextVar`` state,
so it can never tell us *which request / user / route* was running when the
freeze happened (the 2026-06-12 ``event_loop_stall`` row landed with
``request_id``/``user_id``/``route`` all NULL — the stack alone happened to
name the culprit, but a stall buried in a generic helper would not).

This registry closes that gap. The request layer registers a lightweight
marker (method, path, request_id, user_id, start time) for every in-flight
request and unregisters it when the request ends. Any off-loop probe — the
watchdog monitor thread, a future stuck-request sweeper — can read a
thread-safe :meth:`snapshot` to learn which requests were live (and for how
long) at the moment of an anomaly.

Standalone: stdlib only. The request layer (matrx-connect ``AuthMiddleware``)
populates it; the watchdog host reads it. Both go through
:func:`get_inflight_registry`, so there is exactly one registry per process.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from itertools import count
from typing import Any


@dataclass
class RequestMarker:
    token: int
    method: str | None
    path: str | None
    request_id: str | None
    user_id: str | None
    started_monotonic: float
    started_wall: float


class InflightRequestRegistry:
    """Thread-safe registry of currently-executing requests.

    Cheap by design: a dict guarded by a plain lock plus a monotonic counter
    for tokens. ``register`` / ``unregister`` are O(1) and allocation-light so
    they can sit on the hot path of every request.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._markers: dict[int, RequestMarker] = {}
        self._counter = count(1)

    def register(
        self,
        *,
        method: str | None = None,
        path: str | None = None,
        request_id: str | None = None,
        user_id: str | None = None,
    ) -> int:
        token = next(self._counter)
        now_mono = time.monotonic()
        now_wall = time.time()
        with self._lock:
            self._markers[token] = RequestMarker(
                token=token,
                method=method,
                path=path,
                request_id=request_id,
                user_id=user_id,
                started_monotonic=now_mono,
                started_wall=now_wall,
            )
        return token

    def update(self, token: int, **fields: Any) -> None:
        """Backfill marker fields discovered after registration (e.g. user_id
        resolved later in the request). Only non-None values overwrite."""
        with self._lock:
            marker = self._markers.get(token)
            if marker is None:
                return
            for key, value in fields.items():
                if value is not None and hasattr(marker, key):
                    setattr(marker, key, value)

    def unregister(self, token: int) -> None:
        with self._lock:
            self._markers.pop(token, None)

    def snapshot(self, limit: int = 10) -> list[dict[str, Any]]:
        """The current in-flight requests, longest-running first.

        ``running_ms`` is wall-relative to *now*, so when called from a probe
        during a stall it shows which requests have been alive across the
        freeze — the longest-running one is the prime suspect.
        """
        now_mono = time.monotonic()
        with self._lock:
            markers = list(self._markers.values())
        markers.sort(key=lambda m: m.started_monotonic)
        out: list[dict[str, Any]] = []
        for marker in markers[:limit]:
            out.append(
                {
                    "method": marker.method,
                    "path": marker.path,
                    "request_id": marker.request_id,
                    "user_id": marker.user_id,
                    "running_ms": round((now_mono - marker.started_monotonic) * 1000.0, 1),
                }
            )
        return out

    def count(self) -> int:
        with self._lock:
            return len(self._markers)


_GLOBAL_REGISTRY = InflightRequestRegistry()


def get_inflight_registry() -> InflightRequestRegistry:
    """The single process-wide in-flight request registry."""
    return _GLOBAL_REGISTRY


__all__ = [
    "InflightRequestRegistry",
    "RequestMarker",
    "get_inflight_registry",
]
