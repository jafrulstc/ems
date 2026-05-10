"""AppSetting repository — async SQLAlchemy, tenant-scoped."""
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.core.models import AppSetting


class SettingsRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_all(self, org_id: int) -> list[AppSetting]:
        result = await self._db.execute(
            select(AppSetting).where(
                AppSetting.organization_id == org_id,
                AppSetting.is_deleted.is_(False),
            ).order_by(AppSetting.group, AppSetting.key)
        )
        return list(result.scalars().all())

    async def get_by_key(self, org_id: int, key: str) -> Optional[AppSetting]:
        result = await self._db.execute(
            select(AppSetting).where(
                AppSetting.organization_id == org_id,
                AppSetting.key == key,
                AppSetting.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def create(self, org_id: int, data: dict) -> AppSetting:
        obj = AppSetting(organization_id=org_id, **data)
        self._db.add(obj)
        await self._db.flush()
        await self._db.refresh(obj)
        return obj

    async def upsert(self, org_id: int, key: str, value: str, group: Optional[str] = None) -> AppSetting:
        obj = await self.get_by_key(org_id, key)
        if obj:
            obj.value = value
            if group is not None:
                obj.group = group
        else:
            obj = AppSetting(organization_id=org_id, key=key, value=value, group=group)
            self._db.add(obj)
        await self._db.flush()
        await self._db.refresh(obj)
        return obj

    async def soft_delete(self, obj: AppSetting) -> None:
        obj.is_deleted = True
        obj.deleted_at = datetime.utcnow()
        await self._db.flush()
