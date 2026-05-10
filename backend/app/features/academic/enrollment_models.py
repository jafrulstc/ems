"""Enrollment model. Schema: `academic`"""
from typing import Optional
from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.shared.base_model import StandardMixin


class Enrollment(Base, StandardMixin):
    """
    Student enrollment in a section for a given academic year.
    A student may have one active enrollment per academic year (enforced in service layer).
    """

    __tablename__ = "enrollments"
    __table_args__ = {"schema": "academic"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("academic.students.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    section_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("academic.sections.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    academic_year_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("core.academic_years.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    roll_no: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)
