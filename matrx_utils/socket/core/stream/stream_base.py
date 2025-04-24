from abc import ABC, abstractmethod
from typing import Any, Optional
from matrx_utils import vcprint
import datetime
import uuid
import enum

ERROR = True
INFO = True
DEBUG = True
VERBOSE = False

VALID_INFO_OPTIONS = {
    "update",
    "confirm",
    "completed",
    "retry",
    "fatal_error",
    "non_fatal_error",
}


class StreamInterface(ABC):
    """Base abstract class for all stream handlers ensuring consistent interface and core behavior."""

    def __init__(self, event_name: str):
        """Initialize with required event_name and set up common attributes."""
        self.event_name = event_name
        self._is_ended = False
        self._init_message()

    def _init_message(self):
        """Log initialization message."""
        vcprint(
            verbose=VERBOSE,
            data=f"[{self.__class__.__name__} Init] Stream handler created for event: {self.event_name}",
            color="green",
        )

    @abstractmethod
    async def send_chunk(self, chunk: str):
        """Send a chunk of data through the stream."""
        pass

    @abstractmethod
    async def send_object(self, obj: Any):
        """Send a complete object and end the stream."""
        pass

    @abstractmethod
    async def send_info(self, info_type: str, message: str, data: Optional[Any] = None):
        """Send informational message with type, message, and optional data."""
        if info_type not in VALID_INFO_OPTIONS:
            raise ValueError(f"Invalid info_type: {info_type}. Must be one of: {VALID_INFO_OPTIONS}")
        if not isinstance(message, str) or not message.strip():
            raise ValueError("message must be a non-empty string")

    @abstractmethod
    async def send_image(self, image_data: bytes, mime_type: str):
        """Send binary image data with its MIME type through the stream."""
        if not isinstance(image_data, bytes):
            raise ValueError("image_data must be bytes")
        if not isinstance(mime_type, str) or not mime_type.strip():
            raise ValueError("mime_type must be a non-empty string")

    async def end_stream(self):
        """Mark the stream as ended and perform cleanup."""
        if not self._is_ended:
            self._is_ended = True
            vcprint(
                verbose=INFO,
                data=f"\n[{self.__class__.__name__} End Stream] Stream ended for event: {self.event_name}\n",
                color="green",
            )

    async def mic_check(self, message: str) -> None:
        """Send a test message to verify stream functionality."""
        if not isinstance(message, str) or not message.strip():
            raise ValueError("message must be a non-empty string")
        vcprint(
            verbose=INFO,
            data=f"[{self.__class__.__name__} Mic Check] Sending test for event: {self.event_name}",
            color="blue",
        )
        await self.send_chunk(message)

    async def fatal_error(self, error_message) -> None:
        """Handle a fatal error and end the stream."""
        # Format dict errors into a simple string
        if isinstance(error_message, dict):
            formatted_message = ""
            for key, value in error_message.items():
                formatted_message += f"{key}: {value}\n"
            error_message = formatted_message.strip()

        # Validate we have a non-empty string
        if not isinstance(error_message, str) or not error_message.strip():
            raise ValueError("error_message must be a non-empty string")

        await self.send_info("fatal_error", error_message)
        await self.end_stream()

    async def non_fatal_error(self, error_message: str):
        """Handle a non-fatal error without ending the stream."""
        if not isinstance(error_message, str) or not error_message.strip():
            raise ValueError("error_message must be a non-empty string")
        await self.send_info("non_fatal_error", error_message)

    def ensure_not_ended(self):
        """Raise an exception if the stream has already ended."""
        if self._is_ended:
            message = f"Stream handler for event '{self.event_name}' has already ended"
            vcprint(verbose=ERROR, data=message, color="red")
            raise RuntimeError(message)

    def make_json_serializable(self,data):
        """Recursively converts data to a JSON-serializable format."""
        if data is None:
            return None
        elif isinstance(data, (bool, int, float, str)):
            return data
        elif isinstance(data, (datetime.datetime, datetime.date)):
            return data.isoformat()
        elif isinstance(data, uuid.UUID):
            return str(data)
        elif isinstance(data, enum.Enum):
            return data.name
        elif isinstance(data, (set, tuple)):
            return [self.make_json_serializable(item) for item in data]
        elif isinstance(data, dict):
            return {key: self.make_json_serializable(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.make_json_serializable(item) for item in data]
        elif hasattr(data, "__str__"):
            return str(data)
        return data
