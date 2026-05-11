"""
Academic models — Class, Section, Subject, Student, ClassSubject.
Schema: `academic`
"""
from datetime import date
from typing import Optional

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.shared.base_model import StandardMixin


class Class(Base, StandardMixin):
    """School class / grade level, e.g. Class 1, Class 9."""

    __tablename__ = "classes"
    __table_args__ = {"schema": "academic"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_bn: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    numeric_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)


class Section(Base, StandardMixin):
    """Class section (A, B, Science, Arts …)."""

    __tablename__ = "sections"
    __table_args__ = {"schema": "academic"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    class_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("academic.classes.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_bn: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)


class Subject(Base, StandardMixin):
    """Academic subject — may be optional (elective)."""

    __tablename__ = "subjects"
    __table_args__ = {"schema": "academic"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    name_bn: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_optional: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)


class Student(Base, StandardMixin):
    """Student profile — linked optionally to geo and auth.users."""

    __tablename__ = "students"
    __table_args__ = (
        UniqueConstraint("organization_id", "registration_no", name="uq_student_org_reg"),
        {"schema": "academic"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    registration_no: Mapped[str] = mapped_column(String(50), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    gender: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    dob: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    blood_group: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    # FK to deepest geo level — full address reconstructed by joining hierarchy
    village_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("core.villages.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # Optional link to a system user account
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("auth.users.id", ondelete="SET NULL"), nullable=True, index=True
    )


class ClassSubject(Base, StandardMixin):
    """Maps a subject to a class with marks configuration."""

    __tablename__ = "class_subjects"
    __table_args__ = (
        UniqueConstraint("organization_id", "class_id", "subject_id", name="uq_class_subject"),
        {"schema": "academic"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    class_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("academic.classes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    subject_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("academic.subjects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    full_marks: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    pass_marks: Mapped[int] = mapped_column(Integer, nullable=False, default=33)
