"""
Migration: 0005 — Create exam schema tables.

Revision ID: e5f6a1b2c3d4
Revises: d4e5f6a1b2c3
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "e5f6a1b2c3d4"
down_revision: Union[str, None] = "d4e5f6a1b2c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _std():
    return [
        sa.Column("is_deleted", sa.Boolean, server_default="false", nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "exam_types",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("organization_id", sa.Integer, sa.ForeignKey("core.organizations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        *_std(), schema="exam",
    )
    op.create_index("ix_exam_types_org_id", "exam_types", ["organization_id"], schema="exam")

    op.create_table(
        "grading_systems",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("organization_id", sa.Integer, sa.ForeignKey("core.organizations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("is_default", sa.Boolean, server_default="false", nullable=False),
        *_std(), schema="exam",
    )
    op.create_index("ix_exam_grading_systems_org_id", "grading_systems", ["organization_id"], schema="exam")

    op.create_table(
        "grading_rules",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("organization_id", sa.Integer, sa.ForeignKey("core.organizations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("grading_system_id", sa.Integer, sa.ForeignKey("exam.grading_systems.id", ondelete="CASCADE"), nullable=False),
        sa.Column("min_marks", sa.Numeric(5, 2), nullable=False),
        sa.Column("max_marks", sa.Numeric(5, 2), nullable=False),
        sa.Column("grade", sa.String(10), nullable=False),
        sa.Column("grade_point", sa.Numeric(4, 2), nullable=False),
        sa.Column("remarks", sa.String(100), nullable=True),
        *_std(), schema="exam",
    )
    op.create_index("ix_exam_grading_rules_sys_id", "grading_rules", ["grading_system_id"], schema="exam")

    op.create_table(
        "routines",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("organization_id", sa.Integer, sa.ForeignKey("core.organizations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("exam_type_id", sa.Integer, sa.ForeignKey("exam.exam_types.id", ondelete="CASCADE"), nullable=False),
        sa.Column("class_id", sa.Integer, sa.ForeignKey("academic.classes.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("subject_id", sa.Integer, sa.ForeignKey("academic.subjects.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("academic_year_id", sa.Integer, sa.ForeignKey("core.academic_years.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("exam_date", sa.Date, nullable=True),
        sa.Column("start_time", sa.Time, nullable=True),
        sa.Column("end_time", sa.Time, nullable=True),
        sa.UniqueConstraint("organization_id", "exam_type_id", "class_id", "subject_id", "academic_year_id",
                            name="uq_routine_class_subject_year"),
        *_std(), schema="exam",
    )
    op.create_index("ix_exam_routines_org_id", "routines", ["organization_id"], schema="exam")
    op.create_index("ix_exam_routines_exam_type_id", "routines", ["exam_type_id"], schema="exam")

    op.create_table(
        "marks",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("organization_id", sa.Integer, sa.ForeignKey("core.organizations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("enrollment_id", sa.Integer, sa.ForeignKey("academic.enrollments.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("class_subject_id", sa.Integer, sa.ForeignKey("academic.class_subjects.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("exam_type_id", sa.Integer, sa.ForeignKey("exam.exam_types.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("marks_obtained", sa.Numeric(6, 2), nullable=True),
        sa.Column("is_absent", sa.Boolean, server_default="false", nullable=False),
        sa.UniqueConstraint("enrollment_id", "class_subject_id", "exam_type_id", name="uq_mark_enroll_subj_exam"),
        *_std(), schema="exam",
    )
    op.create_index("ix_exam_marks_enrollment_id", "marks", ["enrollment_id"], schema="exam")
    op.create_index("ix_exam_marks_class_subject_id", "marks", ["class_subject_id"], schema="exam")
    op.create_index("ix_exam_marks_exam_type_id", "marks", ["exam_type_id"], schema="exam")

    op.create_table(
        "attendance_records",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("organization_id", sa.Integer, sa.ForeignKey("core.organizations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("enrollment_id", sa.Integer, sa.ForeignKey("academic.enrollments.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("record_date", sa.Date, nullable=False),
        sa.Column("status", sa.String(10), nullable=False),
        sa.UniqueConstraint("enrollment_id", "record_date", name="uq_attendance_enroll_date"),
        *_std(), schema="exam",
    )
    op.create_index("ix_exam_attendance_enrollment_id", "attendance_records", ["enrollment_id"], schema="exam")
    op.create_index("ix_exam_attendance_record_date", "attendance_records", ["record_date"], schema="exam")

    op.create_table(
        "results",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("organization_id", sa.Integer, sa.ForeignKey("core.organizations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("enrollment_id", sa.Integer, sa.ForeignKey("academic.enrollments.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("exam_type_id", sa.Integer, sa.ForeignKey("exam.exam_types.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("total_full_marks", sa.Integer, nullable=False),
        sa.Column("total_obtained_marks", sa.Numeric(8, 2), nullable=False),
        sa.Column("percentage", sa.Numeric(5, 2), nullable=False),
        sa.Column("grade", sa.String(10), nullable=False),
        sa.Column("grade_point", sa.Numeric(4, 2), nullable=False),
        sa.Column("is_pass", sa.Boolean, nullable=False),
        sa.Column("remarks", sa.String(100), nullable=True),
        sa.UniqueConstraint("enrollment_id", "exam_type_id", name="uq_result_enroll_exam"),
        *_std(), schema="exam",
    )
    op.create_index("ix_exam_results_enrollment_id", "results", ["enrollment_id"], schema="exam")
    op.create_index("ix_exam_results_exam_type_id", "results", ["exam_type_id"], schema="exam")


def downgrade() -> None:
    op.drop_table("results", schema="exam")
    op.drop_table("attendance_records", schema="exam")
    op.drop_table("marks", schema="exam")
    op.drop_table("routines", schema="exam")
    op.drop_table("grading_rules", schema="exam")
    op.drop_table("grading_systems", schema="exam")
    op.drop_table("exam_types", schema="exam")
