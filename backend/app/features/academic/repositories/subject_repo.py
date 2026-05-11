from app.features.academic.models import Subject
from app.shared.base_repo import BaseRepo


class SubjectRepository(BaseRepo):
    _model = Subject
