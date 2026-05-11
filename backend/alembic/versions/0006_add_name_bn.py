"""add name_bn to class, section, subject, exam_type

Revision ID: 0006_add_name_bn
Revises: 3c27be385a0c
Create Date: 2025-01-20 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "0006_add_name_bn"
down_revision = "3c27be385a0c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("classes", sa.Column("name_bn", sa.String(200), nullable=True), schema="academic")
    op.add_column("sections", sa.Column("name_bn", sa.String(200), nullable=True), schema="academic")
    op.add_column("subjects", sa.Column("name_bn", sa.String(200), nullable=True), schema="academic")
    op.add_column("exam_types", sa.Column("name_bn", sa.String(200), nullable=True), schema="exam")


def downgrade() -> None:
    op.drop_column("exam_types", "name_bn", schema="exam")
    op.drop_column("subjects", "name_bn", schema="academic")
    op.drop_column("sections", "name_bn", schema="academic")
    op.drop_column("classes", "name_bn", schema="academic")
