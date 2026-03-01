from abc import ABC, abstractmethod


class StorageBackend(ABC):
    """Abstract base for all cloud/remote storage backends.

    Every backend implements both a synchronous and an asynchronous API
    with identical signatures. The sync API is safe to call from scripts
    and tests. The async API must be used inside FastAPI routes and any
    other async context to avoid blocking the event loop.

    S3Backend async methods run the synchronous boto3 calls in a thread-pool
    executor (run_in_executor) — genuinely non-blocking to the event loop,
    the standard pattern for boto3 in async applications.

    SupabaseBackend async methods use supabase-py's native AsyncClient.

    ServerBackend async methods use httpx.AsyncClient.
    """

    # ------------------------------------------------------------------
    # Synchronous API
    # ------------------------------------------------------------------

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
        """Append *content* to the object at *path*."""

    @abstractmethod
    def delete(self, path: str) -> bool:
        """Delete the object at *path*. Returns True on success."""

    @abstractmethod
    def get_url(self, path: str, expires_in: int = 3600) -> str:
        """Return a time-limited or permanent URL for *path*."""

    @abstractmethod
    def list_files(self, prefix: str = "") -> list[str]:
        """Return a list of object keys/paths that start with *prefix*."""

    # ------------------------------------------------------------------
    # Asynchronous API
    # ------------------------------------------------------------------

    @abstractmethod
    async def read_async(self, path: str) -> bytes:
        """Async version of read()."""

    @abstractmethod
    async def write_async(self, path: str, content: bytes | str) -> bool:
        """Async version of write()."""

    @abstractmethod
    async def append_async(self, path: str, content: bytes | str) -> bool:
        """Async version of append()."""

    @abstractmethod
    async def delete_async(self, path: str) -> bool:
        """Async version of delete()."""

    @abstractmethod
    async def get_url_async(self, path: str, expires_in: int = 3600) -> str:
        """Async version of get_url()."""

    @abstractmethod
    async def list_files_async(self, prefix: str = "") -> list[str]:
        """Async version of list_files()."""

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _require_configured(self) -> None:
        if not self.is_configured():
            raise RuntimeError(
                f"{self.__class__.__name__} is not configured. "
                "Check that all required environment variables are set."
            )
