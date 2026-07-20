"""
Storage provider factory.

Returns a cached singleton StorageProvider instance based on current settings.
Currently always returns R2StorageProvider; swap the import here to change backends.
"""

from functools import lru_cache

from app.storage.interface import StorageProvider


@lru_cache
def get_storage() -> StorageProvider:
    """Return a cached storage provider singleton."""
    from app.storage.r2_provider import R2StorageProvider

    return R2StorageProvider()
