from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from app.api.deps import SessionDep, TenantDep, require_permission
from app.models.academic import (
    AcademicClass,
    AcademicYear,
    Department,
    Section,
    Shift,
    Subject,
    YearlyClassSubject,
)
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

router = APIRouter()

# ── Department ───────────────────────────────────────────
@router.post("/departments", response_model=DepartmentRead, dependencies=[Depends(require_permission("academic:create"))])
async def create_department(session: SessionDep, tenant: TenantDep, dept_in: DepartmentCreate) -> Any:
    db = Department(**dept_in.model_dump(), tenant_id=tenant.id)
    session.add(db); await session.commit(); await session.refresh(db); return db

@router.get("/departments", response_model=list[DepartmentRead], dependencies=[Depends(require_permission("academic:read"))])
async def read_departments(session: SessionDep, tenant: TenantDep, skip: int = 0, limit: int = 100) -> Any:
    return (await session.execute(select(Department).offset(skip).limit(limit))).scalars().all()

@router.put("/departments/{dept_id}", response_model=DepartmentRead, dependencies=[Depends(require_permission("academic:update"))])
async def update_department(dept_id: str, session: SessionDep, tenant: TenantDep, dept_in: DepartmentCreate) -> Any:
    db = (await session.execute(select(Department).where(Department.id == dept_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Not found")
    for k, v in dept_in.model_dump().items(): setattr(db, k, v)
    await session.commit(); await session.refresh(db); return db

@router.delete("/departments/{dept_id}", dependencies=[Depends(require_permission("academic:delete"))])
async def delete_department(dept_id: str, session: SessionDep, tenant: TenantDep) -> Any:
    db = (await session.execute(select(Department).where(Department.id == dept_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Not found")
    db.is_deleted = True; await session.commit(); return {"message": "Deleted"}

# ── Academic Year ─────────────────────────────────────────
@router.post("/years", response_model=AcademicYearRead, dependencies=[Depends(require_permission("academic_year:create"))])
async def create_academic_year(session: SessionDep, tenant: TenantDep, year_in: AcademicYearCreate) -> Any:
    db = AcademicYear(**year_in.model_dump(), tenant_id=tenant.id)
    session.add(db); await session.commit(); await session.refresh(db); return db

@router.get("/years", response_model=list[AcademicYearRead], dependencies=[Depends(require_permission("academic_year:read"))])
async def read_academic_years(session: SessionDep, tenant: TenantDep, skip: int = 0, limit: int = 100) -> Any:
    return (await session.execute(select(AcademicYear).offset(skip).limit(limit))).scalars().all()

@router.put("/years/{year_id}", response_model=AcademicYearRead, dependencies=[Depends(require_permission("academic_year:update"))])
async def update_academic_year(year_id: str, session: SessionDep, tenant: TenantDep, year_in: AcademicYearCreate) -> Any:
    db = (await session.execute(select(AcademicYear).where(AcademicYear.id == year_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Not found")
    for k, v in year_in.model_dump().items(): setattr(db, k, v)
    await session.commit(); await session.refresh(db); return db

@router.delete("/years/{year_id}", dependencies=[Depends(require_permission("academic_year:delete"))])
async def delete_academic_year(year_id: str, session: SessionDep, tenant: TenantDep) -> Any:
    db = (await session.execute(select(AcademicYear).where(AcademicYear.id == year_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Not found")
    db.is_deleted = True; await session.commit(); return {"message": "Deleted"}

# ── Class ─────────────────────────────────────────────────
@router.post("/classes", response_model=ClassRead, dependencies=[Depends(require_permission("class:create"))])
async def create_class(session: SessionDep, tenant: TenantDep, class_in: ClassCreate) -> Any:
    db = AcademicClass(**class_in.model_dump(), tenant_id=tenant.id)
    session.add(db); await session.commit(); await session.refresh(db); return db

@router.get("/classes", response_model=list[ClassRead], dependencies=[Depends(require_permission("class:read"))])
async def read_classes(session: SessionDep, tenant: TenantDep, skip: int = 0, limit: int = 100) -> Any:
    classes = (await session.execute(select(AcademicClass).offset(skip).limit(limit))).scalars().all()
    # Populate department_name
    dept_ids = [c.department_id for c in classes if c.department_id]
    dept_map = {}
    if dept_ids:
        depts = (await session.execute(select(Department).where(Department.id.in_(dept_ids)))).scalars().all()
        dept_map = {d.id: d.name for d in depts}
    
    result = []
    for c in classes:
        c_dict = ClassRead.model_validate(c)
        if c.department_id and c.department_id in dept_map:
            c_dict.department_name = dept_map[c.department_id]
        result.append(c_dict)
    return result

@router.put("/classes/{class_id}", response_model=ClassRead, dependencies=[Depends(require_permission("class:update"))])
async def update_class(class_id: str, session: SessionDep, tenant: TenantDep, class_in: ClassCreate) -> Any:
    db = (await session.execute(select(AcademicClass).where(AcademicClass.id == class_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Not found")
    for k, v in class_in.model_dump().items(): setattr(db, k, v)
    await session.commit(); await session.refresh(db); return db

@router.delete("/classes/{class_id}", dependencies=[Depends(require_permission("class:delete"))])
async def delete_class(class_id: str, session: SessionDep, tenant: TenantDep) -> Any:
    db = (await session.execute(select(AcademicClass).where(AcademicClass.id == class_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Not found")
    db.is_deleted = True; await session.commit(); return {"message": "Deleted"}

# ── Section ───────────────────────────────────────────────
@router.post("/sections", response_model=SectionRead, dependencies=[Depends(require_permission("section:create"))])
async def create_section(session: SessionDep, tenant: TenantDep, section_in: SectionCreate) -> Any:
    db = Section(**section_in.model_dump(), tenant_id=tenant.id)
    session.add(db); await session.commit(); await session.refresh(db); return db

@router.get("/sections", response_model=list[SectionRead], dependencies=[Depends(require_permission("section:read"))])
async def read_sections(session: SessionDep, tenant: TenantDep, skip: int = 0, limit: int = 100) -> Any:
    return (await session.execute(select(Section).offset(skip).limit(limit))).scalars().all()

@router.put("/sections/{section_id}", response_model=SectionRead, dependencies=[Depends(require_permission("section:update"))])
async def update_section(section_id: str, session: SessionDep, tenant: TenantDep, section_in: SectionCreate) -> Any:
    db = (await session.execute(select(Section).where(Section.id == section_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Not found")
    for k, v in section_in.model_dump().items(): setattr(db, k, v)
    await session.commit(); await session.refresh(db); return db

@router.delete("/sections/{section_id}", dependencies=[Depends(require_permission("section:delete"))])
async def delete_section(section_id: str, session: SessionDep, tenant: TenantDep) -> Any:
    db = (await session.execute(select(Section).where(Section.id == section_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Not found")
    db.is_deleted = True; await session.commit(); return {"message": "Deleted"}

# ── Subject ───────────────────────────────────────────────
@router.post("/subjects", response_model=SubjectRead, dependencies=[Depends(require_permission("subject:create"))])
async def create_subject(session: SessionDep, tenant: TenantDep, subject_in: SubjectCreate) -> Any:
    db = Subject(**subject_in.model_dump(), tenant_id=tenant.id)
    session.add(db); await session.commit(); await session.refresh(db); return db

@router.get("/subjects", response_model=list[SubjectRead], dependencies=[Depends(require_permission("subject:read"))])
async def read_subjects(session: SessionDep, tenant: TenantDep, skip: int = 0, limit: int = 100) -> Any:
    return (await session.execute(select(Subject).offset(skip).limit(limit))).scalars().all()

@router.put("/subjects/{subject_id}", response_model=SubjectRead, dependencies=[Depends(require_permission("subject:update"))])
async def update_subject(subject_id: str, session: SessionDep, tenant: TenantDep, subject_in: SubjectCreate) -> Any:
    db = (await session.execute(select(Subject).where(Subject.id == subject_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Not found")
    for k, v in subject_in.model_dump().items(): setattr(db, k, v)
    await session.commit(); await session.refresh(db); return db

@router.delete("/subjects/{subject_id}", dependencies=[Depends(require_permission("subject:delete"))])
async def delete_subject(subject_id: str, session: SessionDep, tenant: TenantDep) -> Any:
    db = (await session.execute(select(Subject).where(Subject.id == subject_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Not found")
    db.is_deleted = True; await session.commit(); return {"message": "Deleted"}

# ── Shift ─────────────────────────────────────────────────
@router.post("/shifts", response_model=ShiftRead, dependencies=[Depends(require_permission("academic:create"))])
async def create_shift(session: SessionDep, tenant: TenantDep, shift_in: ShiftCreate) -> Any:
    db = Shift(**shift_in.model_dump(), tenant_id=tenant.id)
    session.add(db); await session.commit(); await session.refresh(db); return db

@router.get("/shifts", response_model=list[ShiftRead], dependencies=[Depends(require_permission("academic:read"))])
async def read_shifts(session: SessionDep, tenant: TenantDep, skip: int = 0, limit: int = 100) -> Any:
    return (await session.execute(select(Shift).offset(skip).limit(limit))).scalars().all()

@router.put("/shifts/{shift_id}", response_model=ShiftRead, dependencies=[Depends(require_permission("academic:update"))])
async def update_shift(shift_id: str, session: SessionDep, tenant: TenantDep, shift_in: ShiftCreate) -> Any:
    db = (await session.execute(select(Shift).where(Shift.id == shift_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Not found")
    for k, v in shift_in.model_dump().items(): setattr(db, k, v)
    await session.commit(); await session.refresh(db); return db

@router.delete("/shifts/{shift_id}", dependencies=[Depends(require_permission("academic:delete"))])
async def delete_shift(shift_id: str, session: SessionDep, tenant: TenantDep) -> Any:
    db = (await session.execute(select(Shift).where(Shift.id == shift_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Not found")
    db.is_deleted = True; await session.commit(); return {"message": "Deleted"}

# ── Yearly Class Subject ───────────────────────────────────
@router.post("/yearly-class-subjects", response_model=YearlyClassSubjectRead, dependencies=[Depends(require_permission("academic:create"))])
async def create_yearly_class_subject(session: SessionDep, tenant: TenantDep, ycs_in: YearlyClassSubjectCreate) -> Any:
    db = YearlyClassSubject(**ycs_in.model_dump(), tenant_id=tenant.id)
    session.add(db); await session.commit(); await session.refresh(db); return db

@router.get("/yearly-class-subjects", response_model=list[YearlyClassSubjectRead], dependencies=[Depends(require_permission("academic:read"))])
async def read_yearly_class_subjects(session: SessionDep, tenant: TenantDep, skip: int = 0, limit: int = 100) -> Any:
    return (await session.execute(select(YearlyClassSubject).offset(skip).limit(limit))).scalars().all()

@router.put("/yearly-class-subjects/{ycs_id}", response_model=YearlyClassSubjectRead, dependencies=[Depends(require_permission("academic:update"))])
async def update_yearly_class_subject(ycs_id: str, session: SessionDep, tenant: TenantDep, ycs_in: YearlyClassSubjectCreate) -> Any:
    db = (await session.execute(select(YearlyClassSubject).where(YearlyClassSubject.id == ycs_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Not found")
    for k, v in ycs_in.model_dump().items(): setattr(db, k, v)
    await session.commit(); await session.refresh(db); return db

@router.delete("/yearly-class-subjects/{ycs_id}", dependencies=[Depends(require_permission("academic:delete"))])
async def delete_yearly_class_subject(ycs_id: str, session: SessionDep, tenant: TenantDep) -> Any:
    db = (await session.execute(select(YearlyClassSubject).where(YearlyClassSubject.id == ycs_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Not found")
    db.is_deleted = True; await session.commit(); return {"message": "Deleted"}
