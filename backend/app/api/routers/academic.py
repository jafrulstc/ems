from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import SessionDep, TenantDep, require_permission
from app.schemas.academic import (
    AcademicYearCreate,
    AcademicYearRead,
    ClassCreate,
    ClassRead,
    DepartmentCreate,
    DepartmentRead,
    SectionCreate,
    SectionRead,
    ShiftCreate,
    ShiftRead,
    SubjectCreate,
    SubjectRead,
    YearlyClassSubjectCreate,
    YearlyClassSubjectRead,
)
from app.services.academic_service import AcademicService

router = APIRouter()

# ── Department ───────────────────────────────────────────
@router.post("/departments", response_model=DepartmentRead, dependencies=[Depends(require_permission("academic:create"))])
async def create_department(session: SessionDep, tenant: TenantDep, dept_in: DepartmentCreate) -> Any:
    return await AcademicService.create_department(session, tenant.id, dept_in)

@router.get("/departments", response_model=list[DepartmentRead], dependencies=[Depends(require_permission("academic:read"))])
async def read_departments(session: SessionDep, tenant: TenantDep, skip: int = 0, limit: int = 100) -> Any:
    return await AcademicService.read_departments(session, skip, limit)

@router.put("/departments/{dept_id}", response_model=DepartmentRead, dependencies=[Depends(require_permission("academic:update"))])
async def update_department(dept_id: str, session: SessionDep, tenant: TenantDep, dept_in: DepartmentCreate) -> Any:
    return await AcademicService.update_department(session, dept_id, dept_in)

@router.delete("/departments/{dept_id}", dependencies=[Depends(require_permission("academic:delete"))])
async def delete_department(dept_id: str, session: SessionDep, tenant: TenantDep) -> Any:
    return await AcademicService.delete_department(session, dept_id)

# ── Academic Year ─────────────────────────────────────────
@router.post("/years", response_model=AcademicYearRead, dependencies=[Depends(require_permission("academic_year:create"))])
async def create_academic_year(session: SessionDep, tenant: TenantDep, year_in: AcademicYearCreate) -> Any:
    return await AcademicService.create_academic_year(session, tenant.id, year_in)

@router.get("/years", response_model=list[AcademicYearRead], dependencies=[Depends(require_permission("academic_year:read"))])
async def read_academic_years(session: SessionDep, tenant: TenantDep, skip: int = 0, limit: int = 100) -> Any:
    return await AcademicService.read_academic_years(session, skip, limit)

@router.put("/years/{year_id}", response_model=AcademicYearRead, dependencies=[Depends(require_permission("academic_year:update"))])
async def update_academic_year(year_id: str, session: SessionDep, tenant: TenantDep, year_in: AcademicYearCreate) -> Any:
    return await AcademicService.update_academic_year(session, year_id, year_in)

@router.delete("/years/{year_id}", dependencies=[Depends(require_permission("academic_year:delete"))])
async def delete_academic_year(year_id: str, session: SessionDep, tenant: TenantDep) -> Any:
    return await AcademicService.delete_academic_year(session, year_id)

# ── Class ─────────────────────────────────────────────────
@router.post("/classes", response_model=ClassRead, dependencies=[Depends(require_permission("class:create"))])
async def create_class(session: SessionDep, tenant: TenantDep, class_in: ClassCreate) -> Any:
    return await AcademicService.create_class(session, tenant.id, class_in)

@router.get("/classes", response_model=list[ClassRead], dependencies=[Depends(require_permission("class:read"))])
async def read_classes(session: SessionDep, tenant: TenantDep, skip: int = 0, limit: int = 100) -> Any:
    return await AcademicService.read_classes(session, skip, limit)

@router.put("/classes/{class_id}", response_model=ClassRead, dependencies=[Depends(require_permission("class:update"))])
async def update_class(class_id: str, session: SessionDep, tenant: TenantDep, class_in: ClassCreate) -> Any:
    return await AcademicService.update_class(session, class_id, class_in)

@router.delete("/classes/{class_id}", dependencies=[Depends(require_permission("class:delete"))])
async def delete_class(class_id: str, session: SessionDep, tenant: TenantDep) -> Any:
    return await AcademicService.delete_class(session, class_id)

# ── Section ───────────────────────────────────────────────
@router.post("/sections", response_model=SectionRead, dependencies=[Depends(require_permission("section:create"))])
async def create_section(session: SessionDep, tenant: TenantDep, section_in: SectionCreate) -> Any:
    return await AcademicService.create_section(session, tenant.id, section_in)

@router.get("/sections", response_model=list[SectionRead], dependencies=[Depends(require_permission("section:read"))])
async def read_sections(session: SessionDep, tenant: TenantDep, skip: int = 0, limit: int = 100) -> Any:
    return await AcademicService.read_sections(session, skip, limit)

@router.put("/sections/{section_id}", response_model=SectionRead, dependencies=[Depends(require_permission("section:update"))])
async def update_section(section_id: str, session: SessionDep, tenant: TenantDep, section_in: SectionCreate) -> Any:
    return await AcademicService.update_section(session, section_id, section_in)

@router.delete("/sections/{section_id}", dependencies=[Depends(require_permission("section:delete"))])
async def delete_section(section_id: str, session: SessionDep, tenant: TenantDep) -> Any:
    return await AcademicService.delete_section(session, section_id)

# ── Subject ───────────────────────────────────────────────
@router.post("/subjects", response_model=SubjectRead, dependencies=[Depends(require_permission("subject:create"))])
async def create_subject(session: SessionDep, tenant: TenantDep, subject_in: SubjectCreate) -> Any:
    return await AcademicService.create_subject(session, tenant.id, subject_in)

@router.get("/subjects", response_model=list[SubjectRead], dependencies=[Depends(require_permission("subject:read"))])
async def read_subjects(session: SessionDep, tenant: TenantDep, skip: int = 0, limit: int = 100) -> Any:
    return await AcademicService.read_subjects(session, skip, limit)

@router.put("/subjects/{subject_id}", response_model=SubjectRead, dependencies=[Depends(require_permission("subject:update"))])
async def update_subject(subject_id: str, session: SessionDep, tenant: TenantDep, subject_in: SubjectCreate) -> Any:
    return await AcademicService.update_subject(session, subject_id, subject_in)

@router.delete("/subjects/{subject_id}", dependencies=[Depends(require_permission("subject:delete"))])
async def delete_subject(subject_id: str, session: SessionDep, tenant: TenantDep) -> Any:
    return await AcademicService.delete_subject(session, subject_id)

# ── Shift ─────────────────────────────────────────────────
@router.post("/shifts", response_model=ShiftRead, dependencies=[Depends(require_permission("academic:create"))])
async def create_shift(session: SessionDep, tenant: TenantDep, shift_in: ShiftCreate) -> Any:
    return await AcademicService.create_shift(session, tenant.id, shift_in)

@router.get("/shifts", response_model=list[ShiftRead], dependencies=[Depends(require_permission("academic:read"))])
async def read_shifts(session: SessionDep, tenant: TenantDep, skip: int = 0, limit: int = 100) -> Any:
    return await AcademicService.read_shifts(session, skip, limit)

@router.put("/shifts/{shift_id}", response_model=ShiftRead, dependencies=[Depends(require_permission("academic:update"))])
async def update_shift(shift_id: str, session: SessionDep, tenant: TenantDep, shift_in: ShiftCreate) -> Any:
    return await AcademicService.update_shift(session, shift_id, shift_in)

@router.delete("/shifts/{shift_id}", dependencies=[Depends(require_permission("academic:delete"))])
async def delete_shift(shift_id: str, session: SessionDep, tenant: TenantDep) -> Any:
    return await AcademicService.delete_shift(session, shift_id)

# ── Yearly Class Subject ───────────────────────────────────
@router.post("/yearly-class-subjects", response_model=YearlyClassSubjectRead, dependencies=[Depends(require_permission("academic:create"))])
async def create_yearly_class_subject(session: SessionDep, tenant: TenantDep, ycs_in: YearlyClassSubjectCreate) -> Any:
    return await AcademicService.create_yearly_class_subject(session, tenant.id, ycs_in)

@router.get("/yearly-class-subjects", response_model=list[YearlyClassSubjectRead], dependencies=[Depends(require_permission("academic:read"))])
async def read_yearly_class_subjects(session: SessionDep, tenant: TenantDep, skip: int = 0, limit: int = 100) -> Any:
    return await AcademicService.read_yearly_class_subjects(session, skip, limit)

@router.put("/yearly-class-subjects/{ycs_id}", response_model=YearlyClassSubjectRead, dependencies=[Depends(require_permission("academic:update"))])
async def update_yearly_class_subject(ycs_id: str, session: SessionDep, tenant: TenantDep, ycs_in: YearlyClassSubjectCreate) -> Any:
    return await AcademicService.update_yearly_class_subject(session, ycs_id, ycs_in)

@router.delete("/yearly-class-subjects/{ycs_id}", dependencies=[Depends(require_permission("academic:delete"))])
async def delete_yearly_class_subject(ycs_id: str, session: SessionDep, tenant: TenantDep) -> Any:
    return await AcademicService.delete_yearly_class_subject(session, ycs_id)
