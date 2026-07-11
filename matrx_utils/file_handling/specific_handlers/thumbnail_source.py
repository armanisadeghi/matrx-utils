"""Universal thumbnail-source dispatcher.

Given any uploaded file's bytes + mime type, returns rasterised PNG/JPEG
bytes that the image variant pipeline can chew on. This is the
foundation of Phase 1's "every file gets a thumbnail" promise:

    image/*          → passthrough (image_handler renders variants directly)
    application/pdf  → render page 1 to PNG via pdf_handler
    video/*          → extract frame at 10% via video_handler
    audio/*          → mime-icon fallback (waveform rendering is a follow-up)
    other            → mime-icon fallback (kind-specific badge)

The icon fallback is rendered at write time from a small Pillow-based
template — no binary PNG blobs committed to the repo, no extra runtime
dependencies beyond Pillow (already a matrx-utils dep).

Use:

    from matrx_utils.file_handling.specific_handlers.thumbnail_source import (
        render_thumbnail_source_bytes,
    )

    rast_bytes, rast_mime = await render_thumbnail_source_bytes(
        content_bytes, mime_type, file_name=upload.filename,
    )
    # rast_bytes can now be passed to image_handler / variants_service
    # like any image master.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Literal

logger = logging.getLogger(__name__)


# Synchronous icon-render cache. Icons are deterministic per (kind, label)
# so we only render each unique combination once per process. Bounded by
# the small fixed kind catalogue + the handful of family labels we emit.
_ICON_CACHE: dict[tuple[str, str], bytes] = {}


# Mime family colour palette. Soft, distinct, high-contrast on white.
# Kept short on purpose — adding a new family is a single dict entry.
_MIME_FAMILY_COLORS: dict[str, str] = {
    "image":    "#3B82F6",  # blue
    "video":    "#EF4444",  # red
    "audio":    "#10B981",  # green
    "pdf":      "#DC2626",  # red-600 (PDF brand-adjacent)
    "document": "#6366F1",  # indigo
    "archive":  "#F59E0B",  # amber
    "text":     "#64748B",  # slate
    "code":     "#8B5CF6",  # violet
    "generic":  "#94A3B8",  # slate-400
}


# Generic mime → family classification. We render the same icon for every
# member of a family — granularity beyond this is a UI concern.
def _mime_family(mime_type: str | None) -> str:
    if not mime_type:
        return "generic"
    mt = mime_type.lower().strip()
    if mt.startswith("image/"):
        return "image"
    if mt.startswith("video/"):
        return "video"
    if mt.startswith("audio/"):
        return "audio"
    if mt == "application/pdf":
        return "pdf"
    if mt in {
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
    }:
        return "document"
    if mt in {
        "application/zip",
        "application/x-tar",
        "application/x-gzip",
        "application/x-bzip2",
        "application/x-7z-compressed",
        "application/x-rar-compressed",
    }:
        return "archive"
    if mt.startswith("text/"):
        # text/plain → text; text/x-python, text/javascript → code
        if "/" in mt and any(tok in mt for tok in ("python", "javascript", "typescript", "rust", "html", "css", "json", "yaml", "x-")):
            return "code"
        return "text"
    if mt.startswith("application/json") or mt.startswith("application/yaml"):
        return "code"
    return "generic"


def _family_label(family: str, mime_type: str | None) -> str:
    """Short uppercase label rendered on the icon. PDF → 'PDF', video/mp4 → 'MP4', etc."""
    if mime_type:
        sub = mime_type.split("/", 1)[-1].split(";", 1)[0].strip().upper()
        # Strip vendor prefixes for readability.
        for prefix in ("X-", "VND.", "VND."):
            if sub.startswith(prefix):
                sub = sub[len(prefix):]
        if "+" in sub:
            sub = sub.split("+", 1)[0]
        # Pick the rightmost dotted token as the most identifying piece.
        if "." in sub:
            sub = sub.rsplit(".", 1)[-1]
        if 1 <= len(sub) <= 6:
            return sub
    return family.upper()


def render_mime_icon_bytes(
    *,
    mime_type: str | None,
    width: int = 800,
    height: int = 800,
) -> bytes:
    """Render a mime-family icon as a PNG. Deterministic + memoised.

    Returns PNG bytes suitable for the image variant pipeline. The output
    is square by default; callers can pass non-square dims for kind-
    specific framings (e.g. 1200×630 for og_url) but the renderer always
    centres a square badge so aspect ratio is just letterbox.
    """
    family = _mime_family(mime_type)
    label = _family_label(family, mime_type)
    cache_key = (f"{family}:{label}", f"{width}x{height}")
    cached = _ICON_CACHE.get(cache_key)
    if cached is not None:
        return cached

    from io import BytesIO

    from PIL import Image, ImageDraw, ImageFont

    color = _MIME_FAMILY_COLORS.get(family, _MIME_FAMILY_COLORS["generic"])

    img = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(img)

    # Background rounded-rect badge — fills 80% of the square.
    margin = min(width, height) // 10
    badge_box = (margin, margin, width - margin, height - margin)
    try:
        draw.rounded_rectangle(badge_box, radius=min(width, height) // 12, fill=color)
    except AttributeError:
        # Pillow < 8.2 — rounded_rectangle not available. Plain rect is fine.
        draw.rectangle(badge_box, fill=color)

    # Label text. Try the default sans-serif at a size proportional to the
    # box; Pillow's default raster font is fixed-size but always works.
    text = label or "FILE"
    try:
        font_size = max(12, min(width, height) // 5)
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
    except (OSError, AttributeError):
        font = ImageFont.load_default()

    # Centre the text inside the badge.
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = (width - tw) // 2 - bbox[0]
    ty = (height - th) // 2 - bbox[1]
    draw.text((tx, ty), text, fill="white", font=font)

    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    out = buf.getvalue()
    _ICON_CACHE[cache_key] = out
    return out


# ---------------------------------------------------------------------------
# Per-family rasterisers
# ---------------------------------------------------------------------------


def _render_pdf_first_page(pdf_bytes: bytes) -> tuple[bytes, str]:
    """Render page 1 of a PDF to PNG bytes at thumbnail-suitable DPI."""
    from .pdf import handler as _pdf_handler_module  # lazy — pdfium pulls native deps

    # Lower DPI than full-quality rendering — thumbnails downsample
    # anyway, so 100 DPI of an A4 page = ~830×1170 (plenty for og_url).
    rendered = _pdf_handler_module.render_page_to_image_bytes(
        pdf_bytes, page=1, dpi=100, fmt="png",
    )
    # PdfPageRender exposes .content (bytes) + .format ("png") — it has no
    # .bytes/.mime_type; reading those made EVERY pdf page-1 thumbnail fall
    # back to the mime icon (found 2026-07-10 via the scan backfill).
    return rendered.content, "image/png"


def _render_video_frame(video_bytes: bytes) -> tuple[bytes, str]:
    """Extract a representative frame from a video as JPEG."""
    from .video_handler import VideoHandler

    frame = VideoHandler.extract_frame_at(video_bytes, position=0.10)
    return frame, "image/jpeg"


# Waveform rendering tunables — kept module-level so subsystems can override.
_WAVEFORM_WIDTH = 1600
_WAVEFORM_HEIGHT = 400
_WAVEFORM_PEAKS = 800
_WAVEFORM_BG = "#0f172a"      # slate-900 — dark, professional
_WAVEFORM_FG = "#38bdf8"      # sky-400 — high-contrast, clear at small sizes
_WAVEFORM_CENTER = "#0ea5e9"  # sky-500 — accent for the centreline


def _render_audio_waveform(audio_bytes: bytes, mime_type: str | None) -> tuple[bytes, str]:
    """Render an audio waveform as a PNG.

    Decodes via pydub (which uses ffmpeg under the hood for arbitrary
    formats), computes ``_WAVEFORM_PEAKS`` evenly-spaced peak amplitudes
    across the file's duration, and draws them as a centred-axis wave
    using Pillow. Returns ``(png_bytes, "image/png")``.

    Raises on any decode/render failure — the caller's try/except in
    the dispatcher catches and falls back to a mime-family icon.
    """
    from io import BytesIO

    from pydub import AudioSegment
    from PIL import Image, ImageDraw

    # Decode via pydub. ``from_file`` autodetects the format from the
    # bytes when possible, but for some formats it needs a hint.
    fmt_hint = None
    if mime_type:
        sub = mime_type.split("/", 1)[-1].lower().split(";", 1)[0].strip()
        # Map common audio subtypes to pydub format names.
        fmt_hint = {
            "mpeg": "mp3",
            "mp3": "mp3",
            "wav": "wav",
            "x-wav": "wav",
            "ogg": "ogg",
            "vorbis": "ogg",
            "flac": "flac",
            "aac": "aac",
            "mp4": "m4a",
            "x-m4a": "m4a",
            "webm": "webm",
            "opus": "opus",
        }.get(sub)
    audio = AudioSegment.from_file(BytesIO(audio_bytes), format=fmt_hint)

    # Mono-mix for a single waveform trace; sample array is signed int.
    samples = audio.set_channels(1).get_array_of_samples()
    total = len(samples)
    if total == 0:
        raise RuntimeError("audio decoded to zero samples")

    # Compute per-bucket peak amplitudes (abs max within each window).
    # max sample magnitude is 2^(sample_width*8 - 1); normalise to 0..1.
    max_amp = max(1, 2 ** (audio.sample_width * 8 - 1))
    bucket = max(1, total // _WAVEFORM_PEAKS)
    peaks: list[float] = []
    for i in range(_WAVEFORM_PEAKS):
        start = i * bucket
        end = min(total, start + bucket)
        if start >= end:
            peaks.append(0.0)
            continue
        slice_ = samples[start:end]
        peak = max(abs(int(s)) for s in slice_) / max_amp
        peaks.append(min(1.0, peak))

    # Render. Centre axis at H/2, draw bars symmetric above/below.
    img = Image.new("RGB", (_WAVEFORM_WIDTH, _WAVEFORM_HEIGHT), _WAVEFORM_BG)
    draw = ImageDraw.Draw(img)
    mid = _WAVEFORM_HEIGHT // 2
    bar_w = max(1, _WAVEFORM_WIDTH // _WAVEFORM_PEAKS)
    for i, peak in enumerate(peaks):
        h = int(peak * (mid - 4))  # leave a 4px breathing margin
        x = i * bar_w
        draw.rectangle(
            (x, mid - h, x + bar_w - 1, mid + h),
            fill=_WAVEFORM_FG,
        )
    # Subtle centre line for visual anchor.
    draw.line((0, mid, _WAVEFORM_WIDTH, mid), fill=_WAVEFORM_CENTER, width=1)

    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue(), "image/png"


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------


ThumbnailKind = Literal["image", "video", "audio", "document", "archive", "text", "code", "generic"]


def render_thumbnail_source_bytes_sync(
    content_bytes: bytes,
    mime_type: str | None,
    *,
    file_name: str | None = None,
) -> tuple[bytes, str]:
    """Synchronous core. See :func:`render_thumbnail_source_bytes`.

    Use the async wrapper from FastAPI / web routes — PDF and video
    rasterisation are CPU-bound and will block the loop here.
    """
    family = _mime_family(mime_type)

    # Image: pass through. The image variant pipeline can re-encode for any
    # target size + format.
    if family == "image":
        return content_bytes, mime_type or "image/png"

    # PDF: render page 1.
    if family == "pdf":
        try:
            return _render_pdf_first_page(content_bytes)
        except Exception as exc:
            logger.warning(
                "thumbnail_source: PDF page-1 render failed for %s (%s); using mime icon",
                file_name, exc,
            )
            return render_mime_icon_bytes(mime_type=mime_type), "image/png"

    # Video: extract frame at 10%.
    if family == "video":
        try:
            return _render_video_frame(content_bytes)
        except Exception as exc:
            logger.warning(
                "thumbnail_source: video frame extraction failed for %s (%s); using mime icon",
                file_name, exc,
            )
            return render_mime_icon_bytes(mime_type=mime_type), "image/png"

    # Audio: render a waveform PNG via pydub + Pillow. pydub uses
    # ffmpeg under the hood for arbitrary formats. Falls back to the
    # mime-family icon when pydub / ffmpeg are unavailable or the file
    # can't be decoded.
    if family == "audio":
        try:
            return _render_audio_waveform(content_bytes, mime_type)
        except Exception as exc:
            logger.warning(
                "thumbnail_source: audio waveform failed for %s (%s); using mime icon",
                file_name, exc,
            )
            return render_mime_icon_bytes(mime_type=mime_type), "image/png"

    # Document / archive / text / code / generic — fall back to the
    # mime-family icon. No richer visual representation is possible
    # without per-format tooling.
    return render_mime_icon_bytes(mime_type=mime_type), "image/png"


async def render_thumbnail_source_bytes(
    content_bytes: bytes,
    mime_type: str | None,
    *,
    file_name: str | None = None,
) -> tuple[bytes, str]:
    """Returns (image_bytes, source_mime) ready for the variant pipeline.

    image/*          → passthrough.
    application/pdf  → first-page render via pdfium (~100 DPI).
    video/*          → frame at 10% via OpenCV.
    everything else  → mime-family icon (deterministic, memoised).

    Errors in any per-kind rasteriser are caught and fall back to the
    mime-family icon so a broken file never blocks the upload pipeline.

    CPU work runs in the default thread executor so the event loop stays
    responsive.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: render_thumbnail_source_bytes_sync(
            content_bytes, mime_type, file_name=file_name,
        ),
    )


# ---------------------------------------------------------------------------
# Kind-specific full-resolution variants
# ---------------------------------------------------------------------------
#
# Phase 1c — in addition to the SOCIAL_BASELINE thumbnails (small image
# previews shared across every file kind), some mime kinds get a full-
# resolution primary representation that is browser-renderable:
#
#   application/pdf → page1_url  : page 1 rendered at 150 DPI as JPEG
#                                  (~1200×1700 for an A4 page — a real
#                                  reading preview, not just a thumbnail)
#   video/*         → poster_url : frame at 10% extracted at native
#                                  resolution as JPEG (the standard
#                                  HTML5 <video poster=...> source)
#
# These keys are stable so the FE can bind to them directly:
#
#   DocumentBlock.page1_url   = variants["page1_url"].url
#   VideoBlock.poster_url     = variants["poster_url"].url
#
# Returns a list of (key, content_bytes, mime_type, variant_family)
# tuples — VariantsService.persist_prerendered_async stores each one as
# a variant cld_files row linked back to the master via
# metadata.derived_from. Idempotent at the (master_id, variant_key)
# level — re-runs are no-ops.


KindSpecificVariant = tuple[str, bytes, str, str]


def render_kind_specific_variants_sync(
    content_bytes: bytes,
    mime_type: str | None,
    *,
    file_name: str | None = None,
) -> list[KindSpecificVariant]:
    """Render every kind-specific full-res variant the source supports.

    Returns ``[]`` for mime kinds without a kind-specific variant
    (images already serve as their own primary; audio waveform deferred
    to Phase 1d). Per-kind renderer failures are caught and the
    offending variant is simply skipped — never raises.
    """
    family = _mime_family(mime_type)
    out: list[KindSpecificVariant] = []

    if family == "pdf":
        try:
            from .pdf import handler as _pdf_handler_module
            rendered = _pdf_handler_module.render_page_to_image_bytes(
                content_bytes, page=1, dpi=150, fmt="jpeg", jpeg_quality=85,
            )
            out.append(("page1_url", rendered.content, "image/jpeg", "document"))
        except Exception as exc:
            logger.warning(
                "kind_specific_variants: page1 render failed for %s (%s) — skipping",
                file_name, exc,
            )

    elif family == "video":
        try:
            from .video_handler import VideoHandler
            frame = VideoHandler.extract_frame_at(content_bytes, position=0.10)
            out.append(("poster_url", frame, "image/jpeg", "video"))
        except Exception as exc:
            logger.warning(
                "kind_specific_variants: video poster failed for %s (%s) — skipping",
                file_name, exc,
            )

    # image / audio / archive / text / code / generic: no kind-specific
    # variant in Phase 1c. Audio waveform comes in Phase 1d.
    return out


async def render_kind_specific_variants(
    content_bytes: bytes,
    mime_type: str | None,
    *,
    file_name: str | None = None,
) -> list[KindSpecificVariant]:
    """Async wrapper around ``render_kind_specific_variants_sync``."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: render_kind_specific_variants_sync(
            content_bytes, mime_type, file_name=file_name,
        ),
    )


# ---------------------------------------------------------------------------
# Source-metadata probe — populates queryable cld_files columns
# ---------------------------------------------------------------------------
#
# Phase 1d.1 — extracts width / height / duration_ms / page_count from the
# uploaded bytes so cld_files rows carry these as first-class columns
# (queryable + indexable) instead of being inferable only via re-decoding
# the file. The fields are wired straight onto the FE-visible Pydantic
# blocks (ImageBlock/VideoBlock width/height, Audio/VideoBlock
# duration_ms, DocumentBlock page_count).
#
# Returns a TypedDict with only the keys that could be probed. Mime kinds
# with nothing to probe (archives, text, generic) return {}. Every probe
# is wrapped in try/except — failures degrade gracefully to "field stays
# null", never block the upload.


from typing import TypedDict


class ProbedMetadata(TypedDict, total=False):
    width: int
    height: int
    duration_ms: int
    page_count: int


def probe_source_metadata_sync(
    content_bytes: bytes,
    mime_type: str | None,
    *,
    file_name: str | None = None,
) -> ProbedMetadata:
    """Extract queryable metadata fields from upload bytes.

    Returns the subset of ``ProbedMetadata`` that could be extracted
    for this source — empty dict when nothing's probable. Never raises.
    """
    out: ProbedMetadata = {}
    family = _mime_family(mime_type)

    if family == "image":
        try:
            from io import BytesIO
            from PIL import Image
            img = Image.open(BytesIO(content_bytes))
            out["width"] = int(img.width)
            out["height"] = int(img.height)
        except Exception as exc:
            logger.debug("probe: image dims failed for %s (%s)", file_name, exc)

    elif family == "pdf":
        try:
            import pypdfium2 as pdfium
            doc = pdfium.PdfDocument(content_bytes)
            try:
                out["page_count"] = int(len(doc))
                # First page dimensions in points → approximate pixel
                # dimensions at the SOCIAL_BASELINE render DPI (150).
                if len(doc) > 0:
                    page = doc[0]
                    w_pt, h_pt = page.get_size()
                    out["width"] = int(w_pt * 150 / 72)
                    out["height"] = int(h_pt * 150 / 72)
            finally:
                doc.close()
        except Exception as exc:
            logger.debug("probe: pdf metadata failed for %s (%s)", file_name, exc)

    elif family == "video":
        try:
            import os
            import tempfile

            import cv2  # type: ignore
            tmp_path: str | None = None
            try:
                with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as tmp:
                    tmp.write(content_bytes)
                    tmp_path = tmp.name
                cap = cv2.VideoCapture(tmp_path)
                if cap.isOpened():
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0)
                    frames = float(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
                    if width > 0:
                        out["width"] = width
                    if height > 0:
                        out["height"] = height
                    if fps > 0 and frames > 0:
                        out["duration_ms"] = int((frames / fps) * 1000)
                cap.release()
            finally:
                if tmp_path:
                    try:
                        os.unlink(tmp_path)
                    except OSError:
                        pass
        except Exception as exc:
            logger.debug("probe: video metadata failed for %s (%s)", file_name, exc)

    elif family == "audio":
        try:
            from io import BytesIO
            from pydub import AudioSegment
            fmt_hint = None
            if mime_type:
                sub = mime_type.split("/", 1)[-1].lower().split(";", 1)[0].strip()
                fmt_hint = {
                    "mpeg": "mp3", "mp3": "mp3", "wav": "wav", "x-wav": "wav",
                    "ogg": "ogg", "vorbis": "ogg", "flac": "flac",
                    "aac": "aac", "mp4": "m4a", "x-m4a": "m4a",
                    "webm": "webm", "opus": "opus",
                }.get(sub)
            audio = AudioSegment.from_file(BytesIO(content_bytes), format=fmt_hint)
            out["duration_ms"] = int(len(audio))  # pydub: len() is duration_ms
        except Exception as exc:
            logger.debug("probe: audio metadata failed for %s (%s)", file_name, exc)

    return out


async def probe_source_metadata(
    content_bytes: bytes,
    mime_type: str | None,
    *,
    file_name: str | None = None,
) -> ProbedMetadata:
    """Async wrapper around ``probe_source_metadata_sync``."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: probe_source_metadata_sync(content_bytes, mime_type, file_name=file_name),
    )


__all__ = [
    "ThumbnailKind",
    "KindSpecificVariant",
    "ProbedMetadata",
    "render_thumbnail_source_bytes",
    "render_thumbnail_source_bytes_sync",
    "render_kind_specific_variants",
    "render_kind_specific_variants_sync",
    "render_mime_icon_bytes",
    "probe_source_metadata",
    "probe_source_metadata_sync",
]
