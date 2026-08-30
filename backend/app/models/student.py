import uuid
from sqlalchemy import String, ForeignKey, Date, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, UUIDMixin, TimestampMixin, TenantMixin, SoftDeleteMixin

class Guardian(Base, UUIDMixin, TimestampMixin, TenantMixin, SoftDeleteMixin):
    __tablename__ = "guardians"
    __table_args__ = {"schema": "student"}
    name: Mapped[str] = mapped_column(String)
    phone: Mapped[str] = mapped_column(String, index=True)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("auth.users.id"), nullable=True)

class Student(Base, UUIDMixin, TimestampMixin, TenantMixin, SoftDeleteMixin):
    __tablename__ = "students"
    __table_args__ = {"schema": "student"}
    student_id_no: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    date_of_birth: Mapped[Date] = mapped_column(Date)
    gender: Mapped[str] = mapped_column(String)
    blood_group: Mapped[str | None] = mapped_column(String, nullable=True)
    address: Mapped[str | None] = mapped_column(String, nullable=True)
    profile_picture_url: Mapped[str | None] = mapped_column(String, nullable=True)
    
    guardian_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("student.guardians.id"), nullable=True)
    branch_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenant.branches.id"))

class Enrollment(Base, UUIDMixin, TimestampMixin, TenantMixin, SoftDeleteMixin):
    __tablename__ = "enrollments"
    __table_args__ = {"schema": "student"}
    roll_number: Mapped[str | None] = mapped_column(String, nullable=True)
    enrollment_date: Mapped[Date] = mapped_column(Date)
    
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("student.students.id"))
    academic_year_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("academic.academic_years.id"))
    class_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("academic.classes.id"))
    section_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("academic.sections.id"), nullable=True)
    
    status: Mapped[str] = mapped_column(String, default="active")
