from app.features.academic.models import Class
from app.features.academic.repositories.base_repo import BaseRepo


class ClassRepository(BaseRepo):
    _model = Class
