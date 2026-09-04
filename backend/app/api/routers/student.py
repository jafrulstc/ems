"""
routers/student.py
------------------
Thin router: only handles HTTP layer (request/response).
Business logic lives in StudentService.
"""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select

from app.api.deps import SessionDep, TenantDep, require_permission
from app.core.storage import get_storage
from app.models.student import Student
from app.schemas.student import (
    EnrollmentCreate,
    EnrollmentRead,
    GuardianCreate,
    GuardianRead,
    StudentCreate,
    StudentRead,
)
from app.services.student_service import StudentService

router = APIRouter()

# ── Guardian ──────────────────────────────────────────────
@router.post("/guardians", response_model=GuardianRead, dependencies=[Depends(require_permission("guardian:create"))])
async def create_guardian(session: SessionDep, tenant: TenantDep, guardian_in: GuardianCreate) -> Any:
    return await StudentService.create_guardian(guardian_in, tenant.id, session)

@router.get("/guardians", response_model=list[GuardianRead], dependencies=[Depends(require_permission("guardian:read"))])
async def read_guardians(session: SessionDep, tenant: TenantDep, skip: int = 0, limit: int = 100) -> Any:
    return await StudentService.get_guardians(session, skip, limit)

@router.put("/guardians/{guardian_id}", response_model=GuardianRead, dependencies=[Depends(require_permission("guardian:update"))])
async def update_guardian(guardian_id: str, session: SessionDep, tenant: TenantDep, guardian_in: GuardianCreate) -> Any:
    return await StudentService.update_guardian(guardian_id, guardian_in, session)

@router.delete("/guardians/{guardian_id}", dependencies=[Depends(require_permission("guardian:delete"))])
async def delete_guardian(guardian_id: str, session: SessionDep, tenant: TenantDep) -> Any:
    return await StudentService.delete_guardian(guardian_id, session)

# ── Student ───────────────────────────────────────────────
@router.post("/students", response_model=StudentRead, dependencies=[Depends(require_permission("student:create"))])
async def create_student(session: SessionDep, tenant: TenantDep, student_in: StudentCreate) -> Any:
    return await StudentService.create_student(student_in, tenant.id, session)

@router.get("/students/next-id", dependencies=[Depends(require_permission("student:read"))])
async def get_next_student_id(session: SessionDep, tenant: TenantDep) -> Any:
    """Return the next suggested student_id_no for this tenant (1-based, unique per tenant)."""
    next_id = await StudentService.get_next_student_id_no(tenant.id, session)
    return {"next_student_id_no": next_id}

@router.get("/students", response_model=list[StudentRead], dependencies=[Depends(require_permission("student:read"))])
async def read_students(session: SessionDep, tenant: TenantDep, skip: int = 0, limit: int = 100) -> Any:
    return await StudentService.get_students(session, skip, limit)

@router.put("/students/{student_id}", response_model=StudentRead, dependencies=[Depends(require_permission("student:update"))])
async def update_student(student_id: str, session: SessionDep, tenant: TenantDep, student_in: StudentCreate) -> Any:
    return await StudentService.update_student(student_id, student_in, session)

@router.delete("/students/{student_id}", dependencies=[Depends(require_permission("student:delete"))])
async def delete_student(student_id: str, session: SessionDep, tenant: TenantDep) -> Any:
    return await StudentService.delete_student(student_id, session)

@router.post("/students/{student_id}/upload-profile-picture", dependencies=[Depends(require_permission("student:update"))])
async def upload_profile_picture(student_id: uuid.UUID, session: SessionDep, tenant: TenantDep, file: UploadFile = File(...)) -> Any:
    stmt = select(Student).where(Student.id == student_id)
    result = await session.execute(stmt)
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    storage = get_storage()
    url = await storage.upload_file(file, directory=f"ems/{tenant.slug}/students")
    student.profile_picture_url = url
    await session.commit()
    return {"url": url}

# ── Enrollment ────────────────────────────────────────────
@router.post("/enrollments", response_model=EnrollmentRead, dependencies=[Depends(require_permission("enrollment:create"))])
async def create_enrollment(session: SessionDep, tenant: TenantDep, enrollment_in: EnrollmentCreate) -> Any:
    return await StudentService.create_enrollment(enrollment_in, tenant.id, session)

@router.get("/enrollments", response_model=list[EnrollmentRead], dependencies=[Depends(require_permission("enrollment:read"))])
async def read_enrollments(session: SessionDep, tenant: TenantDep, skip: int = 0, limit: int = 100) -> Any:
    return await StudentService.get_enrollments(session, skip, limit)

@router.put("/enrollments/{enrollment_id}", response_model=EnrollmentRead, dependencies=[Depends(require_permission("enrollment:update"))])
async def update_enrollment(enrollment_id: str, session: SessionDep, tenant: TenantDep, enrollment_in: EnrollmentCreate) -> Any:
    return await StudentService.update_enrollment(enrollment_id, enrollment_in, session)

@router.delete("/enrollments/{enrollment_id}", dependencies=[Depends(require_permission("enrollment:delete"))])
async def delete_enrollment(enrollment_id: str, session: SessionDep, tenant: TenantDep) -> Any:
    return await StudentService.delete_enrollment(enrollment_id, session)

# ── Reports ───────────────────────────────────────────────
@router.get("/reports/enrollments", dependencies=[Depends(require_permission("student:read"))])
async def report_enrollments(
    session: SessionDep,
    tenant: TenantDep,
    academic_year_id: uuid.UUID | None = None,
    class_id: uuid.UUID | None = None,
    section_id: uuid.UUID | None = None,
) -> Any:
    return await StudentService.report_enrollments(session, academic_year_id, class_id, section_id)
