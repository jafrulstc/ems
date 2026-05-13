"""Exam marking router: Registrations, Marks entry, and Results."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_organization_id, require_permission
from app.features.exam.schemas import (
    ExamRegistrationCreate, ExamRegistrationRead,
    MarkBulkCreate, MarkRead,
    ResultRead,
)
from app.features.exam.services.exam_registration_service import ExamRegistrationService
from app.features.exam.services.mark_service import MarkService
from app.features.exam.services.attendance_result_service import AttendanceResultService
from app.shared.pagination import PaginationParams, pagination_params
from app.shared.schemas import APIResponse, PaginatedResponse, ok, paginated

router = APIRouter()

# ── Exam Registrations ───────────────────────────────────────────────────────

@router.get("/registrations", response_model=PaginatedResponse[ExamRegistrationRead], tags=["Registrations"])
async def list_registrations(p: PaginationParams = Depends(pagination_params),
                            org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                            _=Depends(require_permission("exam.marks.view"))):
    data = await ExamRegistrationService(db).list(org_id, p)
    return paginated(data.items, data.total, data.page, data.size)

@router.post("/registrations", response_model=APIResponse[ExamRegistrationRead], status_code=201, tags=["Registrations"])
async def create_registration(payload: ExamRegistrationCreate, org_id: int = Depends(get_organization_id),
                             db: AsyncSession = Depends(get_db),
                             _=Depends(require_permission("exam.marks.create"))):
    return ok(await ExamRegistrationService(db).create(org_id, payload), "Student registered for exam.")

@router.delete("/registrations/{id}", response_model=APIResponse[None], tags=["Registrations"])
async def delete_registration(id: int, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                             _=Depends(require_permission("exam.marks.delete"))):
    await ExamRegistrationService(db).delete(id, org_id)
    return ok(None, "Registration removed.")

# ── Marks ────────────────────────────────────────────────────────────────────

@router.get("/marks", response_model=PaginatedResponse[MarkRead], tags=["Marks"])
async def list_marks(p: PaginationParams = Depends(pagination_params),
                    org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                    _=Depends(require_permission("exam.marks.view"))):
    data = await MarkService(db).list(org_id, p)
    return paginated(data.items, data.total, data.page, data.size)

@router.get("/marks/by-subject", response_model=APIResponse[list[MarkRead]], tags=["Marks"])
async def get_marks_by_subject(exam_type_id: int, class_subject_id: int,
                              org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                              _=Depends(require_permission("exam.marks.view"))):
    return ok(await MarkService(db).get_by_class_subject(exam_type_id, class_subject_id, org_id))

@router.post("/marks/bulk", response_model=APIResponse[list[MarkRead]], status_code=201, tags=["Marks"])
async def bulk_upsert_marks(payload: MarkBulkCreate, org_id: int = Depends(get_organization_id),
                           db: AsyncSession = Depends(get_db),
                           _=Depends(require_permission("exam.marks.create"))):
    # The service implementation now includes explicit transaction handling
    return ok(await MarkService(db).bulk_upsert(org_id, payload), "Marks saved.")

# ── Results / Marksheets ─────────────────────────────────────────────────────

@router.get("/results/{enrollment_id}/{exam_type_id}", response_model=APIResponse[ResultRead], tags=["Results"])
async def get_exam_result(enrollment_id: int, exam_type_id: int,
                         org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                         _=Depends(require_permission("exam.marks.view"))):
    """Computes GPA/Grade for a specific student in a specific exam."""
    return ok(await AttendanceResultService(db).compute_result(enrollment_id, exam_type_id, org_id))

@router.get("/results/class/{class_id}/{exam_type_id}", response_model=APIResponse[list[ResultRead]], tags=["Results"])
async def get_class_results(class_id: int, exam_type_id: int,
                           org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                           _=Depends(require_permission("exam.marks.view"))):
    """Computes results for an entire class."""
    return ok(await AttendanceResultService(db).compute_class_results(class_id, exam_type_id, org_id))
