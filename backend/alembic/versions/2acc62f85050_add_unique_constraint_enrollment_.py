"""add_unique_constraint_enrollment_student_academic_year

Revision ID: 2acc62f85050
Revises: fc096be78a45
Create Date: 2026-09-09 21:44:01.365812

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '2acc62f85050'
down_revision: Union[str, Sequence[str], None] = 'fc096be78a45'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add unique constraint: a student can only be enrolled once per academic year per tenant."""
    op.create_unique_constraint(
        "uq_enrollment_student_academic_year",
        "enrollments",
        ["student_id", "academic_year_id", "tenant_id"],
        schema="student",
    )


def downgrade() -> None:
    """Remove the unique constraint."""
    op.drop_constraint(
        "uq_enrollment_student_academic_year",
        "enrollments",
        schema="student",
        type_="unique",
    )
