"""Runtime diagnostics primitives for Matrx services.

Currently exposes the event-loop lag watchdog — a loud, always-on backstop
that detects when something blocks the asyncio event loop (the failure mode
that took the production server down on 2026-06-04 when an 82s synchronous
PDF detector ran on the loop).
"""

from __future__ import annotations

from .inflight import (
    InflightRequestRegistry,
    RequestMarker,
    get_inflight_registry,
)
from .loop_watchdog import (
    EventLoopLagWatchdog,
    start_loop_lag_watchdog,
)

__all__ = [
    "EventLoopLagWatchdog",
    "start_loop_lag_watchdog",
    "InflightRequestRegistry",
    "RequestMarker",
    "get_inflight_registry",
]
