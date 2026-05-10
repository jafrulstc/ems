"""
Storage router — file uploads and presigned URLs.
Prefix: /api/v1/storage
"""
from fastapi import APIRouter, Depends, File, UploadFile
import uuid

from app.dependencies import get_organization_id, require_permission
from app.shared.schemas import APIResponse, ok
from app.shared.exceptions import bad_request
from app.storage.s3_storage import S3StorageService
from pydantic import BaseModel

router = APIRouter()

class UploadResponse(BaseModel):
    path: str
    url: str

class PresignedUrlRequest(BaseModel):
    path: str
    expires_in: int = 3600

class PresignedUrlResponse(BaseModel):
    url: str

def get_storage_service() -> S3StorageService:
    return S3StorageService()

@router.post("/upload", response_model=APIResponse[UploadResponse], tags=["Storage"])
async def upload_file(
    file: UploadFile = File(...),
    org_id: int = Depends(get_organization_id),
    storage: S3StorageService = Depends(get_storage_service),
    # To upload, you generally need some form of permission, but keeping it general for now
):
    if not file.filename:
        raise bad_request("No filename provided")

    file_content = await file.read()
    
    # Generate a unique path to prevent overwrites, namespaced by organization
    ext = file.filename.split(".")[-1] if "." in file.filename else "bin"
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    path = f"org_{org_id}/{unique_name}"

    uploaded_path = await storage.upload_file(
        file=file_content,
        path=path,
        content_type=file.content_type or "application/octet-stream"
    )
    
    # Immediately generate a presigned URL for the client to preview
    presigned_url = await storage.get_presigned_url(uploaded_path)

    return ok(
        UploadResponse(path=uploaded_path, url=presigned_url),
        "File uploaded successfully"
    )

@router.post("/presigned-url", response_model=APIResponse[PresignedUrlResponse], tags=["Storage"])
async def get_presigned_url(
    payload: PresignedUrlRequest,
    org_id: int = Depends(get_organization_id),
    storage: S3StorageService = Depends(get_storage_service),
):
    # Security: ensure path belongs to the org
    if not payload.path.startswith(f"org_{org_id}/"):
        raise bad_request("Cannot access files outside your organization")

    url = await storage.get_presigned_url(payload.path, expires=payload.expires_in)
    return ok(PresignedUrlResponse(url=url))

@router.delete("/{path:path}", response_model=APIResponse[None], tags=["Storage"])
async def delete_file(
    path: str,
    org_id: int = Depends(get_organization_id),
    storage: S3StorageService = Depends(get_storage_service),
):
    # Security: ensure path belongs to the org
    if not path.startswith(f"org_{org_id}/"):
        raise bad_request("Cannot access files outside your organization")

    success = await storage.delete_file(path)
    if not success:
        raise bad_request("File not found or could not be deleted")
        
    return ok(None, "File deleted successfully")
