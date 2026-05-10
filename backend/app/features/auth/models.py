"""
Auth feature models. Schema: `auth`
Tables: users, roles, permissions, role_permissions, user_roles, user_permission_overrides
"""
from typing import List, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.shared.base_model import SoftDeleteMixin, StandardMixin, TimestampMixin, TenantMixin


class User(Base, StandardMixin):
    """Tenant-scoped user. Email unique per organization."""

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("organization_id", "email", name="uq_users_org_email"),
        {"schema": "auth"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)

    roles: Mapped[List["Role"]] = relationship(
        "Role", secondary="auth.user_roles", lazy="selectin"
    )


class Role(Base, StandardMixin):
    """Permission group scoped to an organization."""

    __tablename__ = "roles"
    __table_args__ = {"schema": "auth"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    permissions: Mapped[List["Permission"]] = relationship(
        "Permission", secondary="auth.role_permissions", lazy="noload"
    )


class Permission(Base, TimestampMixin):
    """System-level permission key — global, no tenant scope."""

    __tablename__ = "permissions"
    __table_args__ = {"schema": "auth"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    module: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)


class RolePermission(Base):
    """M2M join: Role ↔ Permission."""

    __tablename__ = "role_permissions"
    __table_args__ = {"schema": "auth"}

    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("auth.roles.id", ondelete="CASCADE"), primary_key=True
    )
    permission_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("auth.permissions.id", ondelete="CASCADE"), primary_key=True
    )


class UserRole(Base):
    """M2M join: User ↔ Role."""

    __tablename__ = "user_roles"
    __table_args__ = {"schema": "auth"}

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("auth.users.id", ondelete="CASCADE"), primary_key=True
    )
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("auth.roles.id", ondelete="CASCADE"), primary_key=True
    )


class UserPermissionOverride(Base, TenantMixin, TimestampMixin):
    """Per-user explicit grant or deny for a specific permission."""

    __tablename__ = "user_permission_overrides"
    __table_args__ = (
        UniqueConstraint("user_id", "permission_id", name="uq_override_user_perm"),
        {"schema": "auth"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    permission_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("auth.permissions.id", ondelete="CASCADE"), nullable=False
    )
    is_granted: Mapped[bool] = mapped_column(Boolean, nullable=False)
