"""ExamType and Routine services."""
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.exam.repositories.exam_type_repo import ExamTypeRepository
from app.features.exam.repositories.routine_repo import RoutineRepository
from app.features.exam.schemas import (
    ExamTypeCreate, ExamTypeRead, ExamTypeUpdate,
    RoutineCreate, RoutineRead, RoutineUpdate,
)
from app.shared.exceptions import not_found
from app.shared.pagination import PaginationParams
from app.shared.schemas import PaginatedData


class ExamTypeService:
    def __init__(self, db: AsyncSession):
        self._repo = ExamTypeRepository(db)

    async def list(self, org_id: int, p: PaginationParams) -> PaginatedData[ExamTypeRead]:
        items, total = await self._repo.get_many(org_id, p.offset, p.limit)
        return PaginatedData(items=[ExamTypeRead.model_validate(i) for i in items],
                             total=total, page=p.page, size=p.size,
                             pages=(total + p.size - 1) // p.size if p.size else 0)

    async def get(self, id: int, org_id: int) -> ExamTypeRead:
        obj = await self._repo.get_by_id(id, org_id)
        if not obj: raise not_found("ExamType")
        return ExamTypeRead.model_validate(obj)

    async def create(self, org_id: int, payload: ExamTypeCreate) -> ExamTypeRead:
        obj = await self._repo.create(org_id, payload.model_dump())
        return ExamTypeRead.model_validate(obj)

    async def update(self, id: int, org_id: int, payload: ExamTypeUpdate) -> ExamTypeRead:
        obj = await self._repo.get_by_id(id, org_id)
        if not obj: raise not_found("ExamType")
        obj = await self._repo.update(obj, payload.model_dump(exclude_none=True))
        return ExamTypeRead.model_validate(obj)

    async def delete(self, id: int, org_id: int) -> None:
        obj = await self._repo.get_by_id(id, org_id)
        if not obj: raise not_found("ExamType")
        await self._repo.soft_delete(obj)


class RoutineService:
    def __init__(self, db: AsyncSession):
        self._repo = RoutineRepository(db)

    async def list(self, org_id: int, p: PaginationParams) -> PaginatedData[RoutineRead]:
        items, total = await self._repo.get_many(org_id, p.offset, p.limit)
        return PaginatedData(items=[RoutineRead.model_validate(i) for i in items],
                             total=total, page=p.page, size=p.size,
                             pages=(total + p.size - 1) // p.size if p.size else 0)

    async def list_by_exam_type(self, exam_type_id: int, org_id: int) -> list[RoutineRead]:
        items = await self._repo.get_by_exam_type(exam_type_id, org_id)
        return [RoutineRead.model_validate(i) for i in items]

    async def get(self, id: int, org_id: int) -> RoutineRead:
        obj = await self._repo.get_by_id(id, org_id)
        if not obj: raise not_found("Routine")
        return RoutineRead.model_validate(obj)

    async def create(self, org_id: int, payload: RoutineCreate) -> RoutineRead:
        obj = await self._repo.create(org_id, payload.model_dump())
        return RoutineRead.model_validate(obj)

    async def update(self, id: int, org_id: int, payload: RoutineUpdate) -> RoutineRead:
        obj = await self._repo.get_by_id(id, org_id)
        if not obj: raise not_found("Routine")
        obj = await self._repo.update(obj, payload.model_dump(exclude_none=True))
        return RoutineRead.model_validate(obj)

    async def delete(self, id: int, org_id: int) -> None:
        obj = await self._repo.get_by_id(id, org_id)
        if not obj: raise not_found("Routine")
        await self._repo.soft_delete(obj)
