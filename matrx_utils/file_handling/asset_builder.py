"""Asset envelope construction — pure functions over (FileManager, record).

This module is the single source of truth for converting a master
cld_files row (plus any rendered variant siblings) into the canonical
``Asset`` wire shape. Lives in matrx-utils so every host produces the
same envelope without re-implementing the logic.

Public API:

  - ``build_asset_from_master(fm, master_record, *, ...) -> Asset``
      Top-level builder. Pulls the master, lists sibling variants by
      walking the deterministic ``{master_dir}/v/`` subfolder, and
      assembles the wire shape with all four URL flavours per variant.

  - ``sanitize_asset_metadata(metadata) -> dict``
      Strips internal-only keys (``_*`` and ``request_id``) from a
      cld_files row's metadata before echoing it in an Asset response.

  - ``image_dimensions(image_bytes) -> (width|None, height|None)``
      Cheap PIL-based dimension probe. Returns (None, None) for
      non-image bytes or PIL failures.

  - ``key_from_variant_record(record) -> str``
      Recover a variant's logical key from its cld_files row metadata
      (falls back to the filename stem for legacy rows).
"""

from __future__ import annotations

from io import BytesIO
from typing import Any

from .asset_envelope import Asset, AssetVariant


# Internal metadata keys that must NEVER leak in an Asset response.
_INTERNAL_METADATA_PREFIXES: tuple[str, ...] = ("_",)
_INTERNAL_METADATA_KEYS: frozenset[str] = frozenset({
    "request_id",
})


def sanitize_asset_metadata(metadata: dict[str, Any] | None) -> dict[str, Any]:
    """Drop internal-only keys before echoing metadata in an Asset response.

    Strips keys starting with an underscore (idempotency tokens, audit
    breadcrumbs) and a small explicit blocklist (request_id stamps).
    Anything that started with internal=True semantics should land in
    one of these buckets.
    """
    if not metadata:
        return {}
    return {
        k: v
        for k, v in metadata.items()
        if not k.startswith(_INTERNAL_METADATA_PREFIXES) and k not in _INTERNAL_METADATA_KEYS
    }


def image_dimensions(image_bytes: bytes) -> tuple[int | None, int | None]:
    """Cheap dimension probe for image bytes. Returns (None, None) for non-images."""
    if not image_bytes:
        return None, None
    try:
        from PIL import Image  # type: ignore[import-not-found]
        with Image.open(BytesIO(image_bytes)) as im:
            return int(im.width), int(im.height)
    except Exception:
        return None, None


def key_from_variant_record(record: dict) -> str:
    """Recover the variant ``key`` from a cld_files row.

    Variant rows carry ``{"variant_key": "...", "variant_family": "image"}``
    in their metadata jsonb. Falls back to the filename stem when missing
    (some legacy rows predate the metadata stamp).
    """
    md = record.get("metadata") or {}
    if isinstance(md, dict) and md.get("variant_key"):
        return str(md["variant_key"])
    name = record.get("file_name") or ""
    stem = name.rsplit(".", 1)[0]
    return stem or "unknown"


async def _build_variant_from_record(
    fm: Any,
    record: dict,
    variant_key: str,
    *,
    signed_ttl: int = 3600,
    width: int | None = None,
    height: int | None = None,
) -> AssetVariant:
    urls = await fm.sync_engine.build_urls_for_record_async(record, signed_ttl=signed_ttl)
    return AssetVariant(
        key=variant_key,
        file_id=record["id"],
        file_path=record["file_path"],
        width=width,
        height=height,
        mime_type=record.get("mime_type"),
        size_bytes=record.get("size_bytes"),
        url=urls["url"],
        cdn_url=urls["cdn_url"],
        signed_url=urls["signed_url"],
        download_url=urls["download_url"],
        metadata=sanitize_asset_metadata(record.get("metadata")),
    )


async def _list_existing_variants_for_master(
    fm: Any, master_record: dict
) -> list[dict]:
    """List every cld_files row under the master's variant subfolder.

    Variant rows live at ``{master_dir}/v/{key}.{ext}`` via the
    deterministic path convention. We enumerate all files in that
    folder so an Asset reflects whatever has been rendered so far,
    regardless of which preset asked for it.
    """
    db = fm.sync_engine.db
    parent_path = master_record["file_path"]
    parent_dir = "/".join(parent_path.split("/")[:-1])
    variant_dir = f"{parent_dir}/v" if parent_dir else "v"
    owner_id = master_record["owner_id"]
    folder = await db.get_folder_by_path_async(owner_id, variant_dir)
    if not folder:
        return []
    return await db.list_files_async(owner_id, folder["id"])


async def _resolve_master_dimensions_cached(
    fm: Any, master_record: dict
) -> tuple[int | None, int | None]:
    """Probe image dimensions from the in-process byte cache only.

    Never reaches out to cloud — we don't want a ``GET /assets/{id}`` to
    pay an S3 read just to fill ``width`` / ``height`` on the master.
    Returns ``(None, None)`` if the bytes aren't cached.
    """
    try:
        from .cloud_sync.byte_cache import get_byte_cache
        hit = get_byte_cache().get(master_record["id"])
    except Exception:
        hit = None
    if not hit:
        return None, None
    blob = getattr(hit, "bytes_", None) or getattr(hit, "bytes", None)
    if not blob:
        return None, None
    return image_dimensions(blob)


async def build_asset_from_master(
    fm: Any,
    master_record: dict,
    *,
    preset_name: str | None = None,
    primary_key: str | None = None,
    signed_ttl: int = 3600,
    include_variants: bool = True,
    master_width: int | None = None,
    master_height: int | None = None,
) -> Asset:
    """Assemble an Asset envelope from a master + its persisted variants.

    ``master_width`` / ``master_height`` are an optimisation — when the
    caller already has the dimensions (e.g. just rendered the master),
    they're stamped onto the ``original`` variant without a re-decode.
    For images that arrive via ``GET /assets/{id}`` we lazy-probe the
    cached bytes via the byte cache instead of pulling the full master
    from cloud — see ``_resolve_master_dimensions_cached``.

    ``preset_name`` is used to look up the primary variant key from the
    ``PRESETS`` registry. If ``primary_key`` is supplied explicitly it
    wins. Either way the resolved key falls back to ``"original"`` when
    the requested variant isn't in the bag.
    """
    from .specific_handlers.image_handler import PRESETS

    master_dir_parts = master_record["file_path"].split("/")
    folder = "/".join(master_dir_parts[:-1]) or master_record.get("file_name") or ""

    original = await _build_variant_from_record(
        fm, master_record, "original",
        signed_ttl=signed_ttl,
        width=master_width,
        height=master_height,
    )
    # Lazy-probe dimensions from the byte cache when needed and the
    # master is an image. Cache-only — never a network read.
    if (
        (original.width is None or original.height is None)
        and (master_record.get("mime_type") or "").startswith("image/")
    ):
        w, h = await _resolve_master_dimensions_cached(fm, master_record)
        if w is not None and h is not None:
            original = original.model_copy(update={"width": w, "height": h})

    variants: dict[str, AssetVariant] = {"original": original}

    if include_variants:
        rows = await _list_existing_variants_for_master(fm, master_record)
        for r in rows:
            v_key = key_from_variant_record(r)
            variants[v_key] = await _build_variant_from_record(
                fm, r, v_key, signed_ttl=signed_ttl,
            )

    # Resolve primary key + primary URL.
    if primary_key is None:
        if preset_name and preset_name in PRESETS:
            primary_key = PRESETS[preset_name]["primary_key"]
        else:
            primary_key = "original"
    if primary_key not in variants:
        primary_key = "original"
    primary_url = variants[primary_key].url

    return Asset(
        file_id=master_record["id"],
        visibility=master_record.get("visibility") or "private",  # type: ignore[arg-type]
        folder=folder,
        preset=preset_name,
        primary_key=primary_key,
        primary_url=primary_url,
        variants=variants,
        metadata=sanitize_asset_metadata(master_record.get("metadata")),
    )


__all__ = [
    "build_asset_from_master",
    "sanitize_asset_metadata",
    "image_dimensions",
    "key_from_variant_record",
]
