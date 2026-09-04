"""
Add branch_id to student.enrollments and fix student_id_no uniqueness to be tenant-scoped.

Revision ID: a1b2c3d4e5f6
Revises: 1e3aca4a4b49, 81588816130f  (merges both existing heads)
Create Date: 2026-09-03
"""
import sqlalchemy as sa

from alembic import op

revision = 'a1b2c3d4e5f6'
down_revision = ('1e3aca4a4b49', '81588816130f')   # merges both existing heads
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── 1. Add branch_id to student.enrollments ────────────────────────────
    op.add_column(
        'enrollments',
        sa.Column('branch_id', sa.UUID(), nullable=True),
        schema='student',
    )
    op.create_foreign_key(
        'fk_enrollments_branch_id',
        'enrollments', 'branches',
        ['branch_id'], ['id'],
        source_schema='student',
        referent_schema='tenant',
    )

    # ── 2. Fix student_id_no: drop global unique → tenant-scoped unique ────
    # Drop the global unique constraint (PostgreSQL creates it with this name by default)
    op.execute("ALTER TABLE student.students DROP CONSTRAINT IF EXISTS students_student_id_no_key")
    # Drop the old unique index if it exists separately
    op.execute("DROP INDEX IF EXISTS student.ix_student_students_student_id_no")

    # Re-create as a plain (non-unique) index
    op.create_index(
        'ix_student_students_student_id_no',
        'students',
        ['student_id_no'],
        schema='student',
        unique=False,
    )

    # Add the correct tenant-scoped unique constraint
    op.create_unique_constraint(
        'uq_student_id_no_per_tenant',
        'students',
        ['student_id_no', 'tenant_id'],
        schema='student',
    )


def downgrade() -> None:
    op.drop_constraint('uq_student_id_no_per_tenant', 'students', schema='student')
    op.drop_index('ix_student_students_student_id_no', table_name='students', schema='student')
    op.create_index(
        'ix_student_students_student_id_no',
        'students',
        ['student_id_no'],
        schema='student',
        unique=True,
    )

    op.drop_constraint('fk_enrollments_branch_id', 'enrollments', schema='student')
    op.drop_column('enrollments', 'branch_id', schema='student')
