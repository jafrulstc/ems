from app.features.exam.models import ExamType
from app.features.exam.repositories.base_repo import ExamBaseRepo


class ExamTypeRepository(ExamBaseRepo):
    _model = ExamType
