import uuid

from sqlalchemy import Date, ForeignKey, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, SoftDeleteMixin, TenantMixin, TimestampMixin, UUIDMixin


class AcademicYear(Base, UUIDMixin, TimestampMixin, TenantMixin, SoftDeleteMixin):
    __tablename__ = "academic_years"
    __table_args__ = {"schema": "academic"}
    name: Mapped[str] = mapped_column(String)
    start_date: Mapped[Date] = mapped_column(Date)
    end_date: Mapped[Date] = mapped_column(Date)

class YearlyClassSubject(Base, UUIDMixin, TimestampMixin, TenantMixin, SoftDeleteMixin):
    __tablename__ = "yearly_class_subjects"
    __table_args__ = {"schema": "academic"}
    academic_year_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("academic.academic_years.id"))
    class_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("academic.classes.id"))
    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("academic.subjects.id"))
    is_main_subject: Mapped[bool] = mapped_column(default=True, server_default="true")
    affects_result_calculation: Mapped[bool] = mapped_column(default=True, server_default="true")

class Semester(Base, UUIDMixin, TimestampMixin, TenantMixin, SoftDeleteMixin):
    __tablename__ = "semesters"
    __table_args__ = {"schema": "academic"}
    name: Mapped[str] = mapped_column(String)
    academic_year_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("academic.academic_years.id"))

class Department(Base, UUIDMixin, TimestampMixin, TenantMixin, SoftDeleteMixin):
    __tablename__ = "departments"
    __table_args__ = {"schema": "academic"}
    name: Mapped[str] = mapped_column(String)       # e.g. Science, Commerce, Arts
    level: Mapped[str | None] = mapped_column(String, nullable=True)  # e.g. SSC, HSC, BSC

class AcademicClass(Base, UUIDMixin, TimestampMixin, TenantMixin, SoftDeleteMixin):
    __tablename__ = "classes"
    __table_args__ = {"schema": "academic"}
    name: Mapped[str] = mapped_column(String)
    level: Mapped[str | None] = mapped_column(String, nullable=True)
    department_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("academic.departments.id"), nullable=True)

class Section(Base, UUIDMixin, TimestampMixin, TenantMixin, SoftDeleteMixin):
    __tablename__ = "sections"
    __table_args__ = {"schema": "academic"}
    name: Mapped[str] = mapped_column(String)
    class_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("academic.classes.id"))
    branch_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenant.branches.id"))
    shift_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("academic.shifts.id"), nullable=True)

class Shift(Base, UUIDMixin, TimestampMixin, TenantMixin, SoftDeleteMixin):
    __tablename__ = "shifts"
    __table_args__ = {"schema": "academic"}
    name: Mapped[str] = mapped_column(String)
    start_time: Mapped[Time | None] = mapped_column(Time, nullable=True)
    end_time: Mapped[Time | None] = mapped_column(Time, nullable=True)

class Subject(Base, UUIDMixin, TimestampMixin, TenantMixin, SoftDeleteMixin):
    __tablename__ = "subjects"
    __table_args__ = {"schema": "academic"}
    name: Mapped[str] = mapped_column(String)
    code: Mapped[str] = mapped_column(String)
