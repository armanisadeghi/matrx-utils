"""VideoHandler — frame extraction and cloud upload for video files.

Requires ``opencv-python`` (or ``opencv-python-headless``) for frame extraction.
The dependency is imported lazily inside the methods so that the handler can be
imported without cv2 installed (it will raise only when frame methods are called).

Typical usage in a FastAPI route
---------------------------------
    from matrx_utils.file_handling import FileManager, PODCAST_VARIANTS

    fm = FileManager.get_instance("my_app")

    # Upload a video and get its public URL
    video_url = await fm.video_handler.upload_video_async(
        video_bytes,
        "supabase://podcast-assets/{user_id}/{uuid}/video.mp4",
        content_type="video/mp4",
    )

    # Extract a thumbnail frame and generate image variants from it
    frame_bytes = await fm.video_handler.extract_frame_at_async(video_bytes)
    urls = await fm.image_handler.process_variants_async(
        frame_bytes, PODCAST_VARIANTS, "supabase://podcast-assets/{user_id}/{uuid}"
    )
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from io import BytesIO

from matrx_utils.file_handling.file_handler import FileHandler


class VideoHandler(FileHandler):
    """Handles video upload and frame extraction for media processing pipelines."""

    SUPPORTED_CONTENT_TYPES: frozenset[str] = frozenset({
        "video/mp4",
        "video/quicktime",   # MOV
        "video/webm",
        "video/x-msvideo",   # AVI
        "video/x-matroska",  # MKV
    })

    # ------------------------------------------------------------------
    # Format validation
    # ------------------------------------------------------------------

    @classmethod
    def is_supported_format(cls, content_type: str) -> bool:
        """Return True if *content_type* is a supported video MIME type."""
        return content_type in cls.SUPPORTED_CONTENT_TYPES

    # ------------------------------------------------------------------
    # Frame extraction — pure CPU, runs in executor for async callers
    # ------------------------------------------------------------------

    @staticmethod
    def extract_frame_at(video_bytes: bytes, position: float = 0.10) -> bytes:
        """Extract a single frame from a video at *position* (0.0–1.0) duration.

        Writes *video_bytes* to a named temp file (OpenCV requires a filesystem
        path), seeks to the target frame, converts BGR to RGB, and returns JPEG
        bytes at quality 90. The temp file is always cleaned up.

        Parameters
        ----------
        video_bytes:
            Raw bytes of the video file (MP4, MOV, WebM, etc.).
        position:
            Fractional position within the video (0.0 = first frame,
            0.10 = 10% through, 0.5 = midpoint, 1.0 = last frame).
            Defaults to 0.10 (10%) which typically avoids black intro frames.

        Returns
        -------
        bytes
            JPEG-encoded bytes of the extracted frame.

        Raises
        ------
        RuntimeError
            If the video cannot be opened or the frame cannot be read.
        ImportError
            If ``opencv-python`` (cv2) is not installed.
        """
        try:
            import cv2
        except ImportError as exc:
            raise ImportError(
                "VideoHandler.extract_frame_at requires opencv-python. "
                "Install it with: uv pip install opencv-python-headless"
            ) from exc

        from PIL import Image

        tmp_path: str | None = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as tmp:
                tmp.write(video_bytes)
                tmp_path = tmp.name

            cap = cv2.VideoCapture(tmp_path)
            if not cap.isOpened():
                raise RuntimeError("Could not open video file — unsupported format or corrupt data")

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            target_frame = max(0, int(total_frames * position))
            cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)

            ret, frame = cap.read()
            cap.release()

            if not ret or frame is None:
                raise RuntimeError(
                    f"Could not read frame at position {position:.0%} "
                    f"(frame {target_frame}/{total_frames})"
                )

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            buf = BytesIO()
            img.save(buf, format="JPEG", quality=90, optimize=True)
            return buf.getvalue()

        finally:
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

    async def extract_frame_at_async(
        self, video_bytes: bytes, position: float = 0.10
    ) -> bytes:
        """Async wrapper around extract_frame_at() — offloads to a thread executor.

        Use this in FastAPI routes. The event loop is never blocked.

        Parameters
        ----------
        video_bytes:
            Raw bytes of the video file.
        position:
            Fractional position (0.0–1.0). Defaults to 0.10 (10%).

        Returns
        -------
        bytes
            JPEG-encoded bytes of the extracted frame.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.extract_frame_at, video_bytes, position
        )

    # ------------------------------------------------------------------
    # Cloud upload
    # ------------------------------------------------------------------

    async def upload_video_async(
        self,
        video_bytes: bytes,
        dest_uri: str,
        content_type: str = "video/mp4",
    ) -> str:
        """Upload video bytes to cloud storage and return the permanent public URL.

        The upload uses the BackendRouter's retry policy and the SupabaseBackend's
        600-second timeout, so large files (up to 500MB) are handled safely.

        Parameters
        ----------
        video_bytes:
            Raw bytes of the video file.
        dest_uri:
            Full cloud storage URI including filename.
            e.g. ``"supabase://podcast-assets/{user_id}/{uuid}/video.mp4"``
        content_type:
            MIME type of the video. Defaults to ``"video/mp4"``.

        Returns
        -------
        str
            Permanent public URL of the uploaded video.
        """
        await self.cloud_write_async(dest_uri, video_bytes, content_type=content_type)
        return await self.cloud_get_public_url_async(dest_uri)

    def upload_video(
        self,
        video_bytes: bytes,
        dest_uri: str,
        content_type: str = "video/mp4",
    ) -> str:
        """Synchronous version of upload_video_async(). Use in scripts/tests."""
        self.cloud_write(dest_uri, video_bytes, content_type=content_type)
        return self.cloud_get_public_url(dest_uri)
