import asyncio
import os
import uuid
from abc import ABC, abstractmethod
from fastapi import UploadFile
from app.core.config import settings

import boto3
from botocore.exceptions import ClientError

class BaseStorage(ABC):
    @abstractmethod
    async def upload_file(self, file: UploadFile, directory: str) -> str:
        """Uploads a file and returns its public URL or relative path."""
        pass

    @abstractmethod
    async def delete_file(self, file_path: str) -> None:
        """Deletes a file given its relative path or public_id."""
        pass

class S3CompatibleStorage(BaseStorage):
    def __init__(self):
        endpoint_url = None
        if settings.STORAGE_ENDPOINT:
            scheme = "https" if settings.STORAGE_SECURE else "http"
            endpoint_url = settings.STORAGE_ENDPOINT
            if not endpoint_url.startswith("http"):
                endpoint_url = f"{scheme}://{endpoint_url}"

        self.s3 = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=settings.STORAGE_ACCESS_KEY,
            aws_secret_access_key=settings.STORAGE_SECRET_KEY,
            region_name=settings.STORAGE_REGION or "us-east-1",
        )
        self.bucket = settings.STORAGE_BUCKET_NAME
        
        try:
            self.s3.head_bucket(Bucket=self.bucket)
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code')
            if error_code == '404':
                raise ValueError(f"Bucket '{self.bucket}' does not exist.")
            elif error_code == '403':
                raise ValueError(f"Access denied to bucket '{self.bucket}'. Check credentials.")
            else:
                raise ValueError(f"Storage connection failed: {e}")

    async def upload_file(self, file: UploadFile, directory: str) -> str:
        ext = os.path.splitext(file.filename)[1] if file.filename else ""
        unique_filename = f"{uuid.uuid4().hex[:12]}{ext}"
        object_name = f"{directory}/{unique_filename}"
        
        file.file.seek(0)
        
        def _upload():
            self.s3.upload_fileobj(
                file.file,
                self.bucket,
                object_name,
                ExtraArgs={"ContentType": file.content_type}
            )
        await asyncio.to_thread(_upload)
        
        endpoint_url = self.s3.meta.endpoint_url
        return f"{endpoint_url}/{self.bucket}/{object_name}"

    async def delete_file(self, file_path: str) -> None:
        def _delete():
            try:
                self.s3.delete_object(Bucket=self.bucket, Key=file_path)
            except ClientError:
                pass
        await asyncio.to_thread(_delete)

def get_storage() -> BaseStorage:
    return S3CompatibleStorage()
