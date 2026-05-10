"""Student service with registration_no conflict guard and search."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.academic.repositories.student_repo import StudentRepository
from app.features.academic.schemas import StudentCreate, StudentRead, StudentUpdate
from app.shared.exceptions import conflict, not_found
from app.shared.pagination import PaginationParams
from app.shared.schemas import PaginatedData


class StudentService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = StudentRepository(db)

    async def list(self, org_id: int, p: PaginationParams, q: str = "") -> PaginatedData[StudentRead]:
        if q:
            items, total = await self._repo.search(org_id, q, p.offset, p.limit)
        else:
            items, total = await self._repo.get_many(org_id, p.offset, p.limit)
        return PaginatedData(
            items=[StudentRead.model_validate(i) for i in items],
            total=total, page=p.page, size=p.size,
            pages=(total + p.size - 1) // p.size if p.size else 0,
        )

    async def get(self, id: int, org_id: int) -> StudentRead:
        obj = await self._repo.get_by_id(id, org_id)
        if not obj:
            raise not_found("Student")
        return StudentRead.model_validate(obj)

    async def create(self, org_id: int, payload: StudentCreate) -> StudentRead:
        if await self._repo.get_by_registration(payload.registration_no, org_id):
            raise conflict(f"Registration number '{payload.registration_no}' already exists.")
        obj = await self._repo.create(org_id, payload.model_dump())
        return StudentRead.model_validate(obj)

    async def update(self, id: int, org_id: int, payload: StudentUpdate) -> StudentRead:
        obj = await self._repo.get_by_id(id, org_id)
        if not obj:
            raise not_found("Student")
        obj = await self._repo.update(obj, payload.model_dump(exclude_none=True))
        return StudentRead.model_validate(obj)

    async def delete(self, id: int, org_id: int) -> None:
        obj = await self._repo.get_by_id(id, org_id)
        if not obj:
            raise not_found("Student")
        await self._repo.soft_delete(obj)
