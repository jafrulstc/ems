"""
S3 / MinIO storage backend.

Uses boto3 in a thread-pool executor to keep the async event-loop unblocked.
Works against:
  - MinIO (local dev)  : set STORAGE_ENDPOINT_URL=http://localhost:9000
  - AWS S3 (prod)      : set STORAGE_ENDPOINT_URL to empty string or omit

Required env vars (loaded via app.config.Settings):
  STORAGE_ENDPOINT_URL, STORAGE_ACCESS_KEY, STORAGE_SECRET_KEY, STORAGE_BUCKET
"""
import asyncio
import logging
from functools import partial
from typing import Optional

import boto3
from botocore.exceptions import ClientError

from app.config import get_settings
from app.storage.interface import StorageService

logger = logging.getLogger(__name__)


class S3StorageService(StorageService):
    """Concrete boto3 implementation of StorageService."""

    def __init__(self) -> None:
        settings = get_settings()
        kwargs = {
            "aws_access_key_id": settings.STORAGE_ACCESS_KEY,
            "aws_secret_access_key": settings.STORAGE_SECRET_KEY,
        }
        if settings.STORAGE_ENDPOINT_URL:
            kwargs["endpoint_url"] = settings.STORAGE_ENDPOINT_URL

        self._client = boto3.client("s3", **kwargs)
        self._bucket = settings.STORAGE_BUCKET

    # ── Internal helper ───────────────────────────────────────────────────────

    async def _run_in_executor(self, func, *args, **kwargs):
        """Run a blocking boto3 call in the default thread-pool executor."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, partial(func, *args, **kwargs))

    # ── StorageService interface ───────────────────────────────────────────────

    async def upload_file(
        self,
        file: bytes,
        path: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        await self._run_in_executor(
            self._client.put_object,
            Bucket=self._bucket,
            Key=path,
            Body=file,
            ContentType=content_type,
        )
        logger.debug("Uploaded object: %s/%s", self._bucket, path)
        return path

    async def delete_file(self, path: str) -> bool:
        try:
            await self._run_in_executor(
                self._client.delete_object,
                Bucket=self._bucket,
                Key=path,
            )
            return True
        except ClientError as exc:
            logger.warning("Failed to delete object %s: %s", path, exc)
            return False

    async def get_presigned_url(self, path: str, expires: int = 3600) -> str:
        url: str = await self._run_in_executor(
            self._client.generate_presigned_url,
            "get_object",
            Params={"Bucket": self._bucket, "Key": path},
            ExpiresIn=expires,
        )
        return url
