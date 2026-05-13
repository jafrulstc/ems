from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.academic.models import Student, Class, Section, Subject, Enrollment
from app.features.exam.models import ExamType, Mark, Result
from app.features.reports.schemas import AcademicSummary, ExamSummary

class SummaryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_academic_summary(self, org_id: int) -> AcademicSummary:
        total_students = await self._count(Student, org_id)
        total_classes = await self._count(Class, org_id)
        total_sections = await self._count(Section, org_id)
        total_subjects = await self._count(Subject, org_id)
        total_enrollments = await self._count(Enrollment, org_id)

        return AcademicSummary(
            total_students=total_students,
            total_classes=total_classes,
            total_sections=total_sections,
            total_subjects=total_subjects,
            total_enrollments=total_enrollments
        )

    async def get_exam_summary(self, org_id: int) -> ExamSummary:
        total_exam_types = await self._count(ExamType, org_id)
        total_marks = await self._count(Mark, org_id)
        total_results = await self._count(Result, org_id)

        return ExamSummary(
            total_exam_types=total_exam_types,
            total_marks_entered=total_marks,
            total_results_computed=total_results
        )

    async def _count(self, model, org_id: int) -> int:
        stmt = select(func.count()).where(
            model.organization_id == org_id,
            model.is_deleted.is_(False)
        )
        res = await self.db.execute(stmt)
        return res.scalar() or 0
