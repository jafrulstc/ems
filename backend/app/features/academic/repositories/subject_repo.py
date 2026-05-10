from app.features.academic.models import Subject
from app.features.academic.repositories.base_repo import BaseRepo


class SubjectRepository(BaseRepo):
    _model = Subject
