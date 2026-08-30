from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin, TenantMixin

class Institute(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "institutes"
    __table_args__ = {"schema": "tenant"}
    name: Mapped[str] = mapped_column(String, index=True)
    slug: Mapped[str] = mapped_column(String, unique=True, index=True)
    address: Mapped[str | None] = mapped_column(String, nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String, nullable=True)

class Branch(Base, UUIDMixin, TimestampMixin, TenantMixin, SoftDeleteMixin):
    __tablename__ = "branches"
    __table_args__ = {"schema": "tenant"}
    name: Mapped[str] = mapped_column(String)
    address: Mapped[str | None] = mapped_column(String, nullable=True)
