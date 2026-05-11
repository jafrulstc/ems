from app.features.academic.models import Class
from app.shared.base_repo import BaseRepo


class ClassRepository(BaseRepo):
    _model = Class
