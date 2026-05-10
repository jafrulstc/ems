from app.features.academic.repositories.class_repo import ClassRepository
from app.features.academic.schemas import ClassRead
from app.features.academic.services.base_service import BaseAcademicService


class ClassService(BaseAcademicService):
    _repo_class = ClassRepository
    _schema_read = ClassRead
    _resource_name = "Class"
