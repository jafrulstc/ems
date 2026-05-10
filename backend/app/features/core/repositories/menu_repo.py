"""Menu repository — async SQLAlchemy, tenant-scoped, adjacency list."""
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.features.core.models import Menu


class MenuRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_tree(self, org_id: int) -> list[Menu]:
        """Return all root-level menus (parent_id IS NULL) with children loaded."""
        result = await self._db.execute(
            select(Menu)
            .where(
                Menu.organization_id == org_id,
                Menu.parent_id.is_(None),
                Menu.is_deleted.is_(False),
            )
            .options(selectinload(Menu.children).selectinload(Menu.children))
            .order_by(Menu.order)
        )
        return list(result.scalars().all())

    async def get_all_flat(self, org_id: int) -> list[Menu]:
        result = await self._db.execute(
            select(Menu).where(
                Menu.organization_id == org_id,
                Menu.is_deleted.is_(False),
            ).order_by(Menu.order)
        )
        return list(result.scalars().all())

    async def get_by_id(self, id: int, org_id: int) -> Optional[Menu]:
        result = await self._db.execute(
            select(Menu).where(
                Menu.id == id,
                Menu.organization_id == org_id,
                Menu.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def create(self, org_id: int, data: dict) -> Menu:
        obj = Menu(organization_id=org_id, **data)
        self._db.add(obj)
        await self._db.flush()
        await self._db.refresh(obj)
        return obj

    async def update(self, obj: Menu, data: dict) -> Menu:
        for field, value in data.items():
            setattr(obj, field, value)
        await self._db.flush()
        await self._db.refresh(obj)
        return obj

    async def soft_delete(self, obj: Menu) -> None:
        obj.is_deleted = True
        obj.deleted_at = datetime.utcnow()
        await self._db.flush()
