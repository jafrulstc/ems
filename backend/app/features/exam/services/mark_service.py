"""Mark service — bulk upsert and per-class fetch."""
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.exam.repositories.mark_repo import MarkRepository
from app.features.exam.schemas import MarkBulkCreate, MarkRead
from app.shared.exceptions import not_found
from app.shared.pagination import PaginationParams
from app.shared.schemas import PaginatedData


class MarkService:
    def __init__(self, db: AsyncSession):
        self._repo = MarkRepository(db)

    async def list(self, org_id: int, p: PaginationParams) -> PaginatedData[MarkRead]:
        items, total = await self._repo.get_many(org_id, p.offset, p.limit)
        return PaginatedData(items=[MarkRead.model_validate(i) for i in items],
                             total=total, page=p.page, size=p.size,
                             pages=(total + p.size - 1) // p.size if p.size else 0)

    async def get(self, id: int, org_id: int) -> MarkRead:
        obj = await self._repo.get_by_id(id, org_id)
        if not obj: raise not_found("Mark")
        return MarkRead.model_validate(obj)

    async def bulk_upsert(self, org_id: int, payload: MarkBulkCreate) -> list[MarkRead]:
        from app.features.exam.repositories.exam_registration_repo import ExamRegistrationRepository
        from app.shared.exceptions import bad_request
        reg_repo = ExamRegistrationRepository(self._repo._db)

        results = []
        try:
            for entry in payload.entries:
                # Enforce exam registration
                reg = await reg_repo.get_by_enroll_exam(entry.enrollment_id, payload.exam_type_id, org_id)
                if not reg:
                    raise bad_request(f"Enrollment ID {entry.enrollment_id} is not registered for Exam Type ID {payload.exam_type_id}.")

                mark = await self._repo.upsert(
                    org_id,
                    entry.enrollment_id,
                    entry.class_subject_id,
                    payload.exam_type_id,
                    {"marks_obtained": entry.marks_obtained, "is_absent": entry.is_absent},
                )
                results.append(MarkRead.model_validate(mark))
            
            await self._repo._db.commit()
            return results
        except Exception:
            await self._repo._db.rollback()
            raise

    async def get_by_class_subject(
        self, exam_type_id: int, class_subject_id: int, org_id: int
    ) -> list[MarkRead]:
        items = await self._repo.get_by_exam_type_class(exam_type_id, class_subject_id, org_id)
        return [MarkRead.model_validate(i) for i in items]

    async def delete(self, id: int, org_id: int) -> None:
        obj = await self._repo.get_by_id(id, org_id)
        if not obj: raise not_found("Mark")
        await self._repo.soft_delete(obj)
