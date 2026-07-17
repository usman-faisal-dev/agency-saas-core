"""
Abstract storage provider interface.

All storage backends (R2, S3, local disk, etc.) implement this contract.
The upload endpoint and service layer depend only on this interface —
swapping backends is a config change in factory.py, not a rewrite.
"""
from abc import ABC, abstractmethod


class StorageProvider(ABC):
    """Contract for file-storage backends."""

    @abstractmethod
    def upload(self, key: str, data: bytes, content_type: str) -> str:
        """
        Upload `data` under `key` and return the public URL.

        Args:
            key: Object key / path within the bucket (e.g. "logos/abc/uuid.png").
            data: Raw file bytes.
            content_type: MIME type (e.g. "image/png").

        Returns:
            Public URL where the file can be fetched.
        """

    @abstractmethod
    def delete(self, key: str) -> None:
        """
        Delete the object at `key`.

        Implementations should be idempotent — deleting a missing key
        should not raise.
        """
