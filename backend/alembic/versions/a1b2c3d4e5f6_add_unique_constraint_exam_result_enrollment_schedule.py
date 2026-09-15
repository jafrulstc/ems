"""add unique constraint on exam_results (enrollment_id, exam_schedule_id)

Revision ID: f9e8d7c6b5a4
Revises: 2acc62f85050
Create Date: 2026-09-15

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'f9e8d7c6b5a4'
down_revision: Union[str, Sequence[str], None] = '2acc62f85050'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        'uq_exam_result_enrollment_schedule',
        'exam_results',
        ['enrollment_id', 'exam_schedule_id'],
        schema='exam',
    )


def downgrade() -> None:
    op.drop_constraint(
        'uq_exam_result_enrollment_schedule',
        'exam_results',
        schema='exam',
        type_='unique',
    )
