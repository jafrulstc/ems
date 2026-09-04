import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.api.deps import SessionDep, TenantDep, require_permission
from app.models.exam import Exam, ExamResult, ExamSchedule, ExamType, GradingScale
from app.schemas.exam import (
    ExamCreate,
    ExamRead,
    ExamResultCreate,
    ExamResultRead,
    ExamScheduleCreate,
    ExamScheduleRead,
    ExamTypeCreate,
    ExamTypeRead,
    GradingScaleCreate,
    GradingScaleRead,
)
from app.services.exam_service import ExamService


class ResultGenerateRequest(BaseModel):
    exam_id: uuid.UUID

router = APIRouter()

# ── Grading Scale ─────────────────────────────────────────
@router.post("/grading-scales", response_model=GradingScaleRead, dependencies=[Depends(require_permission("exam:create"))])
async def create_grading_scale(session: SessionDep, tenant: TenantDep, scale_in: GradingScaleCreate) -> Any:
    db = GradingScale(**scale_in.model_dump(), tenant_id=tenant.id)
    session.add(db); await session.commit(); await session.refresh(db); return db

@router.get("/grading-scales", response_model=list[GradingScaleRead], dependencies=[Depends(require_permission("exam:read"))])
async def read_grading_scales(session: SessionDep, tenant: TenantDep, skip: int = 0, limit: int = 100) -> Any:
    return (await session.execute(select(GradingScale).offset(skip).limit(limit))).scalars().all()

@router.put("/grading-scales/{scale_id}", response_model=GradingScaleRead, dependencies=[Depends(require_permission("exam:create"))])
async def update_grading_scale(scale_id: str, session: SessionDep, tenant: TenantDep, scale_in: GradingScaleCreate) -> Any:
    db = (await session.execute(select(GradingScale).where(GradingScale.id == scale_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Not found")
    for k, v in scale_in.model_dump().items(): setattr(db, k, v)
    await session.commit(); await session.refresh(db); return db

@router.delete("/grading-scales/{scale_id}", dependencies=[Depends(require_permission("exam:create"))])
async def delete_grading_scale(scale_id: str, session: SessionDep, tenant: TenantDep) -> Any:
    db = (await session.execute(select(GradingScale).where(GradingScale.id == scale_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Not found")
    db.is_deleted = True; await session.commit(); return {"message": "Deleted"}

# ── Exam ──────────────────────────────────────────────────
@router.post("/", response_model=ExamRead, dependencies=[Depends(require_permission("exam:create"))])
async def create_exam(session: SessionDep, tenant: TenantDep, exam_in: ExamCreate) -> Any:
    db = Exam(**exam_in.model_dump(), tenant_id=tenant.id)
    session.add(db); await session.commit(); await session.refresh(db); return db

@router.get("/", response_model=list[ExamRead], dependencies=[Depends(require_permission("exam:read"))])
async def read_exams(session: SessionDep, tenant: TenantDep, skip: int = 0, limit: int = 100) -> Any:
    return (await session.execute(select(Exam).offset(skip).limit(limit))).scalars().all()

@router.put("/{exam_id}", response_model=ExamRead, dependencies=[Depends(require_permission("exam:create"))])
async def update_exam(exam_id: str, session: SessionDep, tenant: TenantDep, exam_in: ExamCreate) -> Any:
    db = (await session.execute(select(Exam).where(Exam.id == exam_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Not found")
    for k, v in exam_in.model_dump().items(): setattr(db, k, v)
    await session.commit(); await session.refresh(db); return db

@router.delete("/{exam_id}", dependencies=[Depends(require_permission("exam:create"))])
async def delete_exam(exam_id: str, session: SessionDep, tenant: TenantDep) -> Any:
    db = (await session.execute(select(Exam).where(Exam.id == exam_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Not found")
    db.is_deleted = True; await session.commit(); return {"message": "Deleted"}

# ── Exam Schedule ─────────────────────────────────────────
@router.post("/schedules", response_model=ExamScheduleRead, dependencies=[Depends(require_permission("exam_schedule:create"))])
async def create_exam_schedule(session: SessionDep, tenant: TenantDep, schedule_in: ExamScheduleCreate) -> Any:
    db = ExamSchedule(**schedule_in.model_dump(), tenant_id=tenant.id)
    session.add(db); await session.commit(); await session.refresh(db); return db

@router.get("/schedules", response_model=list[ExamScheduleRead], dependencies=[Depends(require_permission("exam:read"))])
async def read_exam_schedules(session: SessionDep, tenant: TenantDep, skip: int = 0, limit: int = 100) -> Any:
    return (await session.execute(select(ExamSchedule).offset(skip).limit(limit))).scalars().all()

@router.put("/schedules/{schedule_id}", response_model=ExamScheduleRead, dependencies=[Depends(require_permission("exam_schedule:create"))])
async def update_exam_schedule(schedule_id: str, session: SessionDep, tenant: TenantDep, schedule_in: ExamScheduleCreate) -> Any:
    db = (await session.execute(select(ExamSchedule).where(ExamSchedule.id == schedule_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Not found")
    for k, v in schedule_in.model_dump().items(): setattr(db, k, v)
    await session.commit(); await session.refresh(db); return db

@router.delete("/schedules/{schedule_id}", dependencies=[Depends(require_permission("exam:create"))])
async def delete_exam_schedule(schedule_id: str, session: SessionDep, tenant: TenantDep) -> Any:
    db = (await session.execute(select(ExamSchedule).where(ExamSchedule.id == schedule_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Not found")
    db.is_deleted = True; await session.commit(); return {"message": "Deleted"}

# ── Exam Result ───────────────────────────────────────────
@router.post("/results", response_model=ExamResultRead, dependencies=[Depends(require_permission("exam_result:create"))])
async def create_exam_result(session: SessionDep, tenant: TenantDep, result_in: ExamResultCreate) -> Any:
    db = ExamResult(**result_in.model_dump(), tenant_id=tenant.id)
    session.add(db); await session.commit(); await session.refresh(db); return db

@router.get("/results", response_model=list[ExamResultRead], dependencies=[Depends(require_permission("exam:read"))])
async def read_exam_results(session: SessionDep, tenant: TenantDep, skip: int = 0, limit: int = 100) -> Any:
    return (await session.execute(select(ExamResult).offset(skip).limit(limit))).scalars().all()

@router.put("/results/{result_id}", response_model=ExamResultRead, dependencies=[Depends(require_permission("exam_result:create"))])
async def update_exam_result(result_id: str, session: SessionDep, tenant: TenantDep, result_in: ExamResultCreate) -> Any:
    db = (await session.execute(select(ExamResult).where(ExamResult.id == result_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Not found")
    for k, v in result_in.model_dump().items(): setattr(db, k, v)
    await session.commit(); await session.refresh(db); return db

@router.delete("/results/{result_id}", dependencies=[Depends(require_permission("exam:create"))])
async def delete_exam_result(result_id: str, session: SessionDep, tenant: TenantDep) -> Any:
    db = (await session.execute(select(ExamResult).where(ExamResult.id == result_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Not found")
    db.is_deleted = True; await session.commit(); return {"message": "Deleted"}

# ── Exam Type ─────────────────────────────────────────────
@router.post("/types", response_model=ExamTypeRead, dependencies=[Depends(require_permission("exam:create"))])
async def create_exam_type(session: SessionDep, tenant: TenantDep, type_in: ExamTypeCreate) -> Any:
    db = ExamType(**type_in.model_dump(), tenant_id=tenant.id)
    session.add(db); await session.commit(); await session.refresh(db); return db

@router.get("/types", response_model=list[ExamTypeRead], dependencies=[Depends(require_permission("exam:read"))])
async def read_exam_types(session: SessionDep, tenant: TenantDep, skip: int = 0, limit: int = 100) -> Any:
    return (await session.execute(select(ExamType).offset(skip).limit(limit))).scalars().all()

@router.put("/types/{type_id}", response_model=ExamTypeRead, dependencies=[Depends(require_permission("exam:update"))])
async def update_exam_type(type_id: str, session: SessionDep, tenant: TenantDep, type_in: ExamTypeCreate) -> Any:
    db = (await session.execute(select(ExamType).where(ExamType.id == type_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Not found")
    for k, v in type_in.model_dump().items(): setattr(db, k, v)
    await session.commit(); await session.refresh(db); return db

@router.delete("/types/{type_id}", dependencies=[Depends(require_permission("exam:delete"))])
async def delete_exam_type(type_id: str, session: SessionDep, tenant: TenantDep) -> Any:
    db = (await session.execute(select(ExamType).where(ExamType.id == type_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Not found")
    db.is_deleted = True; await session.commit(); return {"message": "Deleted"}

# ── Result Generation ─────────────────────────────────────
@router.post("/results/generate", dependencies=[Depends(require_permission("exam_result:create"))])
async def generate_exam_results(req: ResultGenerateRequest, session: SessionDep, tenant: TenantDep) -> Any:
    return await ExamService.generate_exam_results(req.exam_id, session)

@router.get("/{exam_id}/subjects", response_model=list[uuid.UUID])
async def get_exam_assigned_subjects(
    exam_id: uuid.UUID,
    session: SessionDep,
    tenant: TenantDep
) -> Any:
    """Return all unique subject IDs assigned to any class in the academic year of the given exam."""
    return await ExamService.get_exam_assigned_subjects(exam_id, session)

# ── Exam Reports ──────────────────────────────────────────
@router.get("/reports/merit-list", dependencies=[Depends(require_permission("exam:read"))])
async def exam_merit_list(
    session: SessionDep,
    tenant: TenantDep,
    exam_id: uuid.UUID | None = None,
    academic_year_id: uuid.UUID | None = None,
    class_id: uuid.UUID | None = None
) -> Any:
    return await ExamService.get_exam_merit_list(session, exam_id, academic_year_id, class_id)
