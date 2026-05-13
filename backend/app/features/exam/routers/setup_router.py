"""Exam setup router: Exam Types, Board Settings, and Grading Systems."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_organization_id, require_permission
from app.features.exam.schemas import (
    ExamBoardCreate, ExamBoardRead, ExamBoardUpdate,
    ExamTypeCreate, ExamTypeRead, ExamTypeUpdate,
    GradingSystemCreate, GradingSystemRead, GradingSystemUpdate,
)
from app.features.exam.services.exam_board_service import ExamBoardService
from app.features.exam.services.exam_type_service import ExamTypeService
from app.features.exam.services.grading_service import GradingService
from app.shared.pagination import PaginationParams, pagination_params
from app.shared.schemas import APIResponse, PaginatedResponse, ok, paginated

router = APIRouter()

# ── Exam Types ───────────────────────────────────────────────────────────────

@router.get("/types", response_model=PaginatedResponse[ExamTypeRead], tags=["Exam Types"])
async def list_exam_types(p: PaginationParams = Depends(pagination_params),
                         org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                         _=Depends(require_permission("exam.types.view"))):
    data = await ExamTypeService(db).list(org_id, p)
    return paginated(data.items, data.total, data.page, data.size)

@router.post("/types", response_model=APIResponse[ExamTypeRead], status_code=201, tags=["Exam Types"])
async def create_exam_type(payload: ExamTypeCreate, org_id: int = Depends(get_organization_id),
                          db: AsyncSession = Depends(get_db),
                          _=Depends(require_permission("exam.types.create"))):
    return ok(await ExamTypeService(db).create(org_id, payload), "Exam type created.")

@router.get("/types/{id}", response_model=APIResponse[ExamTypeRead], tags=["Exam Types"])
async def get_exam_type(id: int, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                       _=Depends(require_permission("exam.types.view"))):
    return ok(await ExamTypeService(db).get(id, org_id))

@router.put("/types/{id}", response_model=APIResponse[ExamTypeRead], tags=["Exam Types"])
async def update_exam_type(id: int, payload: ExamTypeUpdate, org_id: int = Depends(get_organization_id),
                          db: AsyncSession = Depends(get_db),
                          _=Depends(require_permission("exam.types.edit"))):
    return ok(await ExamTypeService(db).update(id, org_id, payload))

@router.delete("/types/{id}", response_model=APIResponse[None], tags=["Exam Types"])
async def delete_exam_type(id: int, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                          _=Depends(require_permission("exam.types.delete"))):
    await ExamTypeService(db).delete(id, org_id)
    return ok(None, "Exam type deleted.")

# ── Board Settings ───────────────────────────────────────────────────────────

@router.get("/board-settings", response_model=APIResponse[ExamBoardRead], tags=["Settings"])
async def get_board_settings(org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db)):
    return ok(await ExamBoardService(db).get_for_org(org_id))

@router.put("/board-settings", response_model=APIResponse[ExamBoardRead], tags=["Settings"])
async def update_board_settings(payload: ExamBoardUpdate, org_id: int = Depends(get_organization_id),
                               db: AsyncSession = Depends(get_db),
                               _=Depends(require_permission("core.settings.edit"))):
    return ok(await ExamBoardService(db).update_for_org(org_id, payload))

# ── Grading Systems ──────────────────────────────────────────────────────────

@router.get("/grading-systems", response_model=PaginatedResponse[GradingSystemRead], tags=["Grading"])
async def list_grading_systems(p: PaginationParams = Depends(pagination_params),
                              org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                              _=Depends(require_permission("exam.marks.view"))):
    data = await GradingService(db).list(org_id, p)
    return paginated(data.items, data.total, data.page, data.size)

@router.post("/grading-systems", response_model=APIResponse[GradingSystemRead], status_code=201, tags=["Grading"])
async def create_grading_system(payload: GradingSystemCreate, org_id: int = Depends(get_organization_id),
                               db: AsyncSession = Depends(get_db),
                               _=Depends(require_permission("exam.marks.create"))):
    return ok(await GradingService(db).create(org_id, payload), "Grading rule created.")

@router.delete("/grading-systems/{id}", response_model=APIResponse[None], tags=["Grading"])
async def delete_grading_system(id: int, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                               _=Depends(require_permission("exam.marks.delete"))):
    await GradingService(db).delete(id, org_id)
    return ok(None, "Grading rule deleted.")
