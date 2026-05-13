"""Academic student router: Students, Guardians, and Enrollments."""
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_organization_id, require_permission
from app.features.academic.schemas import (
    EnrollmentCreate, EnrollmentRead, EnrollmentUpdate,
    GuardianCreate, GuardianRead, GuardianUpdate,
    StudentCreate, StudentRead, StudentUpdate,
)
from app.features.academic.services.enrollment_service import EnrollmentService
from app.features.academic.services.guardian_service import GuardianService
from app.features.academic.services.student_service import StudentService
from app.shared.pagination import PaginationParams, pagination_params
from app.shared.schemas import APIResponse, PaginatedResponse, ok, paginated

router = APIRouter()

# ── Students ──────────────────────────────────────────────────────────────────

@router.get("/students", response_model=PaginatedResponse[StudentRead], tags=["Students"])
async def list_students(q: Optional[str] = None, p: PaginationParams = Depends(pagination_params),
                        org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                        _=Depends(require_permission("academic.students.view"))):
    data = await StudentService(db).list(org_id, p, q or "")
    return paginated(data.items, data.total, data.page, data.size)

@router.post("/students", response_model=APIResponse[StudentRead], status_code=201, tags=["Students"])
async def create_student(payload: StudentCreate, org_id: int = Depends(get_organization_id),
                         db: AsyncSession = Depends(get_db),
                         _=Depends(require_permission("academic.students.create"))):
    return ok(await StudentService(db).create(org_id, payload), "Student created.")

@router.get("/students/{id}", response_model=APIResponse[StudentRead], tags=["Students"])
async def get_student(id: int, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                      _=Depends(require_permission("academic.students.view"))):
    return ok(await StudentService(db).get(id, org_id))

@router.put("/students/{id}", response_model=APIResponse[StudentRead], tags=["Students"])
async def update_student(id: int, payload: StudentUpdate, org_id: int = Depends(get_organization_id),
                         db: AsyncSession = Depends(get_db),
                         _=Depends(require_permission("academic.students.edit"))):
    return ok(await StudentService(db).update(id, org_id, payload))

@router.delete("/students/{id}", response_model=APIResponse[None], tags=["Students"])
async def delete_student(id: int, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                         _=Depends(require_permission("academic.students.delete"))):
    await StudentService(db).delete(id, org_id)
    return ok(None, "Student deleted.")

# ── Guardians ─────────────────────────────────────────────────────────────────

@router.get("/students/{student_id}/guardians", response_model=APIResponse[list[GuardianRead]], tags=["Guardians"])
async def list_guardians(student_id: int, org_id: int = Depends(get_organization_id),
                         db: AsyncSession = Depends(get_db),
                         _=Depends(require_permission("academic.students.view"))):
    return ok(await GuardianService(db).list_for_student(student_id, org_id))

@router.post("/students/{student_id}/guardians", response_model=APIResponse[GuardianRead], status_code=201, tags=["Guardians"])
async def create_guardian(student_id: int, payload: GuardianCreate,
                          org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                          _=Depends(require_permission("academic.students.edit"))):
    return ok(await GuardianService(db).create_for_student(student_id, org_id, payload), "Guardian added.")

@router.put("/guardians/{id}", response_model=APIResponse[GuardianRead], tags=["Guardians"])
async def update_guardian(id: int, payload: GuardianUpdate,
                          org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                          _=Depends(require_permission("academic.students.edit"))):
    return ok(await GuardianService(db).update(id, org_id, payload))

@router.delete("/guardians/{id}", response_model=APIResponse[None], tags=["Guardians"])
async def delete_guardian(id: int, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                          _=Depends(require_permission("academic.students.edit"))):
    await GuardianService(db).delete(id, org_id)
    return ok(None, "Guardian deleted.")

# ── Enrollments ───────────────────────────────────────────────────────────────

@router.get("/enrollments", response_model=PaginatedResponse[EnrollmentRead], tags=["Enrollments"])
async def list_enrollments(p: PaginationParams = Depends(pagination_params),
                           org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                           _=Depends(require_permission("academic.enrollments.view"))):
    data = await EnrollmentService(db).list(org_id, p)
    return paginated(data.items, data.total, data.page, data.size)

@router.post("/enrollments", response_model=APIResponse[EnrollmentRead], status_code=201, tags=["Enrollments"])
async def create_enrollment(payload: EnrollmentCreate, org_id: int = Depends(get_organization_id),
                            db: AsyncSession = Depends(get_db),
                            _=Depends(require_permission("academic.enrollments.create"))):
    return ok(await EnrollmentService(db).create(org_id, payload), "Enrollment created.")

@router.get("/enrollments/{id}", response_model=APIResponse[EnrollmentRead], tags=["Enrollments"])
async def get_enrollment(id: int, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                         _=Depends(require_permission("academic.enrollments.view"))):
    return ok(await EnrollmentService(db).get(id, org_id))

@router.put("/enrollments/{id}", response_model=APIResponse[EnrollmentRead], tags=["Enrollments"])
async def update_enrollment(id: int, payload: EnrollmentUpdate, org_id: int = Depends(get_organization_id),
                            db: AsyncSession = Depends(get_db),
                            _=Depends(require_permission("academic.enrollments.edit"))):
    return ok(await EnrollmentService(db).update(id, org_id, payload))

@router.delete("/enrollments/{id}", response_model=APIResponse[None], tags=["Enrollments"])
async def delete_enrollment(id: int, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                            _=Depends(require_permission("academic.enrollments.delete"))):
    await EnrollmentService(db).delete(id, org_id)
    return ok(None, "Enrollment deleted.")
