from matrx_utils.socket.core.stream.stream_base import StreamInterface
from typing import Any, Optional
import traceback
import os
import mimetypes
from matrx_utils import print_link, vcprint
from matrx_utils.conf import settings


IMAGE_DIR = os.path.join(settings.TEMP_DIR, "images")
os.makedirs(IMAGE_DIR, exist_ok=True)


class PrintStreamHandler(StreamInterface):
    """Print-based stream handler for testing, fully compatible with SocketStreamHandler."""

    async def send_chunk(self, chunk: str) -> None:
        try:
            if not isinstance(chunk, str):
                raise ValueError("chunk must be a string")
            vcprint(data=chunk, color="blue", chunks=True)
        except Exception as e:
            self._handle_exception("send_chunk", e)

    async def send_object(self, obj: Any) -> None:
        try:
            vcprint(
                data=obj,
                pretty=True,
                title="[PrintStreamHandler Object]",
                color="green",
            )
        except Exception as e:
            self._handle_exception("send_object", e)

    async def send_info(self, info_type: str, message: str, data: Optional[Any] = None) -> None:
        try:
            await super().send_info(info_type, message, data)  # Validate inputs
            title = f"Info [{info_type}]"
            payload = message
            if data is not None:
                payload = {"message": message, "data": data}
            vcprint(data=payload, title=title, color="yellow", pretty=True)
        except Exception as e:
            self._handle_exception("send_info", e)

    async def send_image(self, image_data: bytes, mime_type: str) -> None:
        """Save image data to a local file and print confirmation."""
        try:
            file_extension = mimetypes.guess_extension(mime_type) or ".bin"
            file_name = f"{IMAGE_DIR}/test_image_{len(os.listdir(IMAGE_DIR))}{file_extension}"
            with open(file_name, "wb") as f:
                f.write(image_data)
            print()
            vcprint("Image saved locally", color="magenta")
            print_link(file_name)
            print()
        except Exception as e:
            self._handle_exception("send_image", e)

    def _handle_exception(self, method_name: str, exception: Exception) -> None:
        """Handle exceptions gracefully with formatted output."""
        error_msg = f"Error in {method_name}: {str(exception)}"
        traceback_str = "".join(traceback.format_tb(exception.__traceback__))
        vcprint(
            data=f"{error_msg}\nTraceback:\n{traceback_str}",
            title="Exception",
            color="red",
            pretty=True,
        )
