"""Attendance and Result repositories."""
from datetime import date
from typing import Optional
from sqlalchemy import select
from app.features.exam.models import AttendanceRecord, Result
from app.shared.base_repo import BaseRepo


class AttendanceRepository(BaseRepo):
    _model = AttendanceRecord

    async def get_by_enroll_date(
        self, enrollment_id: int, record_date: date, org_id: int
    ) -> Optional[AttendanceRecord]:
        r = await self._db.execute(
            select(AttendanceRecord).where(
                AttendanceRecord.enrollment_id == enrollment_id,
                AttendanceRecord.record_date == record_date,
                AttendanceRecord.organization_id == org_id,
            )
        )
        return r.scalar_one_or_none()

    async def upsert(self, org_id: int, enrollment_id: int, record_date: date, status: str):
        obj = await self.get_by_enroll_date(enrollment_id, record_date, org_id)
        if obj:
            return await self.update(obj, {"status": status})
        return await self.create(org_id, {
            "enrollment_id": enrollment_id,
            "record_date": record_date,
            "status": status,
        })

    async def get_by_date_range(
        self, enrollment_id: int, org_id: int, from_date: date, to_date: date
    ) -> list[AttendanceRecord]:
        r = await self._db.execute(
            select(AttendanceRecord).where(
                AttendanceRecord.enrollment_id == enrollment_id,
                AttendanceRecord.organization_id == org_id,
                AttendanceRecord.record_date >= from_date,
                AttendanceRecord.record_date <= to_date,
            ).order_by(AttendanceRecord.record_date)
        )
        return list(r.scalars().all())


class ResultRepository(BaseRepo):
    _model = Result

    async def get_by_enroll_exam(
        self, enrollment_id: int, exam_type_id: int, org_id: int
    ) -> Optional[Result]:
        r = await self._db.execute(
            select(Result).where(
                Result.enrollment_id == enrollment_id,
                Result.exam_type_id == exam_type_id,
                Result.organization_id == org_id,
                Result.is_deleted.is_(False),
            )
        )
        return r.scalar_one_or_none()

    async def upsert(self, org_id: int, enrollment_id: int, exam_type_id: int, data: dict) -> Result:
        obj = await self.get_by_enroll_exam(enrollment_id, exam_type_id, org_id)
        if obj:
            return await self.update(obj, data)
        return await self.create(org_id, {"enrollment_id": enrollment_id, "exam_type_id": exam_type_id, **data})

    async def get_by_exam_type(self, exam_type_id: int, org_id: int) -> list[Result]:
        r = await self._db.execute(
            select(Result).where(
                Result.exam_type_id == exam_type_id,
                Result.organization_id == org_id,
                Result.is_deleted.is_(False),
            )
        )
        return list(r.scalars().all())
