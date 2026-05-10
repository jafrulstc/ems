"""
Migration: 0004 — Create academic schema tables.

Revision ID: d4e5f6a1b2c3
Revises: c3d4e5f6a1b2
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "d4e5f6a1b2c3"
down_revision: Union[str, None] = "c3d4e5f6a1b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_ts = {"created_at": sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
       "updated_at": sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
       "is_deleted": sa.Column("is_deleted", sa.Boolean, server_default="false", nullable=False),
       "deleted_at": sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True)}


def _std_cols():
    return [
        sa.Column("is_deleted", sa.Boolean, server_default="false", nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "classes",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("organization_id", sa.Integer, sa.ForeignKey("core.organizations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("numeric_level", sa.Integer, nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        *_std_cols(),
        schema="academic",
    )
    op.create_index("ix_academic_classes_org_id", "classes", ["organization_id"], schema="academic")
    op.create_index("ix_academic_classes_is_deleted", "classes", ["is_deleted"], schema="academic")

    op.create_table(
        "sections",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("organization_id", sa.Integer, sa.ForeignKey("core.organizations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("class_id", sa.Integer, sa.ForeignKey("academic.classes.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        *_std_cols(),
        schema="academic",
    )
    op.create_index("ix_academic_sections_org_id", "sections", ["organization_id"], schema="academic")
    op.create_index("ix_academic_sections_class_id", "sections", ["class_id"], schema="academic")

    op.create_table(
        "subjects",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("organization_id", sa.Integer, sa.ForeignKey("core.organizations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("code", sa.String(20), nullable=True),
        sa.Column("is_optional", sa.Boolean, server_default="false", nullable=False),
        *_std_cols(),
        schema="academic",
    )
    op.create_index("ix_academic_subjects_org_id", "subjects", ["organization_id"], schema="academic")

    op.create_table(
        "students",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("organization_id", sa.Integer, sa.ForeignKey("core.organizations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("registration_no", sa.String(50), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("gender", sa.String(10), nullable=True),
        sa.Column("dob", sa.Date, nullable=True),
        sa.Column("blood_group", sa.String(5), nullable=True),
        sa.Column("village_id", sa.Integer, sa.ForeignKey("core.villages.id", ondelete="SET NULL"), nullable=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("auth.users.id", ondelete="SET NULL"), nullable=True),
        sa.UniqueConstraint("organization_id", "registration_no", name="uq_student_org_reg"),
        *_std_cols(),
        schema="academic",
    )
    op.create_index("ix_academic_students_org_id", "students", ["organization_id"], schema="academic")
    op.create_index("ix_academic_students_village_id", "students", ["village_id"], schema="academic")
    op.create_index("ix_academic_students_user_id", "students", ["user_id"], schema="academic")

    op.create_table(
        "class_subjects",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("organization_id", sa.Integer, sa.ForeignKey("core.organizations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("class_id", sa.Integer, sa.ForeignKey("academic.classes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("subject_id", sa.Integer, sa.ForeignKey("academic.subjects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("full_marks", sa.Integer, nullable=False, server_default="100"),
        sa.Column("pass_marks", sa.Integer, nullable=False, server_default="33"),
        sa.UniqueConstraint("organization_id", "class_id", "subject_id", name="uq_class_subject"),
        *_std_cols(),
        schema="academic",
    )
    op.create_index("ix_academic_class_subjects_class_id", "class_subjects", ["class_id"], schema="academic")
    op.create_index("ix_academic_class_subjects_subject_id", "class_subjects", ["subject_id"], schema="academic")

    op.create_table(
        "guardians",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("organization_id", sa.Integer, sa.ForeignKey("core.organizations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("student_id", sa.Integer, sa.ForeignKey("academic.students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("relation", sa.String(50), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("is_primary", sa.Boolean, server_default="false", nullable=False),
        *_std_cols(),
        schema="academic",
    )
    op.create_index("ix_academic_guardians_student_id", "guardians", ["student_id"], schema="academic")

    op.create_table(
        "enrollments",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("organization_id", sa.Integer, sa.ForeignKey("core.organizations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("student_id", sa.Integer, sa.ForeignKey("academic.students.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("section_id", sa.Integer, sa.ForeignKey("academic.sections.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("academic_year_id", sa.Integer, sa.ForeignKey("core.academic_years.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("roll_no", sa.String(20), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        *_std_cols(),
        schema="academic",
    )
    op.create_index("ix_academic_enrollments_student_id", "enrollments", ["student_id"], schema="academic")
    op.create_index("ix_academic_enrollments_section_id", "enrollments", ["section_id"], schema="academic")
    op.create_index("ix_academic_enrollments_year_id", "enrollments", ["academic_year_id"], schema="academic")


def downgrade() -> None:
    op.drop_table("enrollments", schema="academic")
    op.drop_table("guardians", schema="academic")
    op.drop_table("class_subjects", schema="academic")
    op.drop_table("students", schema="academic")
    op.drop_table("subjects", schema="academic")
    op.drop_table("sections", schema="academic")
    op.drop_table("classes", schema="academic")
