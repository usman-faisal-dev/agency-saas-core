"""
Cloudflare R2 storage provider.

R2 exposes the S3-compatible API, so we use boto3 with a custom endpoint URL.
No egress fees and a generous free tier make it ideal for MVP asset storage.
"""

import logging

import boto3
from botocore.client import Config

from app.config import get_settings
from app.storage.interface import StorageProvider

logger = logging.getLogger(__name__)


class R2StorageProvider(StorageProvider):
    """Upload / delete files via Cloudflare R2's S3-compatible API."""

    def __init__(self) -> None:
        settings = get_settings()
        missing = [
            name
            for name, val in [
                ("R2_ACCOUNT_ID", settings.r2_account_id),
                ("R2_ACCESS_KEY_ID", settings.r2_access_key_id),
                ("R2_SECRET_ACCESS_KEY", settings.r2_secret_access_key),
                ("R2_PUBLIC_URL", settings.r2_public_url),
            ]
            if not val
        ]
        if missing:
            raise RuntimeError(
                f"R2 storage is not fully configured. Missing: {', '.join(missing)}. "
                "Set all R2_* env vars — R2_PUBLIC_URL must be a publicly-accessible "
                "URL (custom domain or R2 dev URL) where uploaded files can be fetched."
            )

        self._bucket = settings.r2_bucket_name
        endpoint_url = f"https://{settings.r2_account_id}.r2.cloudflarestorage.com"

        self._s3 = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=settings.r2_access_key_id,
            aws_secret_access_key=settings.r2_secret_access_key,
            config=Config(signature_version="s3v4"),
            region_name="auto",
        )

        self._public_base = settings.r2_public_url.rstrip("/")

    def upload(self, key: str, data: bytes, content_type: str) -> str:
        self._s3.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        url = f"{self._public_base}/{key}"
        logger.info("Uploaded %s → %s (%d bytes)", key, url, len(data))
        return url

    def delete(self, key: str) -> None:
        self._s3.delete_object(Bucket=self._bucket, Key=key)
        logger.info("Deleted %s from bucket %s", key, self._bucket)
