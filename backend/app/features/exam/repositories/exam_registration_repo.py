from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.exam.models import ExamRegistration
from app.shared.base_repo import BaseRepo


class ExamRegistrationRepository(BaseRepo):
    _model = ExamRegistration

    async def get_by_enroll_exam(
        self, enrollment_id: int, exam_type_id: int, org_id: int
    ) -> Optional[ExamRegistration]:
        r = await self._db.execute(
            select(ExamRegistration).where(
                ExamRegistration.enrollment_id == enrollment_id,
                ExamRegistration.exam_type_id == exam_type_id,
                ExamRegistration.organization_id == org_id,
                ExamRegistration.is_deleted.is_(False),
            )
        )
        return r.scalar_one_or_none()

    async def get_by_exam_type(
        self, exam_type_id: int, org_id: int
    ) -> list[ExamRegistration]:
        r = await self._db.execute(
            select(ExamRegistration).where(
                ExamRegistration.exam_type_id == exam_type_id,
                ExamRegistration.organization_id == org_id,
                ExamRegistration.is_deleted.is_(False),
            )
        )
        return list(r.scalars().all())

    async def upsert(
        self, org_id: int, enrollment_id: int, exam_type_id: int, data: dict
    ) -> ExamRegistration:
        obj = await self.get_by_enroll_exam(enrollment_id, exam_type_id, org_id)
        if obj:
            return await self.update(obj, data)
        return await self.create(
            org_id,
            {"enrollment_id": enrollment_id, "exam_type_id": exam_type_id, **data},
        )
