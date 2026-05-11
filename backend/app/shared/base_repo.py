"""Shared base repository mixin for soft-deletable, tenant-scoped models."""
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepo:
    """Generic async CRUD helpers — subclass and set `_model`."""

    _model = None

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_many(self, org_id: int, offset: int = 0, limit: int = 20):
        base = select(self._model).where(
            self._model.organization_id == org_id,
            self._model.is_deleted.is_(False),
        )
        total = (await self._db.execute(
            select(func.count()).select_from(base.subquery())
        )).scalar_one()
        rows = await self._db.execute(
            base.order_by(self._model.id).offset(offset).limit(limit)
        )
        return list(rows.scalars().all()), total

    async def get_by_id(self, id: int, org_id: int):
        r = await self._db.execute(
            select(self._model).where(
                self._model.id == id,
                self._model.organization_id == org_id,
                self._model.is_deleted.is_(False),
            )
        )
        return r.scalar_one_or_none()

    async def create(self, org_id: int, data: dict):
        obj = self._model(organization_id=org_id, **data)
        self._db.add(obj)
        await self._db.flush()
        await self._db.refresh(obj)
        return obj

    async def update(self, obj, data: dict):
        for k, v in data.items():
            setattr(obj, k, v)
        await self._db.flush()
        await self._db.refresh(obj)
        return obj

    async def soft_delete(self, obj) -> None:
        obj.is_deleted = True
        obj.deleted_at = datetime.utcnow()
        await self._db.flush()
