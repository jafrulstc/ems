"""
Migration: 0002 — Create auth schema tables.

Revision ID: b2c3d4e5f6a1
Revises: a1b2c3d4e5f1
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "b2c3d4e5f6a1"
down_revision: Union[str, None] = "a1b2c3d4e5f1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("key", sa.String(200), nullable=False, unique=True),
        sa.Column("label", sa.String(255), nullable=False),
        sa.Column("module", sa.String(100), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="auth",
    )
    op.create_index("ix_auth_permissions_key", "permissions", ["key"], schema="auth")
    op.create_index("ix_auth_permissions_module", "permissions", ["module"], schema="auth")

    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("organization_id", sa.Integer, sa.ForeignKey("core.organizations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("username", sa.String(100), nullable=True),
        sa.Column("hashed_password", sa.Text, nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("is_superuser", sa.Boolean, server_default="false", nullable=False),
        sa.Column("is_deleted", sa.Boolean, server_default="false", nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("organization_id", "email", name="uq_users_org_email"),
        schema="auth",
    )
    op.create_index("ix_auth_users_org_id", "users", ["organization_id"], schema="auth")
    op.create_index("ix_auth_users_email", "users", ["email"], schema="auth")
    op.create_index("ix_auth_users_is_deleted", "users", ["is_deleted"], schema="auth")

    op.create_table(
        "roles",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("organization_id", sa.Integer, sa.ForeignKey("core.organizations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_deleted", sa.Boolean, server_default="false", nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="auth",
    )
    op.create_index("ix_auth_roles_org_id", "roles", ["organization_id"], schema="auth")
    op.create_index("ix_auth_roles_is_deleted", "roles", ["is_deleted"], schema="auth")

    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.Integer, sa.ForeignKey("auth.roles.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("permission_id", sa.Integer, sa.ForeignKey("auth.permissions.id", ondelete="CASCADE"), primary_key=True),
        schema="auth",
    )

    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.Integer, sa.ForeignKey("auth.users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("role_id", sa.Integer, sa.ForeignKey("auth.roles.id", ondelete="CASCADE"), primary_key=True),
        schema="auth",
    )

    op.create_table(
        "user_permission_overrides",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("organization_id", sa.Integer, sa.ForeignKey("core.organizations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("permission_id", sa.Integer, sa.ForeignKey("auth.permissions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("is_granted", sa.Boolean, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "permission_id", name="uq_override_user_perm"),
        schema="auth",
    )
    op.create_index("ix_auth_overrides_user_id", "user_permission_overrides", ["user_id"], schema="auth")
    op.create_index("ix_auth_overrides_org_id", "user_permission_overrides", ["organization_id"], schema="auth")


def downgrade() -> None:
    op.drop_table("user_permission_overrides", schema="auth")
    op.drop_table("user_roles", schema="auth")
    op.drop_table("role_permissions", schema="auth")
    op.drop_table("roles", schema="auth")
    op.drop_table("users", schema="auth")
    op.drop_table("permissions", schema="auth")
