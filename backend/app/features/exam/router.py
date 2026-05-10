"""
Exam feature router. Prefix: /api/v1/exam
"""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_organization_id, require_permission
from app.features.exam.schemas import (
    AttendanceBulkCreate, AttendanceRead,
    ExamTypeCreate, ExamTypeRead, ExamTypeUpdate,
    GradingRuleCreate, GradingRuleRead,
    GradingSystemCreate, GradingSystemRead, GradingSystemUpdate,
    MarkBulkCreate, MarkRead,
    ResultGenerateRequest, ResultRead,
    RoutineCreate, RoutineRead, RoutineUpdate,
)
from app.features.exam.services.attendance_result_service import AttendanceService, ResultService
from app.features.exam.services.exam_type_service import ExamTypeService, RoutineService
from app.features.exam.services.grading_service import GradingService
from app.features.exam.services.mark_service import MarkService
from app.shared.pagination import PaginationParams, pagination_params
from app.shared.schemas import APIResponse, PaginatedResponse, ok, paginated

router = APIRouter()

# ── Exam Types ────────────────────────────────────────────────────────────────

@router.get("/exam-types", response_model=PaginatedResponse[ExamTypeRead], tags=["Exam Types"])
async def list_exam_types(p: PaginationParams = Depends(pagination_params),
                          org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                          _=Depends(require_permission("exam.exam_types.view"))):
    data = await ExamTypeService(db).list(org_id, p)
    return paginated(data.items, data.total, data.page, data.size)

@router.post("/exam-types", response_model=APIResponse[ExamTypeRead], status_code=201, tags=["Exam Types"])
async def create_exam_type(payload: ExamTypeCreate, org_id: int = Depends(get_organization_id),
                           db: AsyncSession = Depends(get_db),
                           _=Depends(require_permission("exam.exam_types.create"))):
    return ok(await ExamTypeService(db).create(org_id, payload), "Exam type created.")

@router.get("/exam-types/{id}", response_model=APIResponse[ExamTypeRead], tags=["Exam Types"])
async def get_exam_type(id: int, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                        _=Depends(require_permission("exam.exam_types.view"))):
    return ok(await ExamTypeService(db).get(id, org_id))

@router.put("/exam-types/{id}", response_model=APIResponse[ExamTypeRead], tags=["Exam Types"])
async def update_exam_type(id: int, payload: ExamTypeUpdate, org_id: int = Depends(get_organization_id),
                           db: AsyncSession = Depends(get_db),
                           _=Depends(require_permission("exam.exam_types.edit"))):
    return ok(await ExamTypeService(db).update(id, org_id, payload))

@router.delete("/exam-types/{id}", response_model=APIResponse[None], tags=["Exam Types"])
async def delete_exam_type(id: int, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                           _=Depends(require_permission("exam.exam_types.delete"))):
    await ExamTypeService(db).delete(id, org_id)
    return ok(None, "Exam type deleted.")

# ── Routines ──────────────────────────────────────────────────────────────────

@router.get("/routines", response_model=PaginatedResponse[RoutineRead], tags=["Routines"])
async def list_routines(p: PaginationParams = Depends(pagination_params),
                        org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                        _=Depends(require_permission("exam.routines.view"))):
    data = await RoutineService(db).list(org_id, p)
    return paginated(data.items, data.total, data.page, data.size)

@router.get("/routines/by-exam/{exam_type_id}", response_model=APIResponse[list[RoutineRead]], tags=["Routines"])
async def routines_by_exam(exam_type_id: int, org_id: int = Depends(get_organization_id),
                           db: AsyncSession = Depends(get_db),
                           _=Depends(require_permission("exam.routines.view"))):
    return ok(await RoutineService(db).list_by_exam_type(exam_type_id, org_id))

@router.post("/routines", response_model=APIResponse[RoutineRead], status_code=201, tags=["Routines"])
async def create_routine(payload: RoutineCreate, org_id: int = Depends(get_organization_id),
                         db: AsyncSession = Depends(get_db),
                         _=Depends(require_permission("exam.routines.create"))):
    return ok(await RoutineService(db).create(org_id, payload), "Routine created.")

@router.put("/routines/{id}", response_model=APIResponse[RoutineRead], tags=["Routines"])
async def update_routine(id: int, payload: RoutineUpdate, org_id: int = Depends(get_organization_id),
                         db: AsyncSession = Depends(get_db),
                         _=Depends(require_permission("exam.routines.edit"))):
    return ok(await RoutineService(db).update(id, org_id, payload))

@router.delete("/routines/{id}", response_model=APIResponse[None], tags=["Routines"])
async def delete_routine(id: int, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                         _=Depends(require_permission("exam.routines.delete"))):
    await RoutineService(db).delete(id, org_id)
    return ok(None, "Routine deleted.")

# ── Grading Systems ───────────────────────────────────────────────────────────

@router.get("/grading-systems", response_model=PaginatedResponse[GradingSystemRead], tags=["Grading"])
async def list_grading_systems(p: PaginationParams = Depends(pagination_params),
                                org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                                _=Depends(require_permission("exam.grading.view"))):
    data = await GradingService(db).list(org_id, p)
    return paginated(data.items, data.total, data.page, data.size)

@router.post("/grading-systems", response_model=APIResponse[GradingSystemRead], status_code=201, tags=["Grading"])
async def create_grading_system(payload: GradingSystemCreate, org_id: int = Depends(get_organization_id),
                                 db: AsyncSession = Depends(get_db),
                                 _=Depends(require_permission("exam.grading.create"))):
    return ok(await GradingService(db).create(org_id, payload), "Grading system created.")

@router.get("/grading-systems/{id}", response_model=APIResponse[GradingSystemRead], tags=["Grading"])
async def get_grading_system(id: int, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                              _=Depends(require_permission("exam.grading.view"))):
    return ok(await GradingService(db).get(id, org_id))

@router.put("/grading-systems/{id}", response_model=APIResponse[GradingSystemRead], tags=["Grading"])
async def update_grading_system(id: int, payload: GradingSystemUpdate, org_id: int = Depends(get_organization_id),
                                 db: AsyncSession = Depends(get_db),
                                 _=Depends(require_permission("exam.grading.edit"))):
    return ok(await GradingService(db).update(id, org_id, payload))

@router.delete("/grading-systems/{id}", response_model=APIResponse[None], tags=["Grading"])
async def delete_grading_system(id: int, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                                 _=Depends(require_permission("exam.grading.delete"))):
    await GradingService(db).delete(id, org_id)
    return ok(None, "Grading system deleted.")

@router.post("/grading-systems/{id}/rules", response_model=APIResponse[GradingRuleRead], status_code=201, tags=["Grading"])
async def add_grading_rule(id: int, payload: GradingRuleCreate, org_id: int = Depends(get_organization_id),
                            db: AsyncSession = Depends(get_db),
                            _=Depends(require_permission("exam.grading.edit"))):
    return ok(await GradingService(db).add_rule(id, org_id, payload), "Grading rule added.")

# ── Marks ─────────────────────────────────────────────────────────────────────

@router.get("/marks", response_model=PaginatedResponse[MarkRead], tags=["Marks"])
async def list_marks(p: PaginationParams = Depends(pagination_params),
                     org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                     _=Depends(require_permission("exam.marks.view"))):
    data = await MarkService(db).list(org_id, p)
    return paginated(data.items, data.total, data.page, data.size)

@router.post("/marks/bulk", response_model=APIResponse[list[MarkRead]], tags=["Marks"])
async def bulk_upsert_marks(payload: MarkBulkCreate, org_id: int = Depends(get_organization_id),
                             db: AsyncSession = Depends(get_db),
                             _=Depends(require_permission("exam.marks.create"))):
    return ok(await MarkService(db).bulk_upsert(org_id, payload), f"{len(payload.entries)} mark(s) saved.")

@router.get("/marks/by-subject", response_model=APIResponse[list[MarkRead]], tags=["Marks"])
async def marks_by_subject(exam_type_id: int, class_subject_id: int,
                            org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                            _=Depends(require_permission("exam.marks.view"))):
    return ok(await MarkService(db).get_by_class_subject(exam_type_id, class_subject_id, org_id))

@router.delete("/marks/{id}", response_model=APIResponse[None], tags=["Marks"])
async def delete_mark(id: int, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                      _=Depends(require_permission("exam.marks.edit"))):
    await MarkService(db).delete(id, org_id)
    return ok(None, "Mark deleted.")

# ── Attendance ────────────────────────────────────────────────────────────────

@router.post("/attendance/bulk", response_model=APIResponse[list[AttendanceRead]], tags=["Attendance"])
async def bulk_upsert_attendance(payload: AttendanceBulkCreate, org_id: int = Depends(get_organization_id),
                                  db: AsyncSession = Depends(get_db),
                                  _=Depends(require_permission("exam.attendance.create"))):
    return ok(await AttendanceService(db).bulk_upsert(org_id, payload), f"{len(payload.entries)} record(s) saved.")

@router.get("/attendance", response_model=APIResponse[list[AttendanceRead]], tags=["Attendance"])
async def get_attendance(enrollment_id: int, from_date: date, to_date: date,
                         org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                         _=Depends(require_permission("exam.attendance.view"))):
    return ok(await AttendanceService(db).get_by_date_range(enrollment_id, org_id, from_date, to_date))

# ── Results ───────────────────────────────────────────────────────────────────

@router.post("/results/generate", response_model=APIResponse[list[ResultRead]], tags=["Results"])
async def generate_results(payload: ResultGenerateRequest, org_id: int = Depends(get_organization_id),
                            db: AsyncSession = Depends(get_db),
                            _=Depends(require_permission("exam.results.create"))):
    results = await ResultService(db).generate(org_id, payload)
    return ok(results, f"{len(results)} result(s) generated.")

@router.get("/results", response_model=APIResponse[list[ResultRead]], tags=["Results"])
async def list_results(exam_type_id: int, org_id: int = Depends(get_organization_id),
                       db: AsyncSession = Depends(get_db),
                       _=Depends(require_permission("exam.results.view"))):
    return ok(await ResultService(db).list(org_id, exam_type_id))
