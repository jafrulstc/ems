from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.academic.models import ClassSubject
from app.features.academic.repositories.base_repo import BaseRepo


class ClassSubjectRepository(BaseRepo):
    _model = ClassSubject

    async def get_by_class(self, class_id: int, org_id: int) -> list[ClassSubject]:
        r = await self._db.execute(
            select(ClassSubject).where(
                ClassSubject.class_id == class_id,
                ClassSubject.organization_id == org_id,
                ClassSubject.is_deleted.is_(False),
            )
        )
        return list(r.scalars().all())

    async def get_by_class_subject(
        self, class_id: int, subject_id: int, org_id: int
    ) -> Optional[ClassSubject]:
        r = await self._db.execute(
            select(ClassSubject).where(
                ClassSubject.class_id == class_id,
                ClassSubject.subject_id == subject_id,
                ClassSubject.organization_id == org_id,
                ClassSubject.is_deleted.is_(False),
            )
        )
        return r.scalar_one_or_none()
