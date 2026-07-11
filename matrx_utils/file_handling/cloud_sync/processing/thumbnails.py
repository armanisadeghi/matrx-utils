"""Universal post-upload media processing for cld_files — Phase 1d backfill.

Designed for two call sites:

  1. **Fire-and-forget after upload** (TUS finalize, legacy /files/upload,
     anywhere a file lands in cld_files without going through POST /assets):

        asyncio.create_task(generate_thumbnail_for_file(fm, file_id))

  2. **Backfill** — apply the full Phase 1 / 1c / 1d.1 treatment to every
     existing cld_files row that pre-dates these phases. Idempotent, so
     safe to re-run repeatedly:

        await ensure_media_processing(fm, file_id)

Both call sites do the same work:

  - **Phase 1**: render the SOCIAL_BASELINE variants (og_url /
    thumbnail_url / tiny_url) from a universally-rasterised source
    (image passthrough, PDF page 1, video frame, audio waveform,
    mime-icon fallback for everything else).
  - **Phase 1c**: render the kind-specific full-res variants (page1_url
    for PDFs, poster_url for videos) so DocumentBlock / VideoBlock
    carry a browser-renderable primary representation.
  - **Phase 1d.1**: probe width / height / duration_ms / page_count
    from the source bytes and persist to the cld_files columns
    (page_count lands in metadata.page_count since there's no column).

Idempotency comes from VariantsService — variant keys that already
exist for the (master, key) pair are skipped. Probe failures + variant
render failures are non-fatal so a bad file never blocks the upload
pipeline OR the backfill loop.
"""

from __future__ import annotations

import time
from typing import Any

from matrx_utils import vcprint


async def generate_thumbnail_for_file(
    fm: Any,
    file_id: str,
    *,
    record: dict[str, Any] | None = None,
    allow_lineage: bool = False,
) -> bool:
    """Render variants + probe metadata for a cld_files row.

    Returns True when any variant landed (new or already present), False
    on early-skip or any non-fatal failure. Never raises — must not
    bring down the upload pipeline.

    Idempotent across both variants (VariantsService key-deduplication)
    and column updates (overwrites with the probed values, which are
    deterministic for a given byte sequence).

    ``allow_lineage=True`` bypasses ONLY the parent_file_id guard — for
    masters that legitimately carry lineage (a scanned PDF's parent is
    its first source photo). The variant-row guard (derived_from /
    variant_key) always applies; the cascade incident cannot recur via
    this flag because variant rows are identified by metadata, not by
    parentage.
    """
    started = time.monotonic()
    db = fm.sync_engine.db
    try:
        if record is None:
            record = await db.get_file_async(file_id)
        if not record:
            return False

        mime = record.get("mime_type") or ""
        if not mime:
            return False

        # Phase 1d.3 defense-in-depth — refuse to process a row that is
        # itself a variant. This is the bug-fix for the cascade incident
        # where the backfill iterated every cld_files row matching the
        # mime filter (including variant rows) and re-processed each one
        # as if it were a master, creating "variants of variants" up to
        # 12 levels deep. The query-side filter in the backfill script
        # (filtered_query in cloud_sync/backfill/thumbnails.py) is the
        # primary defense; this is the second layer so no future caller
        # can accidentally re-trigger the cascade.
        meta = record.get("metadata") or {}
        if meta.get("derived_from") or meta.get("variant_key"):
            vcprint(
                f"[thumbnails] file={file_id} is a variant "
                f"(derived_from={meta.get('derived_from')}, "
                f"variant_key={meta.get('variant_key')}) — skipping",
                color="yellow",
            )
            return False
        if record.get("parent_file_id") and not allow_lineage:
            vcprint(
                f"[thumbnails] file={file_id} has parent_file_id={record['parent_file_id']} — skipping",
                color="yellow",
            )
            return False
        if (record.get("file_path") or "").startswith("system-files/"):
            vcprint(
                f"[thumbnails] file={file_id} lives under system-files/ — skipping",
                color="yellow",
            )
            return False

        # Read master bytes — prefer canonical_storage_uri (where present).
        source_uri = record.get("canonical_storage_uri") or record.get("storage_uri")
        if not source_uri:
            return False
        content = await fm.sync_engine.router.read_async(source_uri)
        if not content:
            return False

        # ----- Phase 1d.1: probe + persist intrinsic metadata -----------
        # Probe width / height / duration_ms / page_count from the source
        # bytes. Skip the column update when the row already carries
        # every probed field (avoids a needless write on idempotent
        # re-runs).
        from matrx_utils.file_handling.specific_handlers.thumbnail_source import (
            probe_source_metadata,
            render_kind_specific_variants,
            render_thumbnail_source_bytes,
        )
        probed: dict = {}
        try:
            probed = await probe_source_metadata(content, mime, file_name=record.get("file_name"))
        except Exception:
            probed = {}

        if probed:
            col_updates: dict = {}
            if probed.get("width") is not None and record.get("width") is None:
                col_updates["width"] = probed["width"]
            if probed.get("height") is not None and record.get("height") is None:
                col_updates["height"] = probed["height"]
            if probed.get("duration_ms") is not None and record.get("duration_ms") is None:
                col_updates["duration_ms"] = probed["duration_ms"]
            if probed.get("page_count") is not None:
                base_meta = record.get("metadata") or {}
                if base_meta.get("page_count") != probed["page_count"]:
                    col_updates["metadata"] = {**base_meta, "page_count": probed["page_count"]}
            if col_updates:
                try:
                    await db.update_file_async(file_id, col_updates)
                    # Reflect the update on the in-memory record so the
                    # variants pipeline + caller see consistent data.
                    record = {**record, **col_updates}
                except Exception as e:
                    vcprint(
                        f"[thumbnails] file={file_id} probe-persist failed: {e!r}",
                        color="yellow",
                    )

        # ----- Phase 1: SOCIAL_BASELINE variants ------------------------
        # Rasterise via the universal dispatcher (image passthrough,
        # PDF page 1, video frame, audio waveform, mime-icon fallback).
        raster_bytes, _raster_mime = await render_thumbnail_source_bytes(
            content, mime, file_name=record.get("file_name"),
        )
        from matrx_utils.file_handling import SOCIAL_BASELINE

        rendered = await fm.sync_engine.variants.render_async(
            record,
            variants_specs=list(SOCIAL_BASELINE),
            master_bytes=raster_bytes,
        )

        # ----- Phase 1c: kind-specific full-res variants ---------------
        # PDF page 1 at 150 DPI → page1_url; video frame at native res → poster_url.
        kind_specific: list[str] = []
        try:
            kind_variants = await render_kind_specific_variants(
                content, mime, file_name=record.get("file_name"),
            )
            for key, kind_content, kmime, family in kind_variants:
                await fm.sync_engine.variants.persist_prerendered_async(
                    record,
                    variant_key=key,
                    content=kind_content,
                    mime_type=kmime,
                    variant_family=family,
                )
                kind_specific.append(key)
        except Exception as e:
            vcprint(
                f"[thumbnails] file={file_id} kind-specific failed: {e!r}",
                color="yellow",
            )

        elapsed = (time.monotonic() - started) * 1000
        vcprint(
            f"[thumbnails] file={file_id} mime={mime} "
            f"baseline={list(rendered.keys())} kind={kind_specific} "
            f"probed={list(probed.keys())} elapsed={elapsed:.0f}ms",
            color="cyan",
        )
        return bool(rendered) or bool(kind_specific) or bool(probed)
    except Exception as e:
        vcprint(f"[thumbnails] file={file_id} failed: {e!r}", color="yellow")
        return False


# Alias matching the call-site naming used by aidream's backfill script.
# generate_thumbnail_for_file now does much more than thumbnails (it
# probes metadata + renders kind-specific variants too); the alias
# makes that explicit at the import site.
ensure_media_processing = generate_thumbnail_for_file


__all__ = ["generate_thumbnail_for_file", "ensure_media_processing"]
