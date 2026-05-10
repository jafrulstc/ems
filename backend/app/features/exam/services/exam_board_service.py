from sqlalchemy.ext.asyncio import AsyncSession
from app.features.exam.repositories.exam_board_repo import ExamBoardRepository
from app.features.exam.schemas import ExamBoardCreate, ExamBoardRead, ExamBoardUpdate
from app.shared.exceptions import not_found
from app.shared.pagination import PaginationParams
from app.shared.schemas import PaginatedData


class ExamBoardService:
    def __init__(self, db: AsyncSession):
        self._repo = ExamBoardRepository(db)

    async def list(self, org_id: int, p: PaginationParams) -> PaginatedData[ExamBoardRead]:
        items, total = await self._repo.get_many(org_id, p.offset, p.limit)
        return PaginatedData(
            items=[ExamBoardRead.model_validate(i) for i in items],
            total=total, page=p.page, size=p.size,
            pages=(total + p.size - 1) // p.size if p.size else 0,
        )

    async def get(self, id: int, org_id: int) -> ExamBoardRead:
        obj = await self._repo.get_by_id(id, org_id)
        if not obj: raise not_found("ExamBoard")
        return ExamBoardRead.model_validate(obj)

    async def create(self, org_id: int, payload: ExamBoardCreate) -> ExamBoardRead:
        obj = await self._repo.create(org_id, payload.model_dump())
        return ExamBoardRead.model_validate(obj)

    async def update(self, id: int, org_id: int, payload: ExamBoardUpdate) -> ExamBoardRead:
        obj = await self._repo.get_by_id(id, org_id)
        if not obj: raise not_found("ExamBoard")
        obj = await self._repo.update(obj, payload.model_dump(exclude_none=True))
        return ExamBoardRead.model_validate(obj)

    async def delete(self, id: int, org_id: int) -> None:
        obj = await self._repo.get_by_id(id, org_id)
        if not obj: raise not_found("ExamBoard")
        await self._repo.soft_delete(obj)
