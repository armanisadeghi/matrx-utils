from abc import ABC, abstractmethod


class StorageBackend(ABC):
    """Abstract base for all cloud/remote storage backends.

    Each backend must be self-configuring from environment variables and
    must report whether it is ready via `is_configured()` before any I/O
    is attempted. All path arguments are backend-native (e.g. "bucket/key"
    for S3, "bucket/path" for Supabase).
    """

    @abstractmethod
    def is_configured(self) -> bool:
        """Return True if all required credentials/settings are present."""

    @abstractmethod
    def read(self, path: str) -> bytes:
        """Read and return the raw bytes at *path*."""

    @abstractmethod
    def write(self, path: str, content: bytes | str) -> bool:
        """Write *content* to *path*, overwriting if it already exists."""

    @abstractmethod
    def append(self, path: str, content: bytes | str) -> bool:
        """Append *content* to the object at *path*.

        For object stores that do not natively support appending, the
        existing object is downloaded, the new content is concatenated,
        and the result is re-uploaded atomically.
        """

    @abstractmethod
    def delete(self, path: str) -> bool:
        """Delete the object at *path*. Returns True on success."""

    @abstractmethod
    def get_url(self, path: str, expires_in: int = 3600) -> str:
        """Return a time-limited or permanent URL for *path*.

        *expires_in* is in seconds. For backends that produce permanent
        public URLs (e.g. a public server endpoint) this parameter is
        ignored.
        """

    @abstractmethod
    def list_files(self, prefix: str = "") -> list[str]:
        """Return a list of object keys/paths that start with *prefix*."""

    def _require_configured(self) -> None:
        if not self.is_configured():
            raise RuntimeError(
                f"{self.__class__.__name__} is not configured. "
                "Check that all required environment variables are set."
            )
