from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.academic.models import Section
from app.features.academic.repositories.base_repo import BaseRepo


class SectionRepository(BaseRepo):
    _model = Section

    async def get_by_class(self, class_id: int, org_id: int) -> list[Section]:
        r = await self._db.execute(
            select(Section).where(
                Section.class_id == class_id,
                Section.organization_id == org_id,
                Section.is_deleted.is_(False),
            ).order_by(Section.name)
        )
        return list(r.scalars().all())
