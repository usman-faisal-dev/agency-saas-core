"""
Storage module — convenience helpers for logo uploads.

Usage from API endpoints:
    from app.storage import upload_logo, delete_logo

    url = upload_logo(file_bytes, "logo.png", "image/png", org_id)
    delete_logo(key)
"""
import uuid
from pathlib import PurePosixPath

from app.storage.factory import get_storage

# Accepted MIME types → file extension mapping
ALLOWED_IMAGE_TYPES: dict[str, str] = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/webp": "webp",
}


def upload_logo(data: bytes, filename: str, content_type: str, org_id: str) -> str:
    """
    Upload a logo file and return its public URL.

    The key is namespaced by org_id for tenant isolation:
        logos/{org_id}/{uuid}.{ext}

    Args:
        data: Raw file bytes (already validated as a real image).
        filename: Original filename (used only for extension fallback).
        content_type: MIME type resolved by Pillow (authoritative).
        org_id: Authenticated org's ID (from FastAPI dependency, never client-supplied).
    """
    ext = (
        ALLOWED_IMAGE_TYPES.get(content_type)
        or PurePosixPath(filename).suffix.lstrip(".")
        or "bin"
    )
    key = f"logos/{org_id}/{uuid.uuid4()}.{ext}"
    return get_storage().upload(key, data, content_type)


def delete_logo(key: str) -> None:
    """Delete a logo object from storage. Idempotent."""
    get_storage().delete(key)
