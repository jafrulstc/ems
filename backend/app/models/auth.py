import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, SoftDeleteMixin, TenantMixin, TimestampMixin, UUIDMixin


class Permission(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "permissions"
    __table_args__ = {"schema": "auth"}
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

class Role(Base, UUIDMixin, TimestampMixin, TenantMixin, SoftDeleteMixin):
    __tablename__ = "roles"
    __table_args__ = {"schema": "auth"}
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

class RolePermission(Base):
    __tablename__ = "role_permissions"
    __table_args__ = {"schema": "auth"}
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("auth.roles.id", ondelete="CASCADE"), primary_key=True)
    permission_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("auth.permissions.id", ondelete="CASCADE"), primary_key=True)

class User(Base, UUIDMixin, TimestampMixin, TenantMixin, SoftDeleteMixin):
    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    full_name: Mapped[str] = mapped_column(String)
    user_type: Mapped[str] = mapped_column(String) # From UserRole enum
    role_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("auth.roles.id"), nullable=True)
    branch_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("tenant.branches.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
