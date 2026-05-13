from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_organization_id, require_permission
from app.features.reports.schemas import AcademicSummary, ExamSummary
from app.features.reports.services.summary_service import SummaryService
from app.shared.schemas import APIResponse, ok

router = APIRouter()

@router.get("/academic-summary", response_model=APIResponse[AcademicSummary], tags=["Reports"])
async def get_academic_summary(
    org_id: int = Depends(get_organization_id),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission("academic.students.view"))
):
    return ok(await SummaryService(db).get_academic_summary(org_id))

@router.get("/exam-summary", response_model=APIResponse[ExamSummary], tags=["Reports"])
async def get_exam_summary(
    org_id: int = Depends(get_organization_id),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission("exam.marks.view"))
):
    return ok(await SummaryService(db).get_exam_summary(org_id))
