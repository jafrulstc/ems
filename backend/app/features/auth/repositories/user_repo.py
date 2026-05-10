"""User repository — async SQLAlchemy, tenant-scoped."""
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.features.auth.models import User, UserRole
from app.features.core.models import Organization


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_org_by_slug(self, slug: str) -> Optional[Organization]:
        r = await self._db.execute(
            select(Organization).where(Organization.slug == slug, Organization.is_deleted.is_(False))
        )
        return r.scalar_one_or_none()

    async def get_by_email(self, email: str, org_id: int) -> Optional[User]:
        r = await self._db.execute(
            select(User).where(
                User.email == email, User.organization_id == org_id, User.is_deleted.is_(False)
            )
        )
        return r.scalar_one_or_none()

    async def get_by_id(self, id: int, org_id: int) -> Optional[User]:
        r = await self._db.execute(
            select(User)
            .where(User.id == id, User.organization_id == org_id, User.is_deleted.is_(False))
            .options(selectinload(User.roles))
        )
        return r.scalar_one_or_none()

    async def get_many(self, org_id: int, offset: int, limit: int) -> tuple[list[User], int]:
        from sqlalchemy import func
        base = select(User).where(User.organization_id == org_id, User.is_deleted.is_(False))
        total = (await self._db.execute(select(func.count()).select_from(base.subquery()))).scalar_one()
        rows = await self._db.execute(
            base.options(selectinload(User.roles)).order_by(User.id).offset(offset).limit(limit)
        )
        return list(rows.scalars().all()), total

    async def get_role_ids(self, user_id: int) -> list[int]:
        r = await self._db.execute(select(UserRole.role_id).where(UserRole.user_id == user_id))
        return list(r.scalars().all())

    async def create(self, org_id: int, data: dict) -> User:
        obj = User(organization_id=org_id, **data)
        self._db.add(obj)
        await self._db.flush()
        await self._db.refresh(obj)
        return obj

    async def update(self, obj: User, data: dict) -> User:
        for k, v in data.items():
            setattr(obj, k, v)
        await self._db.flush()
        await self._db.refresh(obj)
        return obj

    async def soft_delete(self, obj: User) -> None:
        obj.is_deleted = True
        obj.deleted_at = datetime.utcnow()
        await self._db.flush()

    async def set_roles(self, user_id: int, role_ids: list[int]) -> None:
        from sqlalchemy import delete
        await self._db.execute(delete(UserRole).where(UserRole.user_id == user_id))
        for rid in role_ids:
            self._db.add(UserRole(user_id=user_id, role_id=rid))
        await self._db.flush()
