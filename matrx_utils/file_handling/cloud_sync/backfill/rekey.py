"""Backfill canonical_storage_uri on cld_files.

Walks every cld_files row whose canonical_storage_uri is NULL, performs
a server-side S3 copy from the legacy <owner>/<file_path> key to the
canonical <owner>/<file_id> key, then updates the row.

The script is **idempotent + resumable**:
  * Skips rows that already have canonical_storage_uri set.
  * Skips rows whose legacy storage object is missing (logs + flagged
    in metadata so the operator can investigate).
  * Skips rows that already exist at the canonical key (the copy is
    a no-op, the UPDATE wires the URI).
  * Bounded concurrency so we don't saturate S3 or the Postgres pool.

Portable: pass a configured ``FileManager`` in. Hosts write a tiny CLI
that bootstraps their wiring then calls ``run_rekey_backfill(fm, ...)``.

The script does NOT delete the legacy S3 objects. That happens in a
later migration once we are confident the canonical keys are correct
across the fleet (think: bake time of at least 7 days). Until then
both keys exist; reads prefer canonical and fall back to legacy.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

from matrx_utils import vcprint

from ..db import T_FILES, afiles_table

# Tunables.
_BATCH_SIZE = 200
_PARALLELISM = 8


async def _next_batch(client: Any, *, owner_filter: str | None, batch_size: int) -> list[dict]:
    """Fetch the next batch of rows that still need re-keying.

    We use ``OFFSET 0`` because each iteration's query naturally returns
    different rows (the previous iteration UPDATEd them, removing them
    from the predicate). No cursor needed.
    """
    q = (
        afiles_table(client, T_FILES)
        .select("id,created_by,storage_uri,file_path")
        .is_("canonical_storage_uri", "null")
        .is_("deleted_at", "null")
        .order("created_at", desc=False)
        .limit(batch_size)
    )
    if owner_filter:
        q = q.eq("created_by", owner_filter)
    resp = await q.execute()
    return list(resp.data or [])


def _canonical_key(owner_id: str, file_id: str) -> str:
    """The canonical S3 key inside the bucket. <owner>/<file_id>."""
    return f"{owner_id}/{file_id}"


def _split_uri(uri: str) -> tuple[str, str, str] | None:
    """Split <backend>://<bucket>/<key> into (backend, bucket, key)."""
    if "://" not in uri:
        return None
    backend, rest = uri.split("://", 1)
    if "/" not in rest:
        return None
    bucket, key = rest.split("/", 1)
    return backend, bucket, key


async def _process_row(
    fm: Any,
    client: Any,
    row: dict[str, Any],
    *,
    sem: asyncio.Semaphore,
    stats: dict[str, int],
) -> None:
    async with sem:
        file_id = row["id"]
        owner_id = row.get("owner_id") or row["created_by"]
        legacy_uri = row.get("storage_uri") or ""
        split = _split_uri(legacy_uri)
        if split is None or not legacy_uri.startswith("s3://"):
            # Not an S3-backed row (typical: leftover /tmp test paths).
            # Stamp a sentinel so the row drops out of the IS NULL filter
            # and the loop doesn't churn on it forever.
            sentinel = f"unrecoverable://{file_id}"
            try:
                await (
                    afiles_table(client, T_FILES)
                    .update({"canonical_storage_uri": sentinel})
                    .eq("id", file_id)
                    .execute()
                )
            except Exception:
                pass
            await _flag_missing(client, file_id, f"non-s3 storage_uri: {legacy_uri[:100]!r}")
            stats["skipped_bad_uri"] += 1
            return
        backend, bucket, legacy_key = split
        canonical_key = _canonical_key(owner_id, file_id)
        canonical_uri = f"{backend}://{bucket}/{canonical_key}"

        # Special case: the legacy key already IS the canonical key.
        if legacy_key == canonical_key:
            await _update_row(client, file_id, canonical_uri)
            stats["already_canonical"] += 1
            return

        if not fm.sync_engine._router.is_configured("s3"):
            stats["skipped_no_backend"] += 1
            return
        s3 = fm.sync_engine._router.s3
        s3_client = s3._get_client()

        # Verify the legacy object exists.
        try:
            await asyncio.to_thread(s3_client.head_object, Bucket=bucket, Key=legacy_key)
        except Exception as e:
            vcprint(
                f"[rekey] legacy missing file_id={file_id} key={legacy_key} err={e!r}",
                color="yellow",
            )
            await _flag_missing(client, file_id, str(e))
            stats["legacy_missing"] += 1
            return

        # Server-side copy. Idempotent — copying onto an existing object
        # in the same bucket is allowed.
        try:
            await asyncio.to_thread(
                s3_client.copy_object,
                Bucket=bucket,
                Key=canonical_key,
                CopySource={"Bucket": bucket, "Key": legacy_key},
                MetadataDirective="COPY",
            )
        except Exception as e:
            vcprint(f"[rekey] copy failed file_id={file_id} err={e!r}", color="yellow")
            stats["copy_failed"] += 1
            return

        await _update_row(client, file_id, canonical_uri)
        stats["copied"] += 1


async def _update_row(client: Any, file_id: str, canonical_uri: str) -> None:
    await (
        afiles_table(client, T_FILES)
        .update({"canonical_storage_uri": canonical_uri})
        .eq("id", file_id)
        .execute()
    )


async def _flag_missing(client: Any, file_id: str, error: str) -> None:
    """Stamp metadata so the operator can find rows whose legacy key 404s."""
    try:
        existing = (
            await afiles_table(client, T_FILES)
            .select("metadata")
            .eq("id", file_id)
            .maybe_single()
            .execute()
        )
        meta = (existing.data or {}).get("metadata") or {}
        meta["_rekey_legacy_missing"] = {"error": error[:500]}
        await afiles_table(client, T_FILES).update({"metadata": meta}).eq("id", file_id).execute()
    except Exception:
        pass


async def rekey_one_file(fm: Any, file_id: str) -> bool:
    """Rekey a single cld_files row right after upload.

    Designed for fire-and-forget from the upload handlers:

        asyncio.create_task(rekey_one_file(fm, result.file_id))

    Returns True when the row was rekeyed (or already canonical),
    False on any non-fatal failure. Never raises.
    """
    try:
        if fm is None or fm.sync_engine is None:
            return False
        client = await fm.sync_engine.db._get_async_client()
        resp = (
            await afiles_table(client, T_FILES)
            .select("id,created_by,storage_uri,file_path,canonical_storage_uri")
            .eq("id", file_id)
            .maybe_single()
            .execute()
        )
        row = resp.data
        if not row or row.get("canonical_storage_uri"):
            return True
        sem = asyncio.Semaphore(1)
        stats = {
            "copied": 0,
            "already_canonical": 0,
            "legacy_missing": 0,
            "copy_failed": 0,
            "skipped_bad_uri": 0,
            "skipped_no_backend": 0,
        }
        await _process_row(fm, client, row, sem=sem, stats=stats)
        return stats["copied"] > 0 or stats["already_canonical"] > 0
    except Exception:
        return False


async def run_rekey_backfill(
    fm: Any,
    *,
    owner_filter: str | None = None,
    limit: int | None = None,
) -> dict[str, int]:
    """Walk every row needing rekey, copy bytes, update URIs.

    Pass a configured FileManager (with cloud_sync set up). The CLI
    wrapper a host ships should bootstrap settings + context then
    call this function.
    """
    if fm is None or fm.sync_engine is None:
        raise RuntimeError("cloud sync not configured — pass a FileManager with sync_engine set")
    client = await fm.sync_engine.db._get_async_client()

    sem = asyncio.Semaphore(_PARALLELISM)
    stats: dict[str, int] = {
        "copied": 0,
        "already_canonical": 0,
        "legacy_missing": 0,
        "copy_failed": 0,
        "skipped_bad_uri": 0,
        "skipped_no_backend": 0,
    }
    seen = 0
    started = time.monotonic()

    while True:
        batch_target = min(_BATCH_SIZE, (limit - seen)) if limit else _BATCH_SIZE
        if batch_target <= 0:
            break
        rows = await _next_batch(client, owner_filter=owner_filter, batch_size=batch_target)
        if not rows:
            break
        await asyncio.gather(
            *(_process_row(fm, client, row, sem=sem, stats=stats) for row in rows),
            return_exceptions=True,
        )
        seen += len(rows)
        elapsed = time.monotonic() - started
        rate = seen / elapsed if elapsed > 0 else 0
        vcprint(
            f"[rekey] processed={seen:,} copied={stats['copied']:,} "
            f"already={stats['already_canonical']:,} missing={stats['legacy_missing']:,} "
            f"failed={stats['copy_failed']:,} ({rate:.1f}/s)",
            color="cyan",
        )
        if limit and seen >= limit:
            break

    return stats


__all__ = ["rekey_one_file", "run_rekey_backfill"]
