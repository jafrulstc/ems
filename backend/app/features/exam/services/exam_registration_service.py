from sqlalchemy.ext.asyncio import AsyncSession
from app.features.exam.repositories.exam_registration_repo import ExamRegistrationRepository
from app.features.exam.schemas import (
    ExamRegistrationCreate, ExamRegistrationRead, ExamRegistrationUpdate,
    ExamRegistrationBulkCreate
)
from app.shared.exceptions import not_found
from app.shared.pagination import PaginationParams
from app.shared.schemas import PaginatedData


class ExamRegistrationService:
    def __init__(self, db: AsyncSession):
        self._repo = ExamRegistrationRepository(db)

    async def list(self, org_id: int, p: PaginationParams) -> PaginatedData[ExamRegistrationRead]:
        items, total = await self._repo.get_many(org_id, p.offset, p.limit)
        return PaginatedData(
            items=[ExamRegistrationRead.model_validate(i) for i in items],
            total=total, page=p.page, size=p.size,
            pages=(total + p.size - 1) // p.size if p.size else 0,
        )

    async def list_by_exam_type(self, exam_type_id: int, org_id: int) -> list[ExamRegistrationRead]:
        items = await self._repo.get_by_exam_type(exam_type_id, org_id)
        return [ExamRegistrationRead.model_validate(i) for i in items]

    async def get(self, id: int, org_id: int) -> ExamRegistrationRead:
        obj = await self._repo.get_by_id(id, org_id)
        if not obj: raise not_found("ExamRegistration")
        return ExamRegistrationRead.model_validate(obj)

    async def create(self, org_id: int, payload: ExamRegistrationCreate) -> ExamRegistrationRead:
        obj = await self._repo.upsert(
            org_id,
            payload.enrollment_id,
            payload.exam_type_id,
            {
                "exam_board_id": payload.exam_board_id,
                "board_roll_no": payload.board_roll_no,
                "board_registration_no": payload.board_registration_no,
            }
        )
        return ExamRegistrationRead.model_validate(obj)

    async def bulk_create(self, org_id: int, payload: ExamRegistrationBulkCreate) -> list[ExamRegistrationRead]:
        results = []
        for eid in payload.enrollment_ids:
            obj = await self._repo.upsert(
                org_id,
                eid,
                payload.exam_type_id,
                {"exam_board_id": payload.exam_board_id}
            )
            results.append(ExamRegistrationRead.model_validate(obj))
        return results

    async def update(self, id: int, org_id: int, payload: ExamRegistrationUpdate) -> ExamRegistrationRead:
        obj = await self._repo.get_by_id(id, org_id)
        if not obj: raise not_found("ExamRegistration")
        obj = await self._repo.update(obj, payload.model_dump(exclude_none=True))
        return ExamRegistrationRead.model_validate(obj)

    async def delete(self, id: int, org_id: int) -> None:
        obj = await self._repo.get_by_id(id, org_id)
        if not obj: raise not_found("ExamRegistration")
        await self._repo.soft_delete(obj)
