"""Enrollment service — enforces one active enrollment per student per academic year."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.academic.enrollment_models import Enrollment
from app.features.academic.repositories.enrollment_repo import EnrollmentRepository
from app.features.academic.schemas import EnrollmentCreate, EnrollmentRead, EnrollmentUpdate
from app.shared.exceptions import bad_request, not_found
from app.shared.pagination import PaginationParams
from app.shared.schemas import PaginatedData


class EnrollmentService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = EnrollmentRepository(db)

    async def list(self, org_id: int, p: PaginationParams) -> PaginatedData[EnrollmentRead]:
        items, total = await self._repo.get_many(org_id, p.offset, p.limit)
        return PaginatedData(
            items=[EnrollmentRead.model_validate(i) for i in items],
            total=total, page=p.page, size=p.size,
            pages=(total + p.size - 1) // p.size if p.size else 0,
        )

    async def get(self, id: int, org_id: int) -> EnrollmentRead:
        obj = await self._repo.get_by_id(id, org_id)
        if not obj:
            raise not_found("Enrollment")
        return EnrollmentRead.model_validate(obj)

    async def create(self, org_id: int, payload: EnrollmentCreate) -> EnrollmentRead:
        existing = await self._repo.get_active_by_student_year(
            payload.student_id, payload.academic_year_id, org_id
        )
        if existing:
            raise bad_request(
                "Student already has an active enrollment for this academic year. "
                "Deactivate the existing enrollment before creating a new one."
            )
        obj = await self._repo.create(org_id, payload.model_dump())
        return EnrollmentRead.model_validate(obj)

    async def update(self, id: int, org_id: int, payload: EnrollmentUpdate) -> EnrollmentRead:
        obj = await self._repo.get_by_id(id, org_id)
        if not obj:
            raise not_found("Enrollment")
        obj = await self._repo.update(obj, payload.model_dump(exclude_none=True))
        return EnrollmentRead.model_validate(obj)

    async def delete(self, id: int, org_id: int) -> None:
        obj = await self._repo.get_by_id(id, org_id)
        if not obj:
            raise not_found("Enrollment")
        await self._repo.soft_delete(obj)

    async def class_subject_service(self, org_id: int, payload):
        """ClassSubject create — convenience wrapper used from router."""
        from app.features.academic.repositories.class_subject_repo import ClassSubjectRepository
        from app.features.academic.schemas import ClassSubjectRead
        repo = ClassSubjectRepository(self._repo._db)
        existing = await repo.get_by_class_subject(
            payload.class_id, payload.subject_id, org_id
        )
        if existing:
            from app.shared.exceptions import conflict
            raise conflict("This subject is already mapped to the class.")
        obj = await repo.create(org_id, payload.model_dump())
        return ClassSubjectRead.model_validate(obj)
