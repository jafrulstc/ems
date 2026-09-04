import uuid
from typing import Any

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
    ClassCreate,
    ClassRead,
    DepartmentCreate,
    SectionCreate,
    ShiftCreate,
    SubjectCreate,
    YearlyClassSubjectCreate,
)


class AcademicService:
    # ── Department ───────────────────────────────────────────
    @staticmethod
    async def create_department(session: AsyncSession, tenant_id: uuid.UUID, dept_in: DepartmentCreate) -> Any:
        db = Department(**dept_in.model_dump(), tenant_id=tenant_id)
        session.add(db)
        await session.commit()
        await session.refresh(db)
        return db

    @staticmethod
    async def read_departments(session: AsyncSession, skip: int = 0, limit: int = 100) -> Any:
        return (await session.execute(select(Department).offset(skip).limit(limit))).scalars().all()

    @staticmethod
    async def update_department(session: AsyncSession, dept_id: str, dept_in: DepartmentCreate) -> Any:
        db = (await session.execute(select(Department).where(Department.id == dept_id))).scalar_one_or_none()
        if not db:
            raise HTTPException(status_code=404, detail="Not found")
        for k, v in dept_in.model_dump().items():
            setattr(db, k, v)
        await session.commit()
        await session.refresh(db)
        return db

    @staticmethod
    async def delete_department(session: AsyncSession, dept_id: str) -> Any:
        db = (await session.execute(select(Department).where(Department.id == dept_id))).scalar_one_or_none()
        if not db:
            raise HTTPException(status_code=404, detail="Not found")
        db.is_deleted = True
        await session.commit()
        return {"message": "Deleted"}

    # ── Academic Year ─────────────────────────────────────────
    @staticmethod
    async def create_academic_year(session: AsyncSession, tenant_id: uuid.UUID, year_in: AcademicYearCreate) -> Any:
        db = AcademicYear(**year_in.model_dump(), tenant_id=tenant_id)
        session.add(db)
        await session.commit()
        await session.refresh(db)
        return db

    @staticmethod
    async def read_academic_years(session: AsyncSession, skip: int = 0, limit: int = 100) -> Any:
        return (await session.execute(select(AcademicYear).offset(skip).limit(limit))).scalars().all()

    @staticmethod
    async def update_academic_year(session: AsyncSession, year_id: str, year_in: AcademicYearCreate) -> Any:
        db = (await session.execute(select(AcademicYear).where(AcademicYear.id == year_id))).scalar_one_or_none()
        if not db:
            raise HTTPException(status_code=404, detail="Not found")
        for k, v in year_in.model_dump().items():
            setattr(db, k, v)
        await session.commit()
        await session.refresh(db)
        return db

    @staticmethod
    async def delete_academic_year(session: AsyncSession, year_id: str) -> Any:
        db = (await session.execute(select(AcademicYear).where(AcademicYear.id == year_id))).scalar_one_or_none()
        if not db:
            raise HTTPException(status_code=404, detail="Not found")
        db.is_deleted = True
        await session.commit()
        return {"message": "Deleted"}

    # ── Class ─────────────────────────────────────────────────
    @staticmethod
    async def create_class(session: AsyncSession, tenant_id: uuid.UUID, class_in: ClassCreate) -> Any:
        db = AcademicClass(**class_in.model_dump(), tenant_id=tenant_id)
        session.add(db)
        await session.commit()
        await session.refresh(db)
        return db

    @staticmethod
    async def read_classes(session: AsyncSession, skip: int = 0, limit: int = 100) -> Any:
        classes = (await session.execute(select(AcademicClass).offset(skip).limit(limit))).scalars().all()
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

    @staticmethod
    async def update_class(session: AsyncSession, class_id: str, class_in: ClassCreate) -> Any:
        db = (await session.execute(select(AcademicClass).where(AcademicClass.id == class_id))).scalar_one_or_none()
        if not db:
            raise HTTPException(status_code=404, detail="Not found")
        for k, v in class_in.model_dump().items():
            setattr(db, k, v)
        await session.commit()
        await session.refresh(db)
        return db

    @staticmethod
    async def delete_class(session: AsyncSession, class_id: str) -> Any:
        db = (await session.execute(select(AcademicClass).where(AcademicClass.id == class_id))).scalar_one_or_none()
        if not db:
            raise HTTPException(status_code=404, detail="Not found")
        db.is_deleted = True
        await session.commit()
        return {"message": "Deleted"}

    # ── Section ───────────────────────────────────────────────
    @staticmethod
    async def create_section(session: AsyncSession, tenant_id: uuid.UUID, section_in: SectionCreate) -> Any:
        db = Section(**section_in.model_dump(), tenant_id=tenant_id)
        session.add(db)
        await session.commit()
        await session.refresh(db)
        return db

    @staticmethod
    async def read_sections(session: AsyncSession, skip: int = 0, limit: int = 100) -> Any:
        return (await session.execute(select(Section).offset(skip).limit(limit))).scalars().all()

    @staticmethod
    async def update_section(session: AsyncSession, section_id: str, section_in: SectionCreate) -> Any:
        db = (await session.execute(select(Section).where(Section.id == section_id))).scalar_one_or_none()
        if not db:
            raise HTTPException(status_code=404, detail="Not found")
        for k, v in section_in.model_dump().items():
            setattr(db, k, v)
        await session.commit()
        await session.refresh(db)
        return db

    @staticmethod
    async def delete_section(session: AsyncSession, section_id: str) -> Any:
        db = (await session.execute(select(Section).where(Section.id == section_id))).scalar_one_or_none()
        if not db:
            raise HTTPException(status_code=404, detail="Not found")
        db.is_deleted = True
        await session.commit()
        return {"message": "Deleted"}

    # ── Subject ───────────────────────────────────────────────
    @staticmethod
    async def create_subject(session: AsyncSession, tenant_id: uuid.UUID, subject_in: SubjectCreate) -> Any:
        db = Subject(**subject_in.model_dump(), tenant_id=tenant_id)
        session.add(db)
        await session.commit()
        await session.refresh(db)
        return db

    @staticmethod
    async def read_subjects(session: AsyncSession, skip: int = 0, limit: int = 100) -> Any:
        return (await session.execute(select(Subject).offset(skip).limit(limit))).scalars().all()

    @staticmethod
    async def update_subject(session: AsyncSession, subject_id: str, subject_in: SubjectCreate) -> Any:
        db = (await session.execute(select(Subject).where(Subject.id == subject_id))).scalar_one_or_none()
        if not db:
            raise HTTPException(status_code=404, detail="Not found")
        for k, v in subject_in.model_dump().items():
            setattr(db, k, v)
        await session.commit()
        await session.refresh(db)
        return db

    @staticmethod
    async def delete_subject(session: AsyncSession, subject_id: str) -> Any:
        db = (await session.execute(select(Subject).where(Subject.id == subject_id))).scalar_one_or_none()
        if not db:
            raise HTTPException(status_code=404, detail="Not found")
        db.is_deleted = True
        await session.commit()
        return {"message": "Deleted"}

    # ── Shift ─────────────────────────────────────────────────
    @staticmethod
    async def create_shift(session: AsyncSession, tenant_id: uuid.UUID, shift_in: ShiftCreate) -> Any:
        db = Shift(**shift_in.model_dump(), tenant_id=tenant_id)
        session.add(db)
        await session.commit()
        await session.refresh(db)
        return db

    @staticmethod
    async def read_shifts(session: AsyncSession, skip: int = 0, limit: int = 100) -> Any:
        return (await session.execute(select(Shift).offset(skip).limit(limit))).scalars().all()

    @staticmethod
    async def update_shift(session: AsyncSession, shift_id: str, shift_in: ShiftCreate) -> Any:
        db = (await session.execute(select(Shift).where(Shift.id == shift_id))).scalar_one_or_none()
        if not db:
            raise HTTPException(status_code=404, detail="Not found")
        for k, v in shift_in.model_dump().items():
            setattr(db, k, v)
        await session.commit()
        await session.refresh(db)
        return db

    @staticmethod
    async def delete_shift(session: AsyncSession, shift_id: str) -> Any:
        db = (await session.execute(select(Shift).where(Shift.id == shift_id))).scalar_one_or_none()
        if not db:
            raise HTTPException(status_code=404, detail="Not found")
        db.is_deleted = True
        await session.commit()
        return {"message": "Deleted"}

    # ── Yearly Class Subject ───────────────────────────────────
    @staticmethod
    async def create_yearly_class_subject(session: AsyncSession, tenant_id: uuid.UUID, ycs_in: YearlyClassSubjectCreate) -> Any:
        db = YearlyClassSubject(**ycs_in.model_dump(), tenant_id=tenant_id)
        session.add(db)
        await session.commit()
        await session.refresh(db)
        return db

    @staticmethod
    async def read_yearly_class_subjects(session: AsyncSession, skip: int = 0, limit: int = 100) -> Any:
        return (await session.execute(select(YearlyClassSubject).offset(skip).limit(limit))).scalars().all()

    @staticmethod
    async def update_yearly_class_subject(session: AsyncSession, ycs_id: str, ycs_in: YearlyClassSubjectCreate) -> Any:
        db = (await session.execute(select(YearlyClassSubject).where(YearlyClassSubject.id == ycs_id))).scalar_one_or_none()
        if not db:
            raise HTTPException(status_code=404, detail="Not found")
        for k, v in ycs_in.model_dump().items():
            setattr(db, k, v)
        await session.commit()
        await session.refresh(db)
        return db

    @staticmethod
    async def delete_yearly_class_subject(session: AsyncSession, ycs_id: str) -> Any:
        db = (await session.execute(select(YearlyClassSubject).where(YearlyClassSubject.id == ycs_id))).scalar_one_or_none()
        if not db:
            raise HTTPException(status_code=404, detail="Not found")
        db.is_deleted = True
        await session.commit()
        return {"message": "Deleted"}
