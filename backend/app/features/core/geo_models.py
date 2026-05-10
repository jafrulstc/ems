"""
Geographic reference models — shared national data, no tenant scope.
Schema: `core`

Hierarchy: Division → District → Upazila → PostOffice → Village
These tables are seeded once and read-only via public API endpoints.
"""
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.shared.base_model import GeoMixin


class Division(Base, GeoMixin):
    __tablename__ = "divisions"
    __table_args__ = {"schema": "core"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    bn_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)


class District(Base, GeoMixin):
    __tablename__ = "districts"
    __table_args__ = {"schema": "core"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    division_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("core.divisions.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    bn_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)


class Upazila(Base, GeoMixin):
    __tablename__ = "upazilas"
    __table_args__ = {"schema": "core"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    district_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("core.districts.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    bn_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)


class PostOffice(Base, GeoMixin):
    __tablename__ = "post_offices"
    __table_args__ = {"schema": "core"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    upazila_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("core.upazilas.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    bn_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    post_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)


class Village(Base, GeoMixin):
    __tablename__ = "villages"
    __table_args__ = {"schema": "core"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    post_office_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("core.post_offices.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    bn_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
