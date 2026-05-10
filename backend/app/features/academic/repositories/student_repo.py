from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.academic.models import Student
from app.features.academic.repositories.base_repo import BaseRepo


class StudentRepository(BaseRepo):
    _model = Student

    async def get_by_registration(
        self, registration_no: str, org_id: int
    ) -> Optional[Student]:
        r = await self._db.execute(
            select(Student).where(
                Student.registration_no == registration_no,
                Student.organization_id == org_id,
                Student.is_deleted.is_(False),
            )
        )
        return r.scalar_one_or_none()

    async def search(
        self, org_id: int, q: str, offset: int = 0, limit: int = 20
    ) -> tuple[list[Student], int]:
        from sqlalchemy import func, or_
        pattern = f"%{q}%"
        base = select(Student).where(
            Student.organization_id == org_id,
            Student.is_deleted.is_(False),
            or_(
                Student.full_name.ilike(pattern),
                Student.registration_no.ilike(pattern),
            ),
        )
        total = (await self._db.execute(
            select(func.count()).select_from(base.subquery())
        )).scalar_one()
        rows = await self._db.execute(
            base.order_by(Student.full_name).offset(offset).limit(limit)
        )
        return list(rows.scalars().all()), total
