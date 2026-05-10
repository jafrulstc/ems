"""Academic Year service — business logic layer."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.core.repositories.academic_year_repo import AcademicYearRepository
from app.features.core.schemas import AcademicYearCreate, AcademicYearRead, AcademicYearUpdate
from app.shared.exceptions import bad_request, not_found
from app.shared.pagination import PaginationParams
from app.shared.schemas import PaginatedData


class AcademicYearService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = AcademicYearRepository(db)

    async def list(self, org_id: int, p: PaginationParams) -> PaginatedData[AcademicYearRead]:
        items, total = await self._repo.get_many(org_id, p.offset, p.limit)
        return PaginatedData(
            items=[AcademicYearRead.model_validate(i) for i in items],
            total=total,
            page=p.page,
            size=p.size,
            pages=(total + p.size - 1) // p.size if p.size else 0,
        )

    async def get(self, id: int, org_id: int) -> AcademicYearRead:
        obj = await self._repo.get_by_id(id, org_id)
        if not obj:
            raise not_found("Academic year")
        return AcademicYearRead.model_validate(obj)

    async def create(self, org_id: int, payload: AcademicYearCreate) -> AcademicYearRead:
        data = payload.model_dump()
        if data["end_date"] <= data["start_date"]:
            raise bad_request("end_date must be after start_date.")
        obj = await self._repo.create(org_id, data)
        return AcademicYearRead.model_validate(obj)

    async def update(self, id: int, org_id: int, payload: AcademicYearUpdate) -> AcademicYearRead:
        obj = await self._repo.get_by_id(id, org_id)
        if not obj:
            raise not_found("Academic year")
        data = payload.model_dump(exclude_none=True)
        obj = await self._repo.update(obj, data)
        return AcademicYearRead.model_validate(obj)

    async def delete(self, id: int, org_id: int) -> None:
        obj = await self._repo.get_by_id(id, org_id)
        if not obj:
            raise not_found("Academic year")
        await self._repo.soft_delete(obj)
