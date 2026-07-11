"""Thumbnail-URL resolver — single source of truth for "give me a thumbnail
URL for this cld_files row".

Phase 1b — replaces the legacy ``cld_files.thumbnail_storage_uri`` /
``cld_files.thumbnail_url`` columns. Thumbnails now live as variant
cld_files rows linked back to the master via ``metadata.derived_from``.
The Phase 1 variants pipeline writes them; this module reads them.

Public API:

    # Single-record: when you have one cld_files row and want a thumbnail URL
    url = await resolve_thumbnail_url_async(fm, record, signed_ttl=3600)

    # List-record: when you have N records and want N thumbnail URLs
    # (issues N concurrent queries via asyncio.gather; the
    # idx_cld_files_derived_from B-tree index keeps each lookup O(log n))
    url_by_id = await resolve_thumbnail_urls_async(fm, records, signed_ttl=3600)

Both helpers return None when no thumbnail variant exists yet — caller
falls back to a client-side icon or triggers a thumbnail render.
"""

from __future__ import annotations

import asyncio
from typing import Any

# Variant key the SOCIAL_BASELINE pipeline writes for the 400×400 thumbnail.
# Centralized here so any future rename is a one-line change.
THUMBNAIL_VARIANT_KEY = "thumbnail_url"


async def resolve_thumbnail_url_async(
    fm: Any,
    record: dict,
    *,
    signed_ttl: int = 3600,
    variant_key: str = THUMBNAIL_VARIANT_KEY,
) -> str | None:
    """Return a usable URL for the row's thumbnail variant, or None.

    Looks up ``metadata.derived_from = record["id"]`` AND
    ``metadata.variant_key = variant_key`` in cld_files (one DB hit via
    the migration-009 expression index), then mints a fresh URL via
    SyncEngine.build_urls_for_record_async so private files get a valid
    signed URL and public files get the CDN URL.

    No fallback to the legacy ``record["thumbnail_url"]`` /
    ``record["thumbnail_storage_uri"]`` columns — those are dropped in
    migration 011 and reading them would raise once the schema
    catches up. Callers that need a transition fallback should compute
    it explicitly.

    Returns None when the variant hasn't been rendered yet (file
    uploaded before Phase 1, or thumbnail render failed).
    """
    if not record or not record.get("id"):
        return None
    se = fm.sync_engine
    catalog = await se.variants.list_existing_async(record)
    variant = catalog.get(variant_key)
    if not variant:
        return None
    urls = await se.build_urls_for_record_async(variant, signed_ttl=signed_ttl)
    return urls.get("url")


async def resolve_thumbnail_urls_async(
    fm: Any,
    records: list[dict],
    *,
    signed_ttl: int = 3600,
    variant_key: str = THUMBNAIL_VARIANT_KEY,
) -> dict[str, str | None]:
    """Bulk variant of ``resolve_thumbnail_url_async`` for list endpoints.

    Returns ``{file_id: thumbnail_url_or_none}`` for every input record.
    Issues N parallel queries via asyncio.gather — the migration-009
    expression index ``idx_cld_files_derived_from`` keeps each lookup
    O(log n), and Supabase's HTTP connection pool absorbs the parallel
    load comfortably for typical page sizes (≤200).

    A genuine bulk-SQL implementation (single query with WHERE IN) is
    a future optimisation; the parallel-gather pattern keeps this
    helper dependency-free + portable across the sync_engine's DB
    backends.
    """
    if not records:
        return {}
    file_ids = [r["id"] for r in records if r and r.get("id")]
    if not file_ids:
        return {}
    coros = [
        resolve_thumbnail_url_async(
            fm, r, signed_ttl=signed_ttl, variant_key=variant_key,
        )
        for r in records
    ]
    results = await asyncio.gather(*coros, return_exceptions=True)
    out: dict[str, str | None] = {}
    for r, url in zip(records, results, strict=False):
        if not r or not r.get("id"):
            continue
        if isinstance(url, Exception):
            # Per-record failure is non-fatal — leave None and let the
            # FE fall back to its client-side icon.
            out[r["id"]] = None
        else:
            out[r["id"]] = url
    return out


__all__ = [
    "THUMBNAIL_VARIANT_KEY",
    "resolve_thumbnail_url_async",
    "resolve_thumbnail_urls_async",
]
