from __future__ import annotations

import asyncio
import base64
from io import BytesIO
from pathlib import Path
from typing import TypedDict

from PIL import Image, ImageEnhance

from matrx_utils.file_handling.file_handler import FileHandler


# ---------------------------------------------------------------------------
# Variant type and preset collections
# ---------------------------------------------------------------------------

class ImageVariant(TypedDict):
    key: str      # Key in the returned dict, e.g. "cover_url"
    suffix: str   # Filename suffix, e.g. "cover"
    width: int
    height: int
    quality: int  # JPEG/WEBP quality 1-95
    format: str   # "JPEG" | "PNG" | "WEBP"


# Podcast / Audio — Apple Podcasts & Spotify recommended 3000×3000; 1400 kept
# as legacy SD variant. OG covers Twitter / LinkedIn / Facebook. Thumb for UI.
PODCAST_VARIANTS: list[ImageVariant] = [
    {"key": "cover_url",     "suffix": "cover",    "width": 3000, "height": 3000, "quality": 90, "format": "JPEG"},
    {"key": "cover_sd_url",  "suffix": "cover_sd", "width": 1400, "height": 1400, "quality": 85, "format": "JPEG"},
    {"key": "og_url",        "suffix": "og",       "width": 1200, "height": 630,  "quality": 85, "format": "JPEG"},
    {"key": "thumbnail_url", "suffix": "thumb",    "width": 400,  "height": 400,  "quality": 80, "format": "JPEG"},
]

# Social media — OG/Twitter card, Instagram square/portrait/story, YouTube thumbnail
SOCIAL_VARIANTS: list[ImageVariant] = [
    {"key": "og_url",           "suffix": "og",       "width": 1200, "height": 630,  "quality": 85, "format": "JPEG"},
    {"key": "square_url",       "suffix": "sq",       "width": 1080, "height": 1080, "quality": 85, "format": "JPEG"},
    {"key": "portrait_url",     "suffix": "portrait", "width": 1080, "height": 1350, "quality": 85, "format": "JPEG"},
    {"key": "story_url",        "suffix": "story",    "width": 1080, "height": 1920, "quality": 85, "format": "JPEG"},
    {"key": "yt_thumbnail_url", "suffix": "yt_thumb", "width": 1280, "height": 720,  "quality": 85, "format": "JPEG"},
]

# Web — hero banner, OG/SEO, content card, Apple touch icon, PWA manifest icon, UI thumbnail
WEB_VARIANTS: list[ImageVariant] = [
    {"key": "hero_url",       "suffix": "hero",       "width": 1920, "height": 1080, "quality": 85, "format": "JPEG"},
    {"key": "og_url",         "suffix": "og",         "width": 1200, "height": 630,  "quality": 85, "format": "JPEG"},
    {"key": "card_url",       "suffix": "card",       "width": 800,  "height": 450,  "quality": 85, "format": "JPEG"},
    {"key": "touch_icon_url", "suffix": "touch_icon", "width": 180,  "height": 180,  "quality": 90, "format": "PNG"},
    {"key": "pwa_icon_url",   "suffix": "pwa_icon",   "width": 512,  "height": 512,  "quality": 90, "format": "PNG"},
    {"key": "thumbnail_url",  "suffix": "thumb",      "width": 400,  "height": 400,  "quality": 80, "format": "JPEG"},
]

# Email — standard 600px-wide header + small inline square
EMAIL_VARIANTS: list[ImageVariant] = [
    {"key": "header_url", "suffix": "email_header", "width": 600, "height": 200, "quality": 85, "format": "JPEG"},
    {"key": "square_url", "suffix": "email_sq",     "width": 200, "height": 200, "quality": 85, "format": "JPEG"},
]

# Full set — use when you want every variant in one call
ALL_VARIANTS: list[ImageVariant] = PODCAST_VARIANTS + SOCIAL_VARIANTS + WEB_VARIANTS


class ImageHandler(FileHandler):
    def __init__(self, app_name, batch_print=False):
        super().__init__(app_name, batch_print=batch_print)

    # Custom Methods
    def custom_read_image(self, path):
        try:
            with Image.open(path) as img:
                self._print_link(path=path, message="Read Image file")
                return img.copy()

        except Exception as e:
            print(f"Error reading image from {path}: {str(e)}")
            self._print_link(path=path, message=f"READ IMAGE ERROR {str(e)}", color="red")
            return None

    def custom_write_image(self, path, image):
        try:
            self._ensure_directory(Path(path))
            image.save(path)
            self._print_link(path=path, message="Image File Saved")
            return True
        except Exception as e:
            self._print_link(path=path, message="Error saving Image", color="red")
            print(f"Error saving image to {path}: {str(e)}")
            return False

    def custom_append_image(self, path, image, position=(0, 0)):
        try:
            base_image = self.custom_read_image(path)
            if base_image:
                base_image.paste(image, position)
                return self.custom_write_image(path, base_image)
            return False
        except Exception as e:
            print(f"Error appending image to {path}: {str(e)}")
            return False

    def custom_delete_image(self, path):
        return self.delete(path)

    # Core Methods
    def read_image(self, root, path):
        full_path = self._get_full_path(root, path)
        return self.custom_read_image(full_path)

    def write_image(self, root, path, image):
        full_path = self._get_full_path(root, path)
        return self.custom_write_image(full_path, image)

    def append_image(self, root, path, image, position=(0, 0)):
        full_path = self._get_full_path(root, path)
        return self.custom_append_image(full_path, image, position)

    def delete_image(self, root, path):
        full_path = self._get_full_path(root, path)
        return self.custom_delete_image(full_path)

    # File Type-specific Methods
    def get_image_size(self, root, path):
        image = self.read_image(root, path)
        return image.size if image else None

    def get_image_format(self, root, path):
        image = self.read_image(root, path)
        return image.format if image else None

    def get_image_mode(self, root, path):
        image = self.read_image(root, path)
        return image.mode if image else None

    def resize_image(self, root, path, width, height):
        image = self.read_image(root, path)
        if image:
            resized_image = image.resize((width, height))
            return self.write_image(root, path, resized_image)
        return False

    def convert_image_format(self, root, path, target_format):
        image = self.read_image(root, path)
        if image:
            target_path = Path(path).with_suffix(f'.{target_format.lower()}')
            return self.write_image(root, target_path, image)
        return False

    def crop_image(self, root, path, left, top, right, bottom):
        image = self.read_image(root, path)
        if image:
            cropped_image = image.crop((left, top, right, bottom))
            return self.write_image(root, path, cropped_image)
        return False

    def rotate_image(self, root, path, angle):
        image = self.read_image(root, path)
        if image:
            rotated_image = image.rotate(angle)
            return self.write_image(root, path, rotated_image)
        return False

    def merge_images(self, root, path_list, output_path):
        loaded = [self.read_image(root, path) for path in path_list]
        images: list[Image.Image] = [img for img in loaded if img is not None]
        if not images or len(images) != len(loaded):
            return False
        widths, heights = zip(*(img.size for img in images))
        total_width = sum(widths)
        max_height = max(heights)
        merged_image = Image.new('RGB', (total_width, max_height))
        x_offset = 0
        for img in images:
            merged_image.paste(img, (x_offset, 0))
            x_offset += img.width
        return self.write_image(root, output_path, merged_image)

    def add_watermark(self, root, path, watermark_path, position=(0, 0), opacity=128):
        image = self.read_image(root, path)
        watermark = self.read_image(root, watermark_path)
        if image and watermark:
            if watermark.mode != 'RGBA':
                watermark = watermark.convert('RGBA')
            alpha = watermark.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(opacity / 255.0)
            watermark.putalpha(alpha)
            image.paste(watermark, position, watermark)
            return self.write_image(root, path, image)
        return False

    def adjust_brightness(self, root, path, factor):
        image = self.read_image(root, path)
        if image:
            enhancer = ImageEnhance.Brightness(image)
            brightened_image = enhancer.enhance(factor)
            return self.write_image(root, path, brightened_image)
        return False

    def convert_to_grayscale(self, root, path):
        image = self.read_image(root, path)
        if image:
            grayscale_image = image.convert('L')
            return self.write_image(root, path, grayscale_image)
        return False

    def create_thumbnail(self, root, path, size):
        image = self.read_image(root, path)
        if image:
            image.thumbnail(size)
            return self.write_image(root, path, image)
        return False

    def flip_image(self, root, path, direction='horizontal'):
        image = self.read_image(root, path)
        if image:
            if direction == 'horizontal':
                flipped_image = image.transpose(Image.FLIP_LEFT_RIGHT)
            elif direction == 'vertical':
                flipped_image = image.transpose(Image.FLIP_TOP_BOTTOM)
            else:
                print(f"Invalid flip direction: {direction}. Use 'horizontal' or 'vertical'.")
                return False
            return self.write_image(root, path, flipped_image)
        return False

    def custom_base64_to_png(self, base64_string, path):
        try:
            # Remove data:image/... prefix if present
            if base64_string.startswith("data:image"):
                base64_string = base64_string.split(",")[1]

            # Ensure path has .png extension
            path = Path(path)
            if path.suffix.lower() != ".png":
                path = path.with_suffix(".png")

            # Simple approach: decode and write directly
            self._ensure_directory(path)
            with open(path, "wb") as f:
                f.write(base64.b64decode(base64_string))

            self._print_link(path=path, message="Base64 converted to PNG")
            return True

        except Exception as e:
            print(f"Error converting base64 to PNG at {path}: {str(e)}")
            self._print_link(
                path=path, message=f"BASE64 TO PNG ERROR {str(e)}", color="red"
            )
            return False

    def custom_base64_to_webp(self, base64_string, path):
        try:
            # Remove data:image/... prefix if present
            if base64_string.startswith("data:image"):
                base64_string = base64_string.split(",")[1]

            # For WebP, we need PIL to convert from the original format
            image_data = base64.b64decode(base64_string)
            image = Image.open(BytesIO(image_data))

            # Ensure path has .webp extension
            path = Path(path)
            if path.suffix.lower() != ".webp":
                path = path.with_suffix(".webp")

            # Save as WebP
            self._ensure_directory(path)
            image.save(path, "WEBP", quality=85)
            self._print_link(path=path, message="Base64 converted to WebP")
            return True

        except Exception as e:
            print(f"Error converting base64 to WebP at {path}: {str(e)}")
            self._print_link(
                path=path, message=f"BASE64 TO WEBP ERROR {str(e)}", color="red"
            )
            return False

    def base64_to_png(self, root, path, base64_string):
        full_path = self._get_full_path(root, path)
        return self.custom_base64_to_png(base64_string, full_path)

    def base64_to_webp(self, root, path, base64_string):
        full_path = self._get_full_path(root, path)
        return self.custom_base64_to_webp(base64_string, full_path)

    # ------------------------------------------------------------------
    # Cloud I/O — require FileManager construction (CloudMixin)
    # ------------------------------------------------------------------

    def base64_to_cloud(self, base64_string: str, dest_uri: str) -> bool:
        """Decode a base64 image and write it directly to cloud storage.

        Accepts base64 strings with or without the ``data:image/...;base64,``
        prefix. Writes raw bytes — no format conversion — to any configured
        backend via *dest_uri*.

        Parameters
        ----------
        base64_string:
            Base64-encoded image data, optionally prefixed with a data URI
            header (``data:image/png;base64,...``).
        dest_uri:
            Full cloud storage URI, e.g.
            ``"supabase://bucket/users/123/avatar.png"``
            ``"s3://bucket/generated/image.webp"``

        Examples
        --------
            # From an OpenAI image generation response
            handler.base64_to_cloud(result.data[0].b64_json, "s3://bucket/out.png")

            # From a multipart form upload (already base64-encoded client-side)
            handler.base64_to_cloud(form_data.image_b64, "supabase://media/img.jpg")
        """
        try:
            if base64_string.startswith("data:image"):
                base64_string = base64_string.split(",", 1)[1]
            file_bytes = base64.b64decode(base64_string)
            return self.cloud_write(dest_uri, file_bytes)
        except Exception as e:
            print(f"[ImageHandler] base64_to_cloud failed for {dest_uri}: {e}")
            return False

    async def base64_to_cloud_async(self, base64_string: str, dest_uri: str) -> bool:
        """Async version of base64_to_cloud(). Use this in FastAPI routes."""
        try:
            if base64_string.startswith("data:image"):
                base64_string = base64_string.split(",", 1)[1]
            file_bytes = base64.b64decode(base64_string)
            return await self.cloud_write_async(dest_uri, file_bytes)
        except Exception as e:
            print(f"[ImageHandler] base64_to_cloud_async failed for {dest_uri}: {e}")
            return False

    def read_image_from_cloud(self, uri_or_url: str) -> "Image.Image | None":
        """Read an image from any cloud URI or URL and return a PIL Image.

        Accepts native URIs (``s3://``, ``supabase://``), public HTTPS URLs,
        and signed/expired URLs. Reads via server-side credentials so token
        expiry is irrelevant.

        Parameters
        ----------
        uri_or_url:
            Any cloud storage URI or URL pointing to an image file.

        Examples
        --------
            img = handler.read_image_from_cloud("supabase://bucket/avatar.png")
            img = handler.read_image_from_cloud(signed_url_from_client)
        """
        try:
            raw = self.cloud_read_url(uri_or_url)
            return Image.open(BytesIO(raw))
        except Exception as e:
            print(f"[ImageHandler] read_image_from_cloud failed for {uri_or_url}: {e}")
            return None

    async def read_image_from_cloud_async(self, uri_or_url: str) -> "Image.Image | None":
        """Async version of read_image_from_cloud(). Use this in FastAPI routes."""
        try:
            raw = await self.cloud_read_url_async(uri_or_url)
            return Image.open(BytesIO(raw))
        except Exception as e:
            print(f"[ImageHandler] read_image_from_cloud_async failed for {uri_or_url}: {e}")
            return None

    def write_image_to_cloud(self, image: "Image.Image", dest_uri: str, fmt: str = "PNG") -> bool:
        """Encode a PIL Image and write it to cloud storage.

        Parameters
        ----------
        image:
            A PIL Image object to upload.
        dest_uri:
            Full cloud storage URI (s3://, supabase://, server://).
        fmt:
            Pillow format string used for encoding, e.g. ``"PNG"``, ``"WEBP"``,
            ``"JPEG"``. Defaults to ``"PNG"``.

        Examples
        --------
            handler.write_image_to_cloud(resized_img, "s3://bucket/thumb.webp", fmt="WEBP")
        """
        try:
            buf = BytesIO()
            image.save(buf, format=fmt)
            return self.cloud_write(dest_uri, buf.getvalue())
        except Exception as e:
            print(f"[ImageHandler] write_image_to_cloud failed for {dest_uri}: {e}")
            return False

    async def write_image_to_cloud_async(self, image: "Image.Image", dest_uri: str, fmt: str = "PNG") -> bool:
        """Async version of write_image_to_cloud(). Use this in FastAPI routes."""
        try:
            buf = BytesIO()
            image.save(buf, format=fmt)
            return await self.cloud_write_async(dest_uri, buf.getvalue())
        except Exception as e:
            print(f"[ImageHandler] write_image_to_cloud_async failed for {dest_uri}: {e}")
            return False

    # ------------------------------------------------------------------
    # Cover-crop resize and JPEG normalization
    # ------------------------------------------------------------------

    @staticmethod
    def resize_cover(image: Image.Image, width: int, height: int) -> Image.Image:
        """Scale and center-crop to exact dimensions (CSS object-fit: cover).

        The image is scaled so that it completely fills the target box
        (no empty space), then the excess is trimmed from both sides equally.
        Uses LANCZOS resampling for maximum quality.
        """
        src_ratio = image.width / image.height
        dst_ratio = width / height
        if src_ratio > dst_ratio:
            # Source is wider than target — scale by height, crop width
            new_h = height
            new_w = int(image.width * (height / image.height))
        else:
            # Source is taller than target — scale by width, crop height
            new_w = width
            new_h = int(image.height * (width / image.width))
        image = image.resize((new_w, new_h), Image.LANCZOS)
        left = (image.width - width) // 2
        top = (image.height - height) // 2
        return image.crop((left, top, left + width, top + height))

    @staticmethod
    def normalize_for_export(image: Image.Image, fmt: str) -> Image.Image:
        """Ensure image mode is compatible with the target format.

        JPEG and WEBP cannot encode alpha channels — RGBA images are composited
        onto a white background and converted to RGB. Non-RGB modes for JPEG
        are also converted. PNG passes through unchanged to preserve alpha.
        """
        fmt_upper = fmt.upper()
        if fmt_upper in ("JPEG", "WEBP"):
            if image.mode == "RGBA":
                bg = Image.new("RGB", image.size, (255, 255, 255))
                bg.paste(image, mask=image.split()[3])
                return bg
            if image.mode != "RGB":
                return image.convert("RGB")
        return image

    def _render_variants(
        self, image_bytes: bytes, variants: list[ImageVariant]
    ) -> list[tuple[str, str, str, bytes]]:
        """CPU-bound: open source image and produce all variant byte buffers.

        Returns a list of (key, suffix, format, encoded_bytes) tuples.
        Runs synchronously — always call from a thread executor in async contexts.
        """
        img = Image.open(BytesIO(image_bytes))
        results: list[tuple[str, str, str, bytes]] = []
        for v in variants:
            resized = self.resize_cover(img, v["width"], v["height"])
            normalized = self.normalize_for_export(resized, v["format"])
            buf = BytesIO()
            save_kwargs: dict = {"format": v["format"]}
            if v["format"].upper() in ("JPEG", "WEBP"):
                save_kwargs["quality"] = v.get("quality", 85)
                save_kwargs["optimize"] = True
            normalized.save(buf, **save_kwargs)
            results.append((v["key"], v["suffix"], v["format"], buf.getvalue()))
        return results

    def process_variants(
        self,
        image_bytes: bytes,
        variants: list[ImageVariant],
        folder_uri: str,
    ) -> dict[str, str]:
        """Resize image to all variants, upload each to cloud, return public URLs.

        Synchronous version — use process_variants_async() in FastAPI routes.

        Parameters
        ----------
        image_bytes:
            Raw bytes of the source image (any PIL-supported format).
        variants:
            List of ImageVariant dicts. Use PODCAST_VARIANTS, SOCIAL_VARIANTS,
            WEB_VARIANTS, EMAIL_VARIANTS, or a custom list.
        folder_uri:
            Cloud folder URI, e.g. ``"supabase://podcast-assets/{user_id}/{uuid}"``.
            Each variant is uploaded as ``{folder_uri}/{suffix}.{ext}``.

        Returns
        -------
        dict[str, str]
            Mapping of variant key to permanent public URL.
            e.g. ``{"cover_url": "https://...", "og_url": "https://..."}``
        """
        rendered = self._render_variants(image_bytes, variants)
        urls: dict[str, str] = {}
        for key, suffix, fmt, data in rendered:
            ext = "jpg" if fmt.upper() == "JPEG" else fmt.lower()
            dest_uri = f"{folder_uri.rstrip('/')}/{suffix}.{ext}"
            mime = f"image/jpeg" if ext == "jpg" else f"image/{ext}"
            self.cloud_write(dest_uri, data, content_type=mime)
            urls[key] = self.cloud_get_public_url(dest_uri)
        return urls

    async def process_variants_async(
        self,
        image_bytes: bytes,
        variants: list[ImageVariant],
        folder_uri: str,
    ) -> dict[str, str]:
        """Async version of process_variants(). Use this in FastAPI routes.

        CPU work (Pillow resizing) runs in a thread executor so the event loop
        is never blocked. Supabase uploads are fully async via AsyncClient.

        Parameters
        ----------
        image_bytes:
            Raw bytes of the source image (any PIL-supported format).
        variants:
            List of ImageVariant dicts. Use PODCAST_VARIANTS, SOCIAL_VARIANTS,
            WEB_VARIANTS, EMAIL_VARIANTS, or a custom list.
        folder_uri:
            Cloud folder URI, e.g. ``"supabase://podcast-assets/{user_id}/{uuid}"``.

        Returns
        -------
        dict[str, str]
            Mapping of variant key to permanent public URL.
        """
        loop = asyncio.get_event_loop()
        rendered = await loop.run_in_executor(
            None, self._render_variants, image_bytes, variants
        )
        urls: dict[str, str] = {}
        for key, suffix, fmt, data in rendered:
            ext = "jpg" if fmt.upper() == "JPEG" else fmt.lower()
            dest_uri = f"{folder_uri.rstrip('/')}/{suffix}.{ext}"
            mime = f"image/jpeg" if ext == "jpg" else f"image/{ext}"
            await self.cloud_write_async(dest_uri, data, content_type=mime)
            urls[key] = await self.cloud_get_public_url_async(dest_uri)
        return urls
