from app.features.exam.models import ExamType
from app.shared.base_repo import BaseRepo


class ExamTypeRepository(BaseRepo):
    _model = ExamType
