"""Geo service — read-only, public reference data."""
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.features.core.repositories.geo_repo import GeoRepository
from app.features.core.schemas import (
    DistrictRead, DivisionRead, PostOfficeRead, UpazilaRead, VillageRead,
)


class GeoService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = GeoRepository(db)

    async def get_divisions(self) -> list[DivisionRead]:
        items = await self._repo.get_divisions()
        return [DivisionRead.model_validate(i) for i in items]

    async def get_districts(self, division_id: Optional[int] = None) -> list[DistrictRead]:
        items = await self._repo.get_districts(division_id)
        return [DistrictRead.model_validate(i) for i in items]

    async def get_upazilas(self, district_id: Optional[int] = None) -> list[UpazilaRead]:
        items = await self._repo.get_upazilas(district_id)
        return [UpazilaRead.model_validate(i) for i in items]

    async def get_post_offices(self, upazila_id: Optional[int] = None) -> list[PostOfficeRead]:
        items = await self._repo.get_post_offices(upazila_id)
        return [PostOfficeRead.model_validate(i) for i in items]

    async def get_villages(self, post_office_id: Optional[int] = None) -> list[VillageRead]:
        items = await self._repo.get_villages(post_office_id)
        return [VillageRead.model_validate(i) for i in items]
