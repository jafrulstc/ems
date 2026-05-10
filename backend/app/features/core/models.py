"""
Core feature models — Organization, AppSetting, Menu, AcademicYear.
Schema: `core`
"""
from datetime import date
from typing import List, Optional

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.shared.base_model import SoftDeleteMixin, StandardMixin, TimestampMixin


class Organization(Base, TimestampMixin, SoftDeleteMixin):
    """Root tenant entity — no TenantMixin, this IS the tenant."""

    __tablename__ = "organizations"
    __table_args__ = {"schema": "core"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true", nullable=False
    )


class AppSetting(Base, StandardMixin):
    """Per-tenant key/value configuration store."""

    __tablename__ = "app_settings"
    __table_args__ = (
        UniqueConstraint("organization_id", "key", name="uq_app_settings_org_key"),
        {"schema": "core"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    group: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class Menu(Base, StandardMixin):
    """Navigation menu item — hierarchical (adjacency list), per-tenant."""

    __tablename__ = "menus"
    __table_args__ = {"schema": "core"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("core.menus.id", ondelete="SET NULL"), nullable=True, index=True
    )
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    icon: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    route_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    permission_key: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true", nullable=False
    )

    # Self-referential: children load lazily on demand
    children: Mapped[List["Menu"]] = relationship(
        "Menu",
        foreign_keys=[parent_id],
        back_populates="parent",
        lazy="select",
    )
    parent: Mapped[Optional["Menu"]] = relationship(
        "Menu",
        foreign_keys=[parent_id],
        back_populates="children",
        remote_side="Menu.id",
        lazy="noload",
    )


class AcademicYear(Base, StandardMixin):
    """Academic year/term scoped to an organization."""

    __tablename__ = "academic_years"
    __table_args__ = {"schema": "core"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true", nullable=False
    )
