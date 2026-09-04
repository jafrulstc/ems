"""
student_service.py
------------------
Business logic for Student, Guardian, and Enrollment management.
"""

import uuid

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.student import Enrollment, Guardian, Student
from app.schemas.student import (
    EnrollmentCreate,
    GuardianCreate,
    StudentCreate,
)


class StudentService:
    # ── Guardian ──────────────────────────────────────────────────────────────

    @staticmethod
    async def create_guardian(data: GuardianCreate, tenant_id: uuid.UUID, session: AsyncSession) -> Guardian:
        db = Guardian(**data.model_dump(), tenant_id=tenant_id)
        session.add(db)
        await session.commit()
        await session.refresh(db)
        return db

    @staticmethod
    async def get_guardians(session: AsyncSession, skip: int = 0, limit: int = 100) -> list[Guardian]:
        result = await session.execute(select(Guardian).offset(skip).limit(limit))
        return list(result.scalars().all())

    @staticmethod
    async def update_guardian(guardian_id: str, data: GuardianCreate, session: AsyncSession) -> Guardian:
        db = (await session.execute(select(Guardian).where(Guardian.id == guardian_id))).scalar_one_or_none()
        if not db:
            raise HTTPException(status_code=404, detail="Guardian not found")
        for k, v in data.model_dump().items():
            setattr(db, k, v)
        await session.commit()
        await session.refresh(db)
        return db

    @staticmethod
    async def delete_guardian(guardian_id: str, session: AsyncSession) -> dict:
        db = (await session.execute(select(Guardian).where(Guardian.id == guardian_id))).scalar_one_or_none()
        if not db:
            raise HTTPException(status_code=404, detail="Guardian not found")
        db.is_deleted = True
        await session.commit()
        return {"message": "Deleted"}

    # ── Student ───────────────────────────────────────────────────────────────

    @staticmethod
    async def get_next_student_id_no(tenant_id: uuid.UUID, session: AsyncSession) -> int:
        """Return the next available student_id_no for the given tenant (1-based, no gaps allowed)."""
        result = await session.execute(
            select(func.max(Student.student_id_no)).where(Student.tenant_id == tenant_id)
        )
        current_max = result.scalar_one_or_none()
        return (current_max or 0) + 1

    @staticmethod
    async def create_student(data: StudentCreate, tenant_id: uuid.UUID, session: AsyncSession) -> Student:
        """
        Safely assign student_id_no:
        - UI sends a suggested student_id_no (pre-filled from get_next_student_id_no).
        - At save-time, re-check the actual max in the DB (handles concurrent inserts).
        - If the suggested ID is still free, use it; otherwise use max+1.
        """
        result = await session.execute(
            select(func.max(Student.student_id_no)).where(Student.tenant_id == tenant_id)
        )
        current_max = result.scalar_one_or_none() or 0
        safe_id = max(data.student_id_no, current_max + 1)

        dump = data.model_dump()
        dump["student_id_no"] = safe_id
        db = Student(**dump, tenant_id=tenant_id)
        session.add(db)
        await session.commit()
        await session.refresh(db)
        return db

    @staticmethod
    async def get_students(session: AsyncSession, skip: int = 0, limit: int = 100) -> list[Student]:
        result = await session.execute(select(Student).offset(skip).limit(limit))
        return list(result.scalars().all())

    @staticmethod
    async def update_student(student_id: str, data: StudentCreate, session: AsyncSession) -> Student:
        db = (await session.execute(select(Student).where(Student.id == student_id))).scalar_one_or_none()
        if not db:
            raise HTTPException(status_code=404, detail="Student not found")
        for k, v in data.model_dump().items():
            setattr(db, k, v)
        await session.commit()
        await session.refresh(db)
        return db

    @staticmethod
    async def delete_student(student_id: str, session: AsyncSession) -> dict:
        db = (await session.execute(select(Student).where(Student.id == student_id))).scalar_one_or_none()
        if not db:
            raise HTTPException(status_code=404, detail="Student not found")
        db.is_deleted = True
        await session.commit()
        return {"message": "Deleted"}

    # ── Enrollment ────────────────────────────────────────────────────────────

    @staticmethod
    async def create_enrollment(data: EnrollmentCreate, tenant_id: uuid.UUID, session: AsyncSession) -> Enrollment:
        db = Enrollment(**data.model_dump(), tenant_id=tenant_id)
        session.add(db)
        await session.commit()
        await session.refresh(db)
        return db

    @staticmethod
    async def get_enrollments(session: AsyncSession, skip: int = 0, limit: int = 100) -> list[Enrollment]:
        result = await session.execute(select(Enrollment).offset(skip).limit(limit))
        return list(result.scalars().all())

    @staticmethod
    async def update_enrollment(enrollment_id: str, data: EnrollmentCreate, session: AsyncSession) -> Enrollment:
        db = (await session.execute(select(Enrollment).where(Enrollment.id == enrollment_id))).scalar_one_or_none()
        if not db:
            raise HTTPException(status_code=404, detail="Enrollment not found")
        for k, v in data.model_dump().items():
            setattr(db, k, v)
        await session.commit()
        await session.refresh(db)
        return db

    @staticmethod
    async def delete_enrollment(enrollment_id: str, session: AsyncSession) -> dict:
        db = (await session.execute(select(Enrollment).where(Enrollment.id == enrollment_id))).scalar_one_or_none()
        if not db:
            raise HTTPException(status_code=404, detail="Enrollment not found")
        db.is_deleted = True
        await session.commit()
        return {"message": "Deleted"}

    # ── Reports ───────────────────────────────────────────────────────────────

    @staticmethod
    async def report_enrollments(
        session: AsyncSession,
        academic_year_id: uuid.UUID | None = None,
        class_id: uuid.UUID | None = None,
        section_id: uuid.UUID | None = None,
    ) -> list[dict]:
        stmt = select(Enrollment, Student).join(Student, Enrollment.student_id == Student.id)
        if academic_year_id:
            stmt = stmt.where(Enrollment.academic_year_id == academic_year_id)
        if class_id:
            stmt = stmt.where(Enrollment.class_id == class_id)
        if section_id:
            stmt = stmt.where(Enrollment.section_id == section_id)

        result = await session.execute(stmt)
        records = result.all()

        return [
            {
                "enrollment_id": enr.id,
                "roll_number": enr.roll_number,
                "student_id": std.id,
                "student_id_no": std.student_id_no,
                "student_name": f"{std.first_name} {std.last_name}",
                "gender": std.gender,
            }
            for enr, std in records
        ]
