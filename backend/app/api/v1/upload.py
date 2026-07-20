"""
File upload API — logo upload endpoint.

Routes:
  POST /api/v1/upload/logo  → upload a logo image, return { "url": "..." }

Validation:
  1. Max size 2 MB (checked before reading full content).
  2. Content-based image validation via Pillow (reads actual image headers).
  3. SVG explicitly rejected — stored-XSS vector if served inline.

Supports optional client_id form field for client-scoped logo keys.
"""

import io
import logging

from fastapi import APIRouter, Depends, Form, UploadFile
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import NotFoundError, UnprocessableError
from app.dependencies import CurrentOrgId
from app.models.client import Client
from app.storage import upload_logo

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["upload"])

MAX_LOGO_SIZE = 2 * 1024 * 1024  # 2 MB

# Pillow reports these format names for valid images we accept
_ACCEPTED_PIL_FORMATS = {"PNG", "JPEG", "WEBP"}

# MIME type mapping from Pillow format names
_PIL_FORMAT_TO_MIME = {
    "PNG": "image/png",
    "JPEG": "image/jpeg",
    "WEBP": "image/webp",
}


class UploadResponse(BaseModel):
    url: str


@router.post("/logo", response_model=UploadResponse)
async def upload_logo_endpoint(
    logo: UploadFile,
    org_id: CurrentOrgId,
    client_id: str | None = Form(None),
    db: Session = Depends(get_db),
) -> UploadResponse:
    """
    Upload a logo image (agency or client).

    Accepts multipart/form-data with a file field named "logo" and an
    optional "client_id" field for client-scoped uploads.
    Returns the public URL of the uploaded file.
    """
    # If client_id provided, validate the client belongs to this org
    if client_id:
        client = db.query(Client).filter(Client.id == client_id, Client.org_id == org_id).first()
        if client is None:
            raise NotFoundError("Client not found")

    # --- Size check: read up to MAX + 1 byte to detect oversized uploads ---
    contents = await logo.read()
    if len(contents) > MAX_LOGO_SIZE:
        raise UnprocessableError(f"Logo must be under {MAX_LOGO_SIZE // (1024 * 1024)} MB")

    if len(contents) == 0:
        raise UnprocessableError("Uploaded file is empty")

    # --- Content-based image validation via Pillow ---
    try:
        img = Image.open(io.BytesIO(contents))
        img.verify()  # Confirms file is a valid, non-corrupt image
    except UnidentifiedImageError:
        raise UnprocessableError("File is not a valid image. Accepted formats: PNG, JPG, WebP.")
    except Exception:
        raise UnprocessableError("File is not a valid or supported image.")

    # Re-open after verify() (verify leaves the image in an unusable state)
    img = Image.open(io.BytesIO(contents))
    fmt = img.format

    # Reject SVG (and anything else not in our allowlist)
    if fmt not in _ACCEPTED_PIL_FORMATS:
        raise UnprocessableError(
            f"Unsupported image format. Accepted: PNG, JPG, WebP. Got: {fmt or 'unknown'}"
        )

    content_type = _PIL_FORMAT_TO_MIME[fmt]
    filename = logo.filename or "logo"

    url = upload_logo(contents, filename, content_type, org_id, client_id=client_id)
    logger.info("Logo uploaded for org %s (client=%s): %s", org_id, client_id, url)
    return UploadResponse(url=url)
