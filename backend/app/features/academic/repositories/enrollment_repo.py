from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.academic.enrollment_models import Enrollment
from app.features.academic.repositories.base_repo import BaseRepo


class EnrollmentRepository(BaseRepo):
    _model = Enrollment

    async def get_active_by_student_year(
        self, student_id: int, academic_year_id: int, org_id: int
    ) -> Optional[Enrollment]:
        r = await self._db.execute(
            select(Enrollment).where(
                Enrollment.student_id == student_id,
                Enrollment.academic_year_id == academic_year_id,
                Enrollment.organization_id == org_id,
                Enrollment.is_active.is_(True),
                Enrollment.is_deleted.is_(False),
            )
        )
        return r.scalar_one_or_none()

    async def get_by_section(
        self, section_id: int, academic_year_id: int, org_id: int
    ) -> list[Enrollment]:
        r = await self._db.execute(
            select(Enrollment).where(
                Enrollment.section_id == section_id,
                Enrollment.academic_year_id == academic_year_id,
                Enrollment.organization_id == org_id,
                Enrollment.is_deleted.is_(False),
            ).order_by(Enrollment.roll_no)
        )
        return list(r.scalars().all())
