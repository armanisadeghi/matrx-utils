"""Executor pools for CPU-bound and OCR PDF work.

PyMuPDF is sync C code and the upstream FAQ explicitly states multi-threaded
use is unsupported (GIL release is "intolerable overhead"). Our discipline:

- Every public ``_async`` method opens its own ``Document`` from bytes inside
  the executor thread. Never share a Document across coroutines or threads.
- General CPU work goes through ``get_cpu_executor`` / ``run_in_cpu_executor``.
- OCR work goes through ``get_ocr_executor`` / ``run_in_ocr_executor`` so
  Tesseract concurrency can be sized independently (it is CPU-saturating
  per-process).

Both pools are lazily initialized on first use and shut down via
``shutdown_executors`` (registered with atexit). Sizing is configurable via
``MATRX_PDF_CPU_WORKERS`` and ``MATRX_PDF_OCR_WORKERS`` env vars.
"""

from __future__ import annotations

import asyncio
import atexit
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, TypeVar

T = TypeVar("T")

# OCR pool size is capped here. PyMuPDF's Tesseract bindings release the GIL,
# so a thread pool is sufficient; we keep the cap conservative because each
# worker can independently saturate a CPU core via Tesseract. Override via
# the ``MATRX_PDF_OCR_WORKERS`` env var.
_DEFAULT_OCR_MAX = 4

_cpu_executor: ThreadPoolExecutor | None = None
_ocr_executor: ThreadPoolExecutor | None = None
_init_lock = threading.Lock()


def _cpu_worker_count() -> int:
    raw = os.environ.get("MATRX_PDF_CPU_WORKERS")
    if raw:
        try:
            return max(1, int(raw))
        except ValueError:
            pass
    return max(1, os.cpu_count() or 2)


def _ocr_worker_count() -> int:
    raw = os.environ.get("MATRX_PDF_OCR_WORKERS")
    if raw:
        try:
            return max(1, int(raw))
        except ValueError:
            pass
    return max(1, min(_DEFAULT_OCR_MAX, os.cpu_count() or 2))


def get_cpu_executor() -> ThreadPoolExecutor:
    global _cpu_executor
    if _cpu_executor is None:
        with _init_lock:
            if _cpu_executor is None:
                _cpu_executor = ThreadPoolExecutor(
                    max_workers=_cpu_worker_count(),
                    thread_name_prefix="matrx-pdf-cpu",
                )
    return _cpu_executor


def get_ocr_executor() -> ThreadPoolExecutor:
    global _ocr_executor
    if _ocr_executor is None:
        with _init_lock:
            if _ocr_executor is None:
                _ocr_executor = ThreadPoolExecutor(
                    max_workers=_ocr_worker_count(),
                    thread_name_prefix="matrx-pdf-ocr",
                )
    return _ocr_executor


async def run_in_cpu_executor(fn: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    loop = asyncio.get_running_loop()
    if kwargs:
        return await loop.run_in_executor(
            get_cpu_executor(), lambda: fn(*args, **kwargs)
        )
    return await loop.run_in_executor(get_cpu_executor(), fn, *args)


async def run_in_ocr_executor(fn: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    loop = asyncio.get_running_loop()
    if kwargs:
        return await loop.run_in_executor(
            get_ocr_executor(), lambda: fn(*args, **kwargs)
        )
    return await loop.run_in_executor(get_ocr_executor(), fn, *args)


def shutdown_executors() -> None:
    global _cpu_executor, _ocr_executor
    with _init_lock:
        if _cpu_executor is not None:
            _cpu_executor.shutdown(wait=False)
            _cpu_executor = None
        if _ocr_executor is not None:
            _ocr_executor.shutdown(wait=False)
            _ocr_executor = None


atexit.register(shutdown_executors)


__all__ = [
    "get_cpu_executor",
    "get_ocr_executor",
    "run_in_cpu_executor",
    "run_in_ocr_executor",
    "shutdown_executors",
]
