"""Guardian service."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.academic.repositories.guardian_repo import GuardianRepository
from app.features.academic.repositories.student_repo import StudentRepository
from app.features.academic.schemas import GuardianCreate, GuardianRead, GuardianUpdate
from app.shared.exceptions import not_found


class GuardianService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = GuardianRepository(db)
        self._student_repo = StudentRepository(db)

    async def list_for_student(self, student_id: int, org_id: int) -> list[GuardianRead]:
        if not await self._student_repo.get_by_id(student_id, org_id):
            raise not_found("Student")
        items = await self._repo.get_by_student(student_id, org_id)
        return [GuardianRead.model_validate(i) for i in items]

    async def create_for_student(
        self, student_id: int, org_id: int, payload: GuardianCreate
    ) -> GuardianRead:
        if not await self._student_repo.get_by_id(student_id, org_id):
            raise not_found("Student")
        obj = await self._repo.create_for_student(org_id, student_id, payload.model_dump())
        return GuardianRead.model_validate(obj)

    async def update(self, id: int, org_id: int, payload: GuardianUpdate) -> GuardianRead:
        obj = await self._repo.get_by_id(id, org_id)
        if not obj:
            raise not_found("Guardian")
        obj = await self._repo.update(obj, payload.model_dump(exclude_none=True))
        return GuardianRead.model_validate(obj)

    async def delete(self, id: int, org_id: int) -> None:
        obj = await self._repo.get_by_id(id, org_id)
        if not obj:
            raise not_found("Guardian")
        await self._repo.soft_delete(obj)
