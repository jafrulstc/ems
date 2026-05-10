"""Settings service — business logic layer."""
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.features.core.repositories.settings_repo import SettingsRepository
from app.features.core.schemas import AppSettingCreate, AppSettingRead, AppSettingUpdate
from app.shared.exceptions import conflict, not_found


class SettingsService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = SettingsRepository(db)

    async def list(self, org_id: int) -> list[AppSettingRead]:
        items = await self._repo.get_all(org_id)
        return [AppSettingRead.model_validate(i) for i in items]

    async def get_by_key(self, org_id: int, key: str) -> AppSettingRead:
        obj = await self._repo.get_by_key(org_id, key)
        if not obj:
            raise not_found(f"Setting '{key}'")
        return AppSettingRead.model_validate(obj)

    async def create(self, org_id: int, payload: AppSettingCreate) -> AppSettingRead:
        existing = await self._repo.get_by_key(org_id, payload.key)
        if existing:
            raise conflict(f"Setting '{payload.key}' already exists. Use PUT to update.")
        obj = await self._repo.create(org_id, payload.model_dump())
        return AppSettingRead.model_validate(obj)

    async def update(self, org_id: int, key: str, payload: AppSettingUpdate) -> AppSettingRead:
        obj = await self._repo.upsert(
            org_id, key, payload.value or "", payload.group
        )
        return AppSettingRead.model_validate(obj)
