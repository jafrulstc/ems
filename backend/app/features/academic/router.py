"""
Academic feature router. Prefix: /api/v1/academic
"""
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_organization_id, require_permission
from app.features.academic.schemas import (
    ClassCreate, ClassRead, ClassUpdate,
    ClassSubjectCreate, ClassSubjectRead,
    EnrollmentCreate, EnrollmentRead, EnrollmentUpdate,
    GuardianCreate, GuardianRead, GuardianUpdate,
    SectionCreate, SectionRead, SectionUpdate,
    StudentCreate, StudentRead, StudentUpdate,
    SubjectCreate, SubjectRead, SubjectUpdate,
)
from app.features.academic.services.class_service import ClassService
from app.features.academic.services.enrollment_service import EnrollmentService
from app.features.academic.services.guardian_service import GuardianService
from app.features.academic.services.section_service import SectionService
from app.features.academic.services.student_service import StudentService
from app.features.academic.services.subject_service import SubjectService
from app.shared.pagination import PaginationParams, pagination_params
from app.shared.schemas import APIResponse, PaginatedResponse, ok, paginated

router = APIRouter()

# ── Classes ───────────────────────────────────────────────────────────────────

@router.get("/classes", response_model=PaginatedResponse[ClassRead], tags=["Classes"])
async def list_classes(p: PaginationParams = Depends(pagination_params),
                       org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                       _=Depends(require_permission("academic.classes.view"))):
    data = await ClassService(db).list(org_id, p)
    return paginated(data.items, data.total, data.page, data.size)

@router.post("/classes", response_model=APIResponse[ClassRead], status_code=201, tags=["Classes"])
async def create_class(payload: ClassCreate, org_id: int = Depends(get_organization_id),
                       db: AsyncSession = Depends(get_db),
                       _=Depends(require_permission("academic.classes.create"))):
    return ok(await ClassService(db).create(org_id, payload), "Class created.")

@router.get("/classes/{id}", response_model=APIResponse[ClassRead], tags=["Classes"])
async def get_class(id: int, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                    _=Depends(require_permission("academic.classes.view"))):
    return ok(await ClassService(db).get(id, org_id))

@router.put("/classes/{id}", response_model=APIResponse[ClassRead], tags=["Classes"])
async def update_class(id: int, payload: ClassUpdate, org_id: int = Depends(get_organization_id),
                       db: AsyncSession = Depends(get_db),
                       _=Depends(require_permission("academic.classes.edit"))):
    return ok(await ClassService(db).update(id, org_id, payload))

@router.delete("/classes/{id}", response_model=APIResponse[None], tags=["Classes"])
async def delete_class(id: int, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                       _=Depends(require_permission("academic.classes.delete"))):
    await ClassService(db).delete(id, org_id)
    return ok(None, "Class deleted.")

# ── Sections ──────────────────────────────────────────────────────────────────

@router.get("/sections", response_model=PaginatedResponse[SectionRead], tags=["Sections"])
async def list_sections(p: PaginationParams = Depends(pagination_params),
                        org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                        _=Depends(require_permission("academic.sections.view"))):
    data = await SectionService(db).list(org_id, p)
    return paginated(data.items, data.total, data.page, data.size)

@router.post("/sections", response_model=APIResponse[SectionRead], status_code=201, tags=["Sections"])
async def create_section(payload: SectionCreate, org_id: int = Depends(get_organization_id),
                         db: AsyncSession = Depends(get_db),
                         _=Depends(require_permission("academic.sections.create"))):
    return ok(await SectionService(db).create(org_id, payload), "Section created.")

@router.get("/sections/{id}", response_model=APIResponse[SectionRead], tags=["Sections"])
async def get_section(id: int, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                      _=Depends(require_permission("academic.sections.view"))):
    return ok(await SectionService(db).get(id, org_id))

@router.put("/sections/{id}", response_model=APIResponse[SectionRead], tags=["Sections"])
async def update_section(id: int, payload: SectionUpdate, org_id: int = Depends(get_organization_id),
                         db: AsyncSession = Depends(get_db),
                         _=Depends(require_permission("academic.sections.edit"))):
    return ok(await SectionService(db).update(id, org_id, payload))

@router.delete("/sections/{id}", response_model=APIResponse[None], tags=["Sections"])
async def delete_section(id: int, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                         _=Depends(require_permission("academic.sections.delete"))):
    await SectionService(db).delete(id, org_id)
    return ok(None, "Section deleted.")

# ── Subjects ──────────────────────────────────────────────────────────────────

@router.get("/subjects", response_model=PaginatedResponse[SubjectRead], tags=["Subjects"])
async def list_subjects(p: PaginationParams = Depends(pagination_params),
                        org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                        _=Depends(require_permission("academic.subjects.view"))):
    data = await SubjectService(db).list(org_id, p)
    return paginated(data.items, data.total, data.page, data.size)

@router.post("/subjects", response_model=APIResponse[SubjectRead], status_code=201, tags=["Subjects"])
async def create_subject(payload: SubjectCreate, org_id: int = Depends(get_organization_id),
                         db: AsyncSession = Depends(get_db),
                         _=Depends(require_permission("academic.subjects.create"))):
    return ok(await SubjectService(db).create(org_id, payload), "Subject created.")

@router.get("/subjects/{id}", response_model=APIResponse[SubjectRead], tags=["Subjects"])
async def get_subject(id: int, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                      _=Depends(require_permission("academic.subjects.view"))):
    return ok(await SubjectService(db).get(id, org_id))

@router.put("/subjects/{id}", response_model=APIResponse[SubjectRead], tags=["Subjects"])
async def update_subject(id: int, payload: SubjectUpdate, org_id: int = Depends(get_organization_id),
                         db: AsyncSession = Depends(get_db),
                         _=Depends(require_permission("academic.subjects.edit"))):
    return ok(await SubjectService(db).update(id, org_id, payload))

@router.delete("/subjects/{id}", response_model=APIResponse[None], tags=["Subjects"])
async def delete_subject(id: int, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                         _=Depends(require_permission("academic.subjects.delete"))):
    await SubjectService(db).delete(id, org_id)
    return ok(None, "Subject deleted.")

# ── Class Subjects ────────────────────────────────────────────────────────────

@router.get("/class-subjects", response_model=PaginatedResponse[ClassSubjectRead], tags=["Class Subjects"])
async def list_class_subjects(p: PaginationParams = Depends(pagination_params),
                               org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                               _=Depends(require_permission("academic.class_subjects.view"))):
    from app.features.academic.repositories.class_subject_repo import ClassSubjectRepository
    from app.features.academic.repositories.base_repo import BaseRepo
    repo = ClassSubjectRepository(db)
    items, total = await repo.get_many(org_id, p.offset, p.limit)
    return paginated([ClassSubjectRead.model_validate(i) for i in items], total, p.page, p.size)

@router.post("/class-subjects", response_model=APIResponse[ClassSubjectRead], status_code=201, tags=["Class Subjects"])
async def create_class_subject(payload: ClassSubjectCreate, org_id: int = Depends(get_organization_id),
                                db: AsyncSession = Depends(get_db),
                                _=Depends(require_permission("academic.class_subjects.create"))):
    svc = EnrollmentService(db)
    return ok(await svc.class_subject_service(org_id, payload), "Class subject mapped.")

# ── Students ──────────────────────────────────────────────────────────────────

@router.get("/students", response_model=PaginatedResponse[StudentRead], tags=["Students"])
async def list_students(q: Optional[str] = None, p: PaginationParams = Depends(pagination_params),
                        org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                        _=Depends(require_permission("academic.students.view"))):
    data = await StudentService(db).list(org_id, p, q or "")
    return paginated(data.items, data.total, data.page, data.size)

@router.post("/students", response_model=APIResponse[StudentRead], status_code=201, tags=["Students"])
async def create_student(payload: StudentCreate, org_id: int = Depends(get_organization_id),
                         db: AsyncSession = Depends(get_db),
                         _=Depends(require_permission("academic.students.create"))):
    return ok(await StudentService(db).create(org_id, payload), "Student created.")

@router.get("/students/{id}", response_model=APIResponse[StudentRead], tags=["Students"])
async def get_student(id: int, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                      _=Depends(require_permission("academic.students.view"))):
    return ok(await StudentService(db).get(id, org_id))

@router.put("/students/{id}", response_model=APIResponse[StudentRead], tags=["Students"])
async def update_student(id: int, payload: StudentUpdate, org_id: int = Depends(get_organization_id),
                         db: AsyncSession = Depends(get_db),
                         _=Depends(require_permission("academic.students.edit"))):
    return ok(await StudentService(db).update(id, org_id, payload))

@router.delete("/students/{id}", response_model=APIResponse[None], tags=["Students"])
async def delete_student(id: int, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                         _=Depends(require_permission("academic.students.delete"))):
    await StudentService(db).delete(id, org_id)
    return ok(None, "Student deleted.")

# ── Guardians ─────────────────────────────────────────────────────────────────

@router.get("/students/{student_id}/guardians", response_model=APIResponse[list[GuardianRead]], tags=["Guardians"])
async def list_guardians(student_id: int, org_id: int = Depends(get_organization_id),
                         db: AsyncSession = Depends(get_db),
                         _=Depends(require_permission("academic.students.view"))):
    return ok(await GuardianService(db).list_for_student(student_id, org_id))

@router.post("/students/{student_id}/guardians", response_model=APIResponse[GuardianRead], status_code=201, tags=["Guardians"])
async def create_guardian(student_id: int, payload: GuardianCreate,
                          org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                          _=Depends(require_permission("academic.students.edit"))):
    return ok(await GuardianService(db).create_for_student(student_id, org_id, payload), "Guardian added.")

@router.put("/guardians/{id}", response_model=APIResponse[GuardianRead], tags=["Guardians"])
async def update_guardian(id: int, payload: GuardianUpdate,
                          org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                          _=Depends(require_permission("academic.students.edit"))):
    return ok(await GuardianService(db).update(id, org_id, payload))

@router.delete("/guardians/{id}", response_model=APIResponse[None], tags=["Guardians"])
async def delete_guardian(id: int, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                          _=Depends(require_permission("academic.students.edit"))):
    await GuardianService(db).delete(id, org_id)
    return ok(None, "Guardian deleted.")

# ── Enrollments ───────────────────────────────────────────────────────────────

@router.get("/enrollments", response_model=PaginatedResponse[EnrollmentRead], tags=["Enrollments"])
async def list_enrollments(p: PaginationParams = Depends(pagination_params),
                           org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                           _=Depends(require_permission("academic.enrollments.view"))):
    data = await EnrollmentService(db).list(org_id, p)
    return paginated(data.items, data.total, data.page, data.size)

@router.post("/enrollments", response_model=APIResponse[EnrollmentRead], status_code=201, tags=["Enrollments"])
async def create_enrollment(payload: EnrollmentCreate, org_id: int = Depends(get_organization_id),
                            db: AsyncSession = Depends(get_db),
                            _=Depends(require_permission("academic.enrollments.create"))):
    return ok(await EnrollmentService(db).create(org_id, payload), "Enrollment created.")

@router.get("/enrollments/{id}", response_model=APIResponse[EnrollmentRead], tags=["Enrollments"])
async def get_enrollment(id: int, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                         _=Depends(require_permission("academic.enrollments.view"))):
    return ok(await EnrollmentService(db).get(id, org_id))

@router.put("/enrollments/{id}", response_model=APIResponse[EnrollmentRead], tags=["Enrollments"])
async def update_enrollment(id: int, payload: EnrollmentUpdate, org_id: int = Depends(get_organization_id),
                            db: AsyncSession = Depends(get_db),
                            _=Depends(require_permission("academic.enrollments.edit"))):
    return ok(await EnrollmentService(db).update(id, org_id, payload))

@router.delete("/enrollments/{id}", response_model=APIResponse[None], tags=["Enrollments"])
async def delete_enrollment(id: int, org_id: int = Depends(get_organization_id), db: AsyncSession = Depends(get_db),
                            _=Depends(require_permission("academic.enrollments.delete"))):
    await EnrollmentService(db).delete(id, org_id)
    return ok(None, "Enrollment deleted.")
