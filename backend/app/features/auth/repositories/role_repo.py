"""Role repository — async SQLAlchemy, tenant-scoped."""
from datetime import datetime
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.features.auth.models import Role, RolePermission


class RoleRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_many(self, org_id: int) -> list[Role]:
        r = await self._db.execute(
            select(Role)
            .where(Role.organization_id == org_id, Role.is_deleted.is_(False))
            .options(selectinload(Role.permissions))
            .order_by(Role.name)
        )
        return list(r.scalars().all())

    async def get_by_id(self, id: int, org_id: int) -> Optional[Role]:
        r = await self._db.execute(
            select(Role)
            .where(Role.id == id, Role.organization_id == org_id, Role.is_deleted.is_(False))
            .options(selectinload(Role.permissions))
        )
        return r.scalar_one_or_none()

    async def create(self, org_id: int, data: dict) -> Role:
        obj = Role(organization_id=org_id, **data)
        self._db.add(obj)
        await self._db.flush()
        await self._db.refresh(obj)
        return obj

    async def update(self, obj: Role, data: dict) -> Role:
        for k, v in data.items():
            setattr(obj, k, v)
        await self._db.flush()
        await self._db.refresh(obj)
        return obj

    async def soft_delete(self, obj: Role) -> None:
        obj.is_deleted = True
        obj.deleted_at = datetime.utcnow()
        await self._db.flush()

    async def set_permissions(self, role_id: int, permission_ids: list[int]) -> None:
        await self._db.execute(
            delete(RolePermission).where(RolePermission.role_id == role_id)
        )
        for pid in permission_ids:
            self._db.add(RolePermission(role_id=role_id, permission_id=pid))
        await self._db.flush()
