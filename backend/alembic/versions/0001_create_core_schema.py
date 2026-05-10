"""
Migration: 0001 — Create core schema tables.

Creates all tables in the `core` PostgreSQL schema:
  organizations, app_settings, menus, academic_years,
  divisions, districts, upazilas, post_offices, villages

Revision ID: a1b2c3d4e5f1
Revises: (none — first migration)
Create Date: 2026-05-10
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f1"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Schema is created by alembic/env.py before migrations run.

    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("is_deleted", sa.Boolean, server_default="false", nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="core",
    )
    op.create_index("ix_core_organizations_slug", "organizations", ["slug"], schema="core")

    op.create_table(
        "app_settings",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("organization_id", sa.Integer, sa.ForeignKey("core.organizations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("value", sa.Text, nullable=True),
        sa.Column("group", sa.String(100), nullable=True),
        sa.Column("is_deleted", sa.Boolean, server_default="false", nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("organization_id", "key", name="uq_app_settings_org_key"),
        schema="core",
    )
    op.create_index("ix_core_app_settings_org_id", "app_settings", ["organization_id"], schema="core")
    op.create_index("ix_core_app_settings_is_deleted", "app_settings", ["is_deleted"], schema="core")

    op.create_table(
        "menus",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("organization_id", sa.Integer, sa.ForeignKey("core.organizations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("parent_id", sa.Integer, sa.ForeignKey("core.menus.id", ondelete="SET NULL"), nullable=True),
        sa.Column("label", sa.String(100), nullable=False),
        sa.Column("icon", sa.String(100), nullable=True),
        sa.Column("route_name", sa.String(100), nullable=True),
        sa.Column("permission_key", sa.String(200), nullable=True),
        sa.Column("order", sa.Integer, server_default="0", nullable=False),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("is_deleted", sa.Boolean, server_default="false", nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="core",
    )
    op.create_index("ix_core_menus_org_id", "menus", ["organization_id"], schema="core")
    op.create_index("ix_core_menus_parent_id", "menus", ["parent_id"], schema="core")
    op.create_index("ix_core_menus_is_deleted", "menus", ["is_deleted"], schema="core")

    op.create_table(
        "academic_years",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("organization_id", sa.Integer, sa.ForeignKey("core.organizations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("end_date", sa.Date, nullable=False),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("is_deleted", sa.Boolean, server_default="false", nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="core",
    )
    op.create_index("ix_core_academic_years_org_id", "academic_years", ["organization_id"], schema="core")
    op.create_index("ix_core_academic_years_is_deleted", "academic_years", ["is_deleted"], schema="core")

    # ── Geo tables (no tenant, no soft-delete) ────────────────────────────────
    op.create_table(
        "divisions",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("bn_name", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="core",
    )

    op.create_table(
        "districts",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("division_id", sa.Integer, sa.ForeignKey("core.divisions.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("bn_name", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="core",
    )
    op.create_index("ix_core_districts_division_id", "districts", ["division_id"], schema="core")

    op.create_table(
        "upazilas",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("district_id", sa.Integer, sa.ForeignKey("core.districts.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("bn_name", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="core",
    )
    op.create_index("ix_core_upazilas_district_id", "upazilas", ["district_id"], schema="core")

    op.create_table(
        "post_offices",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("upazila_id", sa.Integer, sa.ForeignKey("core.upazilas.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("bn_name", sa.String(100), nullable=True),
        sa.Column("post_code", sa.String(10), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="core",
    )
    op.create_index("ix_core_post_offices_upazila_id", "post_offices", ["upazila_id"], schema="core")

    op.create_table(
        "villages",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("post_office_id", sa.Integer, sa.ForeignKey("core.post_offices.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("bn_name", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="core",
    )
    op.create_index("ix_core_villages_post_office_id", "villages", ["post_office_id"], schema="core")


def downgrade() -> None:
    op.drop_table("villages", schema="core")
    op.drop_table("post_offices", schema="core")
    op.drop_table("upazilas", schema="core")
    op.drop_table("districts", schema="core")
    op.drop_table("divisions", schema="core")
    op.drop_table("academic_years", schema="core")
    op.drop_table("menus", schema="core")
    op.drop_table("app_settings", schema="core")
    op.drop_table("organizations", schema="core")
