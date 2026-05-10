"""
Shared SQLAlchemy mixins applied to all feature models.

Mixin taxonomy (as per architecture plan):
  - TimestampMixin    : created_at, updated_at
  - SoftDeleteMixin   : is_deleted, deleted_at
  - TenantMixin       : organization_id FK → core.organizations.id
  - StandardMixin     : TimestampMixin + SoftDeleteMixin + TenantMixin (most models)
  - GeoMixin          : TimestampMixin only (no tenant, no soft-delete — shared reference data)
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """Automatic created_at / updated_at columns managed by the DB server."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """Logical deletion support — never hard-delete tenant records."""

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
        index=True,
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class TenantMixin:
    """
    Row-level multi-tenancy column.
    FK enforces referential integrity; index enables fast tenant-scoped queries.
    The FK is deferred to avoid import order issues across features.
    """

    organization_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("core.organizations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )


class StandardMixin(TimestampMixin, SoftDeleteMixin, TenantMixin):
    """
    Full mixin for tenant-aware, soft-deletable models.
    Inherit this for all core / auth / academic / exam models.
    """
    pass


class GeoMixin(TimestampMixin):
    """
    Minimal mixin for shared geographic reference tables.
    No tenant scope, no soft-delete — seeded once at the national level.
    """
    pass
