from app.features.academic.repositories.section_repo import SectionRepository
from app.features.academic.schemas import SectionRead
from app.features.academic.services.base_service import BaseAcademicService


class SectionService(BaseAcademicService):
    _repo_class = SectionRepository
    _schema_read = SectionRead
    _resource_name = "Section"
