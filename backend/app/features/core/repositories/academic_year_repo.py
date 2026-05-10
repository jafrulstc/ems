"""Academic Year repository — async SQLAlchemy, tenant-scoped."""
from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.core.models import AcademicYear


class AcademicYearRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_many(
        self, org_id: int, offset: int = 0, limit: int = 20
    ) -> tuple[list[AcademicYear], int]:
        base = select(AcademicYear).where(
            AcademicYear.organization_id == org_id,
            AcademicYear.is_deleted.is_(False),
        )
        total_res = await self._db.execute(select(func.count()).select_from(base.subquery()))
        total: int = total_res.scalar_one()
        rows = await self._db.execute(
            base.order_by(AcademicYear.start_date.desc()).offset(offset).limit(limit)
        )
        return list(rows.scalars().all()), total

    async def get_by_id(self, id: int, org_id: int) -> Optional[AcademicYear]:
        result = await self._db.execute(
            select(AcademicYear).where(
                AcademicYear.id == id,
                AcademicYear.organization_id == org_id,
                AcademicYear.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def create(self, org_id: int, data: dict) -> AcademicYear:
        obj = AcademicYear(organization_id=org_id, **data)
        self._db.add(obj)
        await self._db.flush()
        await self._db.refresh(obj)
        return obj

    async def update(self, obj: AcademicYear, data: dict) -> AcademicYear:
        for field, value in data.items():
            if value is not None:
                setattr(obj, field, value)
        await self._db.flush()
        await self._db.refresh(obj)
        return obj

    async def soft_delete(self, obj: AcademicYear) -> None:
        obj.is_deleted = True
        obj.deleted_at = datetime.utcnow()
        await self._db.flush()
