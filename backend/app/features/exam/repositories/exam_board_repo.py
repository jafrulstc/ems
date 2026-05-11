from app.features.exam.models import ExamBoard
from app.shared.base_repo import BaseRepo


class ExamBoardRepository(BaseRepo):
    _model = ExamBoard
