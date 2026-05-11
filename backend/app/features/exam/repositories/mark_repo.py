"""Mark repository — supports upsert and joins with class_subjects for full_marks."""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.exam.models import Mark
from app.shared.base_repo import BaseRepo


class MarkRepository(BaseRepo):
    _model = Mark

    async def get_by_unique_key(
        self, enrollment_id: int, class_subject_id: int, exam_type_id: int, org_id: int
    ) -> Optional[Mark]:
        r = await self._db.execute(
            select(Mark).where(
                Mark.enrollment_id == enrollment_id,
                Mark.class_subject_id == class_subject_id,
                Mark.exam_type_id == exam_type_id,
                Mark.organization_id == org_id,
                Mark.is_deleted.is_(False),
            )
        )
        return r.scalar_one_or_none()

    async def upsert(
        self, org_id: int, enrollment_id: int,
        class_subject_id: int, exam_type_id: int, data: dict
    ) -> Mark:
        obj = await self.get_by_unique_key(enrollment_id, class_subject_id, exam_type_id, org_id)
        if obj:
            return await self.update(obj, data)
        full_data = {
            "enrollment_id": enrollment_id,
            "class_subject_id": class_subject_id,
            "exam_type_id": exam_type_id,
            **data,
        }
        return await self.create(org_id, full_data)

    async def get_for_result(
        self, enrollment_id: int, exam_type_id: int, org_id: int
    ) -> list[tuple]:
        """Returns list of (Mark, full_marks) tuples for result computation."""
        from app.features.academic.models import ClassSubject
        stmt = (
            select(Mark, ClassSubject.full_marks, ClassSubject.pass_marks)
            .join(ClassSubject, Mark.class_subject_id == ClassSubject.id)
            .where(
                Mark.enrollment_id == enrollment_id,
                Mark.exam_type_id == exam_type_id,
                Mark.organization_id == org_id,
                Mark.is_deleted.is_(False),
            )
        )
        r = await self._db.execute(stmt)
        return list(r.all())

    async def get_by_exam_type_class(
        self, exam_type_id: int, class_subject_id: int, org_id: int
    ) -> list[Mark]:
        r = await self._db.execute(
            select(Mark).where(
                Mark.exam_type_id == exam_type_id,
                Mark.class_subject_id == class_subject_id,
                Mark.organization_id == org_id,
                Mark.is_deleted.is_(False),
            )
        )
        return list(r.scalars().all())
