import uuid
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select

from app.api.deps import SessionDep, TenantDep, require_permission
from app.core.storage import get_storage
from app.models.student import Enrollment, Guardian, Student
from app.schemas.student import (
    EnrollmentCreate,
    EnrollmentRead,
    GuardianCreate,
    GuardianRead,
    StudentCreate,
    StudentRead,
)

router = APIRouter()

# ── Guardian ──────────────────────────────────────────────
@router.post("/guardians", response_model=GuardianRead, dependencies=[Depends(require_permission("guardian:create"))])
async def create_guardian(session: SessionDep, tenant: TenantDep, guardian_in: GuardianCreate) -> Any:
    db = Guardian(**guardian_in.model_dump(), tenant_id=tenant.id)
    session.add(db); await session.commit(); await session.refresh(db); return db

@router.get("/guardians", response_model=list[GuardianRead], dependencies=[Depends(require_permission("guardian:read"))])
async def read_guardians(session: SessionDep, tenant: TenantDep, skip: int = 0, limit: int = 100) -> Any:
    return (await session.execute(select(Guardian).offset(skip).limit(limit))).scalars().all()

@router.put("/guardians/{guardian_id}", response_model=GuardianRead, dependencies=[Depends(require_permission("guardian:update"))])
async def update_guardian(guardian_id: str, session: SessionDep, tenant: TenantDep, guardian_in: GuardianCreate) -> Any:
    db = (await session.execute(select(Guardian).where(Guardian.id == guardian_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Not found")
    for k, v in guardian_in.model_dump().items(): setattr(db, k, v)
    await session.commit(); await session.refresh(db); return db

@router.delete("/guardians/{guardian_id}", dependencies=[Depends(require_permission("guardian:delete"))])
async def delete_guardian(guardian_id: str, session: SessionDep, tenant: TenantDep) -> Any:
    db = (await session.execute(select(Guardian).where(Guardian.id == guardian_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Not found")
    db.is_deleted = True; await session.commit(); return {"message": "Deleted"}

# ── Student ───────────────────────────────────────────────
@router.post("/students", response_model=StudentRead, dependencies=[Depends(require_permission("student:create"))])
async def create_student(session: SessionDep, tenant: TenantDep, student_in: StudentCreate) -> Any:
    db = Student(**student_in.model_dump(), tenant_id=tenant.id)
    session.add(db); await session.commit(); await session.refresh(db); return db

@router.get("/students", response_model=list[StudentRead], dependencies=[Depends(require_permission("student:read"))])
async def read_students(session: SessionDep, tenant: TenantDep, skip: int = 0, limit: int = 100) -> Any:
    return (await session.execute(select(Student).offset(skip).limit(limit))).scalars().all()

@router.put("/students/{student_id}", response_model=StudentRead, dependencies=[Depends(require_permission("student:update"))])
async def update_student(student_id: str, session: SessionDep, tenant: TenantDep, student_in: StudentCreate) -> Any:
    db = (await session.execute(select(Student).where(Student.id == student_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Not found")
    for k, v in student_in.model_dump().items(): setattr(db, k, v)
    await session.commit(); await session.refresh(db); return db

@router.delete("/students/{student_id}", dependencies=[Depends(require_permission("student:delete"))])
async def delete_student(student_id: str, session: SessionDep, tenant: TenantDep) -> Any:
    db = (await session.execute(select(Student).where(Student.id == student_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Not found")
    db.is_deleted = True; await session.commit(); return {"message": "Deleted"}

@router.post("/students/{student_id}/upload-profile-picture", dependencies=[Depends(require_permission("student:update"))])
async def upload_profile_picture(student_id: uuid.UUID, session: SessionDep, tenant: TenantDep, file: UploadFile = File(...)) -> Any:
    stmt = select(Student).where(Student.id == student_id)
    result = await session.execute(stmt)
    student = result.scalar_one_or_none()
    if not student: raise HTTPException(status_code=404, detail="Student not found")
    storage = get_storage()
    url = await storage.upload_file(file, directory=f"ems/{tenant.slug}/students")
    student.profile_picture_url = url
    await session.commit()
    return {"url": url}

# ── Enrollment ────────────────────────────────────────────
@router.post("/enrollments", response_model=EnrollmentRead, dependencies=[Depends(require_permission("enrollment:create"))])
async def create_enrollment(session: SessionDep, tenant: TenantDep, enrollment_in: EnrollmentCreate) -> Any:
    db = Enrollment(**enrollment_in.model_dump(), tenant_id=tenant.id)
    session.add(db); await session.commit(); await session.refresh(db); return db

@router.get("/enrollments", response_model=list[EnrollmentRead], dependencies=[Depends(require_permission("enrollment:read"))])
async def read_enrollments(session: SessionDep, tenant: TenantDep, skip: int = 0, limit: int = 100) -> Any:
    return (await session.execute(select(Enrollment).offset(skip).limit(limit))).scalars().all()

@router.put("/enrollments/{enrollment_id}", response_model=EnrollmentRead, dependencies=[Depends(require_permission("enrollment:update"))])
async def update_enrollment(enrollment_id: str, session: SessionDep, tenant: TenantDep, enrollment_in: EnrollmentCreate) -> Any:
    db = (await session.execute(select(Enrollment).where(Enrollment.id == enrollment_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Not found")
    for k, v in enrollment_in.model_dump().items(): setattr(db, k, v)
    await session.commit(); await session.refresh(db); return db

@router.delete("/enrollments/{enrollment_id}", dependencies=[Depends(require_permission("enrollment:delete"))])
async def delete_enrollment(enrollment_id: str, session: SessionDep, tenant: TenantDep) -> Any:
    db = (await session.execute(select(Enrollment).where(Enrollment.id == enrollment_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Not found")
    db.is_deleted = True; await session.commit(); return {"message": "Deleted"}

# ── Reports ───────────────────────────────────────────────
@router.get("/reports/enrollments", dependencies=[Depends(require_permission("student:read"))])
async def report_enrollments(
    session: SessionDep, 
    tenant: TenantDep, 
    academic_year_id: uuid.UUID | None = None,
    class_id: uuid.UUID | None = None,
    section_id: uuid.UUID | None = None
) -> Any:
    stmt = select(Enrollment, Student).join(Student, Enrollment.student_id == Student.id)
    if academic_year_id:
        stmt = stmt.where(Enrollment.academic_year_id == academic_year_id)
    if class_id:
        stmt = stmt.where(Enrollment.class_id == class_id)
    if section_id:
        stmt = stmt.where(Enrollment.section_id == section_id)
        
    result = await session.execute(stmt)
    records = result.all()
    
    report_data = []
    for enr, std in records:
        report_data.append({
            "enrollment_id": enr.id,
            "roll_number": enr.roll_number,
            "student_id": std.id,
            "student_id_no": std.student_id_no,
            "student_name": f"{std.first_name} {std.last_name}",
            "gender": std.gender
        })
    return report_data
