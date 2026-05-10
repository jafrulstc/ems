from app.features.academic.repositories.subject_repo import SubjectRepository
from app.features.academic.schemas import SubjectRead
from app.features.academic.services.base_service import BaseAcademicService


class SubjectService(BaseAcademicService):
    _repo_class = SubjectRepository
    _schema_read = SubjectRead
    _resource_name = "Subject"
