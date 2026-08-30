import uuid
from sqlalchemy import String, ForeignKey, Date, Float, Time, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, UUIDMixin, TimestampMixin, TenantMixin, SoftDeleteMixin

class ExamType(Base, UUIDMixin, TimestampMixin, TenantMixin, SoftDeleteMixin):
    __tablename__ = "exam_types"
    __table_args__ = {"schema": "exam"}
    name: Mapped[str] = mapped_column(String)

class Exam(Base, UUIDMixin, TimestampMixin, TenantMixin, SoftDeleteMixin):
    __tablename__ = "exams"
    __table_args__ = {"schema": "exam"}
    name: Mapped[str] = mapped_column(String)
    start_date: Mapped[Date] = mapped_column(Date)
    end_date: Mapped[Date] = mapped_column(Date)
    academic_year_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("academic.academic_years.id"))
    exam_type_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("exam.exam_types.id"), nullable=True)
    max_failing_subjects: Mapped[int] = mapped_column(default=0, server_default="0")

class ExamSchedule(Base, UUIDMixin, TimestampMixin, TenantMixin, SoftDeleteMixin):
    __tablename__ = "exam_schedules"
    __table_args__ = {"schema": "exam"}
    exam_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exam.exams.id"))
    class_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("academic.classes.id"))
    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("academic.subjects.id"))
    exam_date: Mapped[Date] = mapped_column(Date)
    start_time: Mapped[Time | None] = mapped_column(Time, nullable=True)
    end_time: Mapped[Time | None] = mapped_column(Time, nullable=True)
    full_marks: Mapped[float] = mapped_column(Float, default=100.0)
    pass_marks: Mapped[float] = mapped_column(Float, default=33.0)

class ExamResult(Base, UUIDMixin, TimestampMixin, TenantMixin, SoftDeleteMixin):
    __tablename__ = "exam_results"
    __table_args__ = {"schema": "exam"}
    enrollment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("student.enrollments.id"))
    exam_schedule_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exam.exam_schedules.id"))
    obtained_marks: Mapped[float] = mapped_column(Float)
    grade: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="PRESENT", server_default="PRESENT")

class GradingScale(Base, UUIDMixin, TimestampMixin, TenantMixin, SoftDeleteMixin):
    __tablename__ = "grading_scales"
    __table_args__ = {"schema": "exam"}
    grade_name: Mapped[str] = mapped_column(String)
    min_marks: Mapped[float] = mapped_column(Float)
    max_marks: Mapped[float] = mapped_column(Float)
    grade_point: Mapped[float] = mapped_column(Float)
    is_pass: Mapped[bool] = mapped_column(Boolean, default=True)
