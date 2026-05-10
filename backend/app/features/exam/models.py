"""
Exam feature models. Schema: `exam`
Tables: exam_types, routines, marks, grading_systems, grading_rules,
        attendance_records, results
"""
from datetime import date, time
from typing import Optional

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Numeric, String, Text, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.shared.base_model import StandardMixin


class ExamType(Base, StandardMixin):
    """Named exam category, e.g. Mid-term, Final, Unit Test."""

    __tablename__ = "exam_types"
    __table_args__ = {"schema": "exam"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class ExamRoutine(Base, StandardMixin):
    """Scheduled exam slot: class + subject + date/time for a given exam type."""

    __tablename__ = "routines"
    __table_args__ = (
        UniqueConstraint(
            "organization_id", "exam_type_id", "class_id", "subject_id", "academic_year_id",
            name="uq_routine_class_subject_year",
        ),
        {"schema": "exam"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    exam_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("exam.exam_types.id", ondelete="CASCADE"), nullable=False, index=True)
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("academic.classes.id", ondelete="RESTRICT"), nullable=False, index=True)
    subject_id: Mapped[int] = mapped_column(Integer, ForeignKey("academic.subjects.id", ondelete="RESTRICT"), nullable=False, index=True)
    academic_year_id: Mapped[int] = mapped_column(Integer, ForeignKey("core.academic_years.id", ondelete="RESTRICT"), nullable=False, index=True)
    exam_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    start_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    end_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)


class GradingSystem(Base, StandardMixin):
    """Named grading scale (GPA 4.0, percentage bands, etc.)."""

    __tablename__ = "grading_systems"
    __table_args__ = {"schema": "exam"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)


class GradingRule(Base, StandardMixin):
    """A single grade band within a grading system."""

    __tablename__ = "grading_rules"
    __table_args__ = {"schema": "exam"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    grading_system_id: Mapped[int] = mapped_column(Integer, ForeignKey("exam.grading_systems.id", ondelete="CASCADE"), nullable=False, index=True)
    min_marks: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)   # percentage
    max_marks: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)   # percentage
    grade: Mapped[str] = mapped_column(String(10), nullable=False)
    grade_point: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    remarks: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)


class Mark(Base, StandardMixin):
    """Marks obtained by one enrolled student for one subject in one exam type."""

    __tablename__ = "marks"
    __table_args__ = (
        UniqueConstraint("enrollment_id", "class_subject_id", "exam_type_id", name="uq_mark_enroll_subj_exam"),
        {"schema": "exam"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    enrollment_id: Mapped[int] = mapped_column(Integer, ForeignKey("academic.enrollments.id", ondelete="RESTRICT"), nullable=False, index=True)
    class_subject_id: Mapped[int] = mapped_column(Integer, ForeignKey("academic.class_subjects.id", ondelete="RESTRICT"), nullable=False, index=True)
    exam_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("exam.exam_types.id", ondelete="RESTRICT"), nullable=False, index=True)
    marks_obtained: Mapped[Optional[float]] = mapped_column(Numeric(6, 2), nullable=True)
    is_absent: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)


class AttendanceRecord(Base, StandardMixin):
    """Daily attendance record per enrolled student."""

    __tablename__ = "attendance_records"
    __table_args__ = (
        UniqueConstraint("enrollment_id", "record_date", name="uq_attendance_enroll_date"),
        {"schema": "exam"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    enrollment_id: Mapped[int] = mapped_column(Integer, ForeignKey("academic.enrollments.id", ondelete="RESTRICT"), nullable=False, index=True)
    record_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(10), nullable=False)  # Present / Absent / Late


class Result(Base, StandardMixin):
    """Pre-computed exam result for an enrollment × exam type. Generated by result_service."""

    __tablename__ = "results"
    __table_args__ = (
        UniqueConstraint("enrollment_id", "exam_type_id", name="uq_result_enroll_exam"),
        {"schema": "exam"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    enrollment_id: Mapped[int] = mapped_column(Integer, ForeignKey("academic.enrollments.id", ondelete="RESTRICT"), nullable=False, index=True)
    exam_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("exam.exam_types.id", ondelete="RESTRICT"), nullable=False, index=True)
    total_full_marks: Mapped[int] = mapped_column(Integer, nullable=False)
    total_obtained_marks: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    percentage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    grade: Mapped[str] = mapped_column(String(10), nullable=False)
    grade_point: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    is_pass: Mapped[bool] = mapped_column(Boolean, nullable=False)
    remarks: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)


class ExamBoard(Base, StandardMixin):
    """Reference table for external examination boards (e.g., Dhaka Board, Edexcel)."""

    __tablename__ = "exam_boards"
    __table_args__ = {"schema": "exam"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class ExamRegistration(Base, StandardMixin):
    """
    Links an enrollment to an exam type.
    Must exist before marks can be entered. If exam_board_id is null, it's an institutional exam.
    """

    __tablename__ = "exam_registrations"
    __table_args__ = (
        UniqueConstraint("enrollment_id", "exam_type_id", name="uq_exam_registration_enroll_exam"),
        {"schema": "exam"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    enrollment_id: Mapped[int] = mapped_column(Integer, ForeignKey("academic.enrollments.id", ondelete="RESTRICT"), nullable=False, index=True)
    exam_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("exam.exam_types.id", ondelete="RESTRICT"), nullable=False, index=True)
    exam_board_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("exam.exam_boards.id", ondelete="RESTRICT"), nullable=True, index=True)
    board_roll_no: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    board_registration_no: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
