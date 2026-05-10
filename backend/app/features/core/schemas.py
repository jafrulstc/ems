"""
Pydantic schemas for the Core feature.
Covers: Organization, AppSetting, Menu (nested), AcademicYear, Geo read models.
"""
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator


# ── Organization ──────────────────────────────────────────────────────────────

class OrganizationCreate(BaseModel):
    name: str
    slug: str
    is_active: bool = True


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    is_active: Optional[bool] = None


class OrganizationRead(BaseModel):
    id: int
    name: str
    slug: str
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ── AppSetting ────────────────────────────────────────────────────────────────

class AppSettingCreate(BaseModel):
    key: str
    value: Optional[str] = None
    group: Optional[str] = None


class AppSettingUpdate(BaseModel):
    value: Optional[str] = None
    group: Optional[str] = None


class AppSettingRead(BaseModel):
    id: int
    organization_id: int
    key: str
    value: Optional[str]
    group: Optional[str]
    model_config = ConfigDict(from_attributes=True)


# ── Menu ──────────────────────────────────────────────────────────────────────

class MenuCreate(BaseModel):
    parent_id: Optional[int] = None
    label: str
    icon: Optional[str] = None
    route_name: Optional[str] = None
    permission_key: Optional[str] = None
    order: int = 0
    is_active: bool = True


class MenuUpdate(BaseModel):
    parent_id: Optional[int] = None
    label: Optional[str] = None
    icon: Optional[str] = None
    route_name: Optional[str] = None
    permission_key: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None


class MenuRead(BaseModel):
    id: int
    organization_id: int
    parent_id: Optional[int]
    label: str
    icon: Optional[str]
    route_name: Optional[str]
    permission_key: Optional[str]
    order: int
    is_active: bool
    children: List["MenuRead"] = []
    model_config = ConfigDict(from_attributes=True)


MenuRead.model_rebuild()  # required for self-referential type


# ── AcademicYear ──────────────────────────────────────────────────────────────

class AcademicYearCreate(BaseModel):
    name: str
    start_date: date
    end_date: date
    is_active: bool = True

    @field_validator("end_date")
    @classmethod
    def end_after_start(cls, v: date, info) -> date:
        if info.data.get("start_date") and v <= info.data["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v


class AcademicYearUpdate(BaseModel):
    name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None


class AcademicYearRead(BaseModel):
    id: int
    organization_id: int
    name: str
    start_date: date
    end_date: date
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


# ── Geo (read-only) ───────────────────────────────────────────────────────────

class DivisionRead(BaseModel):
    id: int
    name: str
    bn_name: Optional[str]
    model_config = ConfigDict(from_attributes=True)


class DistrictRead(BaseModel):
    id: int
    division_id: int
    name: str
    bn_name: Optional[str]
    model_config = ConfigDict(from_attributes=True)


class UpazilaRead(BaseModel):
    id: int
    district_id: int
    name: str
    bn_name: Optional[str]
    model_config = ConfigDict(from_attributes=True)


class PostOfficeRead(BaseModel):
    id: int
    upazila_id: int
    name: str
    bn_name: Optional[str]
    post_code: Optional[str]
    model_config = ConfigDict(from_attributes=True)


class VillageRead(BaseModel):
    id: int
    post_office_id: int
    name: str
    bn_name: Optional[str]
    model_config = ConfigDict(from_attributes=True)
