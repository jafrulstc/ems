from typing import Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.academic.guardian_models import Guardian
from app.shared.base_repo import BaseRepo


class GuardianRepository(BaseRepo):
    _model = Guardian

    async def get_by_student(self, student_id: int, org_id: int) -> list[Guardian]:
        r = await self._db.execute(
            select(Guardian).where(
                Guardian.student_id == student_id,
                Guardian.organization_id == org_id,
                Guardian.is_deleted.is_(False),
            ).order_by(Guardian.is_primary.desc())
        )
        return list(r.scalars().all())

    async def create_for_student(
        self, org_id: int, student_id: int, data: dict
    ) -> Guardian:
        obj = Guardian(organization_id=org_id, student_id=student_id, **data)
        self._db.add(obj)
        await self._db.flush()
        await self._db.refresh(obj)
        return obj
