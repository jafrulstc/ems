"""
Abstract storage interface.

All file storage operations are channeled through this ABC.
Concrete implementations (S3, MinIO, local) simply satisfy this contract,
enabling zero-code-change swaps between environments.
"""
from abc import ABC, abstractmethod


class StorageService(ABC):
    """
    Abstract base class for object storage backends.

    Implementations must be async-safe (use asyncio-compatible clients or
    run blocking calls in a thread-pool executor).
    """

    @abstractmethod
    async def upload_file(self, file: bytes, path: str, content_type: str = "application/octet-stream") -> str:
        """
        Upload raw bytes to the given storage path.

        Returns
        -------
        str
            The canonical path / key of the uploaded object.
        """
        ...

    @abstractmethod
    async def delete_file(self, path: str) -> bool:
        """
        Delete the object at `path`.

        Returns
        -------
        bool
            True if the object was deleted, False if it did not exist.
        """
        ...

    @abstractmethod
    async def get_presigned_url(self, path: str, expires: int = 3600) -> str:
        """
        Generate a time-limited presigned URL for direct client access.

        Parameters
        ----------
        path : str
            Object key / path inside the bucket.
        expires : int
            URL lifetime in seconds (default 1 h).

        Returns
        -------
        str
            The presigned URL string.
        """
        ...
