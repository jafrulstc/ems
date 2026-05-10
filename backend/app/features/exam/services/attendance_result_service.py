"""Attendance and Result services."""
from datetime import date
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.exam.repositories.attendance_result_repo import AttendanceRepository, ResultRepository
from app.features.exam.repositories.grading_repo import GradingSystemRepository
from app.features.exam.repositories.mark_repo import MarkRepository
from app.features.exam.schemas import (
    AttendanceBulkCreate, AttendanceRead,
    ResultGenerateRequest, ResultRead,
)
from app.shared.exceptions import bad_request, not_found
from app.shared.pagination import PaginationParams
from app.shared.schemas import PaginatedData


class AttendanceService:
    def __init__(self, db: AsyncSession):
        self._repo = AttendanceRepository(db)

    async def bulk_upsert(self, org_id: int, payload: AttendanceBulkCreate) -> list[AttendanceRead]:
        results = []
        for entry in payload.entries:
            rec = await self._repo.upsert(org_id, entry.enrollment_id, payload.record_date, entry.status)
            results.append(AttendanceRead.model_validate(rec))
        return results

    async def get_by_date_range(
        self, enrollment_id: int, org_id: int, from_date: date, to_date: date
    ) -> list[AttendanceRead]:
        items = await self._repo.get_by_date_range(enrollment_id, org_id, from_date, to_date)
        return [AttendanceRead.model_validate(i) for i in items]


class ResultService:
    def __init__(self, db: AsyncSession):
        self._mark_repo = MarkRepository(db)
        self._grading_repo = GradingSystemRepository(db)
        self._result_repo = ResultRepository(db)

    async def generate(self, org_id: int, payload: ResultGenerateRequest) -> list[ResultRead]:
        # Determine grading system
        if payload.grading_system_id:
            gs = await self._grading_repo.get_by_id(payload.grading_system_id, org_id)
        else:
            gs = await self._grading_repo.get_default(org_id)
        if not gs:
            raise bad_request("No grading system found. Create one and mark it as default.")

        # Determine enrollments to process
        if payload.enrollment_ids:
            enrollment_ids = payload.enrollment_ids
        else:
            # Get all enrollment IDs that have marks for this exam type
            items, _ = await self._result_repo.get_many(org_id, 0, 10000)
            from app.features.exam.models import Mark
            from sqlalchemy import select
            r = await self._mark_repo._db.execute(
                select(Mark.enrollment_id).where(
                    Mark.exam_type_id == payload.exam_type_id,
                    Mark.organization_id == org_id,
                    Mark.is_deleted.is_(False),
                ).distinct()
            )
            enrollment_ids = list(r.scalars().all())

        results = []
        for eid in enrollment_ids:
            rows = await self._mark_repo.get_for_result(eid, payload.exam_type_id, org_id)
            if not rows:
                continue
            total_full = sum(int(row[1]) for row in rows)
            total_obtained = sum(
                float(row[0].marks_obtained) if not row[0].is_absent and row[0].marks_obtained else 0.0
                for row in rows
            )
            pct = round((total_obtained / total_full * 100) if total_full else 0.0, 2)
            rule = await self._grading_repo.resolve_grade(gs.id, org_id, pct)
            grade = rule.grade if rule else "F"
            gp = float(rule.grade_point) if rule else 0.0
            is_pass = gp > 0
            result = await self._result_repo.upsert(org_id, eid, payload.exam_type_id, {
                "total_full_marks": total_full,
                "total_obtained_marks": total_obtained,
                "percentage": pct,
                "grade": grade,
                "grade_point": gp,
                "is_pass": is_pass,
                "remarks": rule.remarks if rule else None,
            })
            results.append(ResultRead.model_validate(result))
        return results

    async def list(self, org_id: int, exam_type_id: int) -> list[ResultRead]:
        items = await self._result_repo.get_by_exam_type(exam_type_id, org_id)
        return [ResultRead.model_validate(i) for i in items]
