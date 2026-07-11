"""Generic, encoder-injected variant primitive.

A "variant" is a derived file produced from a master ``cld_files`` row by
running an encoder over the master's bytes. Variants are themselves
``cld_files`` rows under a deterministic path so they get share links,
permissions, CDN URLs, checksum cache-busting, lifecycle policy — every
existing platform feature applies for free.

This module is intentionally encoder-agnostic. The host (or a sibling
package like matrx-ai) registers an encoder for a *family* (e.g.
``"vision"``) and a *variant key* (e.g. ``"anthropic_opus_hires"``).
matrx-utils never imports matrx-ai.

Wire shape
----------

A master file lives at::

    {master.file_path}                       (e.g. screenshots/<uuid>/master.jpg)

Its variants live alongside under a deterministic ``v/`` subfolder::

    {master_dir}/v/{variant_key}.{ext}       (e.g. screenshots/<uuid>/v/anthropic_opus_hires.jpg)

The variant's ``cld_files.metadata`` carries::

    {
        "derived_from": "<master_file_id>",
        "variant_family": "vision",
        "variant_key": "anthropic_opus_hires",
    }

Idempotency
-----------

``render_variant_async`` short-circuits when a variant row already exists
for the given (master_file_id, variant_key) pair. The encoder is invoked
exactly once per master+key tuple per process — re-runs are free.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from posixpath import dirname
from typing import TYPE_CHECKING, Any

logger = logging.getLogger(__name__)


# Encoder signature: receives master bytes + variant key, returns
# (encoded_bytes, mime_type). Encoders are pure — no I/O, no DB.
VariantEncoder = Callable[[bytes, str], "Awaitable[tuple[bytes, str]] | tuple[bytes, str]"]


# Process-level registry: family -> encoder. Hosts call register_variant_encoder()
# at startup. Lookups happen inside render_variant_async().
_ENCODERS: dict[str, VariantEncoder] = {}


def register_variant_encoder(family: str, encoder: VariantEncoder) -> None:
    """Register an encoder for a variant family.

    A "family" is a top-level namespace like ``"vision"`` (used for LLM
    image re-encoding) or ``"thumbnail"``. The encoder receives the
    master bytes plus the specific variant key and returns the encoded
    bytes plus their mime_type.

    Calling this with the same ``family`` replaces the previous encoder.
    """
    if not callable(encoder):
        raise TypeError(f"encoder for family {family!r} must be callable")
    _ENCODERS[family] = encoder
    logger.info("[variants] registered encoder for family=%s", family)


def get_variant_encoder(family: str) -> VariantEncoder | None:
    return _ENCODERS.get(family)


def has_variant_encoder(family: str) -> bool:
    return family in _ENCODERS


# ---------------------------------------------------------------------------
# Path / filename helpers
# ---------------------------------------------------------------------------

# Map common image mime_types to file extensions for variant filenames.
_MIME_TO_EXT: dict[str, str] = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
    "image/heic": "heic",
}


def _ext_for_mime(mime: str) -> str:
    if not mime:
        return "bin"
    norm = mime.lower().split(";", 1)[0].strip()
    if norm in _MIME_TO_EXT:
        return _MIME_TO_EXT[norm]
    if "/" in norm:
        return norm.split("/", 1)[1]
    return "bin"


def variant_file_path(master_file_path: str, variant_key: str, ext: str) -> str:
    """Build the deterministic logical path for a variant of a master.

    Master:  ``a/b/master.jpg``
    Variant: ``a/b/v/{variant_key}.{ext}``

    For a master with no parent folder (just ``master.jpg``), the variant
    is placed at ``v/{variant_key}.{ext}``.
    """
    master_dir = dirname(master_file_path)
    name = f"{variant_key}.{ext}"
    return f"{master_dir}/v/{name}" if master_dir else f"v/{name}"


# ---------------------------------------------------------------------------
# Render entry points
# ---------------------------------------------------------------------------

if TYPE_CHECKING:
    from ..file_manager import FileManager


async def render_variant_async(
    fm: FileManager,
    master_file_id: str,
    *,
    variant_key: str,
    family: str = "vision",
    encoder: VariantEncoder | None = None,
) -> dict[str, Any]:
    """Resolve (or render and persist) a variant for ``master_file_id``.

    Parameters
    ----------
    fm
        A FileManager with cloud_sync configured.
    master_file_id
        The cld_files UUID for the master file.
    variant_key
        The variant identifier within the family (e.g. ``"anthropic_opus_hires"``).
    family
        The encoder family. Defaults to ``"vision"``.
    encoder
        Optional override; falls back to the family-registered encoder.

    Returns
    -------
    A dict with the resolved variant's cld_files-style fields:

        {
            "file_id": <uuid>,
            "storage_uri": "s3://...",
            "file_path": "...",
            "mime_type": "image/jpeg",
            "size_bytes": 12345,
            "url": "<signed url>",   # may be None if the router can't sign
            "is_new": False,         # True iff this call rendered the variant
            "metadata": {...},
        }

    Raises
    ------
    RuntimeError
        When no encoder is registered for ``family`` and ``encoder`` is None.
    FileNotFoundError
        When the master record cannot be found.
    """
    se = fm._require_sync_engine()
    db = se.db
    router = se.router

    master = await db.get_file_async(master_file_id)
    if not master:
        raise FileNotFoundError(f"master file_id {master_file_id} not found")

    enc = encoder or get_variant_encoder(family)
    if enc is None:
        raise RuntimeError(
            f"no variant encoder registered for family={family!r}; "
            f"call register_variant_encoder({family!r}, encoder) at startup."
        )

    master_path: str = master["file_path"]
    owner_id: str = master["owner_id"]

    # Try a path-based hit first — variants are deterministic by (master, key).
    # Probe the JPEG extension first (the common case for vision); fall back
    # to a wider scan only if needed.
    for guess_ext in ("jpg", "png", "webp", "bin"):
        guess_path = variant_file_path(master_path, variant_key, guess_ext)
        existing = await db.get_file_by_path_async(owner_id, guess_path)
        if existing:
            urls = await se.build_urls_for_record_async(existing)
            return {
                "file_id": existing["id"],
                "storage_uri": existing["storage_uri"],
                "file_path": existing["file_path"],
                "mime_type": existing.get("mime_type"),
                "size_bytes": existing.get("size_bytes"),
                "url": urls["url"],
                "signed_url_expires_at": urls.get("signed_url_expires_at"),
                "cdn_url": urls["cdn_url"],
                "signed_url": urls["signed_url"],
                "download_url": urls["download_url"],
                "is_new": False,
                "metadata": existing.get("metadata") or {},
            }

    # Cache miss — read master bytes, run encoder, write variant row.
    master_bytes = await router.read_async(master["storage_uri"])

    raw = enc(master_bytes, variant_key)
    if hasattr(raw, "__await__"):
        encoded_bytes, encoded_mime = await raw  # type: ignore[misc]
    else:
        encoded_bytes, encoded_mime = raw  # type: ignore[misc]

    ext = _ext_for_mime(encoded_mime)
    variant_path = variant_file_path(master_path, variant_key, ext)

    metadata = {
        "derived_from": master_file_id,
        "variant_family": family,
        "variant_key": variant_key,
    }

    result = await se.managed_write_async(
        variant_path,
        encoded_bytes,
        mime_type=encoded_mime,
        visibility=master.get("visibility") or "private",
        user_id=owner_id,
        metadata=metadata,
    )

    return {
        "file_id": result.file_id,
        "storage_uri": result.storage_uri,
        "file_path": variant_path,
        "mime_type": encoded_mime,
        "size_bytes": len(encoded_bytes),
        "url": result.url,
        "cdn_url": result.cdn_url,
        "signed_url": result.signed_url,
        "download_url": result.download_url,
        "is_new": result.is_new,
        "metadata": metadata,
    }


__all__ = [
    "VariantEncoder",
    "register_variant_encoder",
    "get_variant_encoder",
    "has_variant_encoder",
    "variant_file_path",
    "render_variant_async",
]
