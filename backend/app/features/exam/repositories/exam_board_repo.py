from app.features.exam.models import ExamBoard
from app.features.exam.repositories.base_repo import ExamBaseRepo


class ExamBoardRepository(ExamBaseRepo):
    _model = ExamBoard
