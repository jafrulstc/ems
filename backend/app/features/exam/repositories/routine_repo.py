from sqlalchemy import select
from app.features.exam.models import ExamRoutine
from app.features.exam.repositories.base_repo import ExamBaseRepo


class RoutineRepository(ExamBaseRepo):
    _model = ExamRoutine

    async def get_by_exam_type(self, exam_type_id: int, org_id: int) -> list[ExamRoutine]:
        r = await self._db.execute(
            select(ExamRoutine).where(
                ExamRoutine.exam_type_id == exam_type_id,
                ExamRoutine.organization_id == org_id,
                ExamRoutine.is_deleted.is_(False),
            ).order_by(ExamRoutine.exam_date, ExamRoutine.start_time)
        )
        return list(r.scalars().all())
