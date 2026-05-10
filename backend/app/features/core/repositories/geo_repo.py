"""Geo repository — public reference data, no tenant scope."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.core.geo_models import District, Division, PostOffice, Upazila, Village


class GeoRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_divisions(self) -> list[Division]:
        result = await self._db.execute(select(Division).order_by(Division.name))
        return list(result.scalars().all())

    async def get_districts(self, division_id: Optional[int] = None) -> list[District]:
        stmt = select(District)
        if division_id:
            stmt = stmt.where(District.division_id == division_id)
        result = await self._db.execute(stmt.order_by(District.name))
        return list(result.scalars().all())

    async def get_upazilas(self, district_id: Optional[int] = None) -> list[Upazila]:
        stmt = select(Upazila)
        if district_id:
            stmt = stmt.where(Upazila.district_id == district_id)
        result = await self._db.execute(stmt.order_by(Upazila.name))
        return list(result.scalars().all())

    async def get_post_offices(self, upazila_id: Optional[int] = None) -> list[PostOffice]:
        stmt = select(PostOffice)
        if upazila_id:
            stmt = stmt.where(PostOffice.upazila_id == upazila_id)
        result = await self._db.execute(stmt.order_by(PostOffice.name))
        return list(result.scalars().all())

    async def get_villages(self, post_office_id: Optional[int] = None) -> list[Village]:
        stmt = select(Village)
        if post_office_id:
            stmt = stmt.where(Village.post_office_id == post_office_id)
        result = await self._db.execute(stmt.order_by(Village.name))
        return list(result.scalars().all())
