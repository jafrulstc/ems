"""remove last_name from students

Revision ID: fc096be78a45
Revises: a1b2c3d4e5f6
Create Date: 2026-09-04 20:56:55.719119

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'fc096be78a45'
down_revision: str | Sequence[str] | None = 'a1b2c3d4e5f6'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('students', 'first_name', new_column_name='full_name', schema='student')
    op.drop_column('students', 'last_name', schema='student')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('students', sa.Column('last_name', sa.String(), nullable=True), schema='student')
    op.alter_column('students', 'full_name', new_column_name='first_name', schema='student')
