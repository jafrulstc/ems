"""Pydantic schemas for the Academic feature."""
from datetime import date
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict

BloodGroup = Literal["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
Gender = Literal["Male", "Female", "Other"]

# ── Class ─────────────────────────────────────────────────────────────────────

class ClassCreate(BaseModel):
    name: str
    name_bn: Optional[str] = None
    numeric_level: Optional[int] = None
    is_active: bool = True

class ClassUpdate(BaseModel):
    name: Optional[str] = None
    name_bn: Optional[str] = None
    numeric_level: Optional[int] = None
    is_active: Optional[bool] = None

class ClassRead(BaseModel):
    id: int; organization_id: int; name: str
    name_bn: Optional[str]; numeric_level: Optional[int]; is_active: bool
    model_config = ConfigDict(from_attributes=True)

# ── Section ───────────────────────────────────────────────────────────────────

class SectionCreate(BaseModel):
    class_id: int
    name: str
    name_bn: Optional[str] = None

class SectionUpdate(BaseModel):
    name: Optional[str] = None
    name_bn: Optional[str] = None

class SectionRead(BaseModel):
    id: int; organization_id: int; class_id: int; name: str
    name_bn: Optional[str]
    model_config = ConfigDict(from_attributes=True)

# ── Subject ───────────────────────────────────────────────────────────────────

class SubjectCreate(BaseModel):
    name: str
    name_bn: Optional[str] = None
    code: Optional[str] = None
    is_optional: bool = False

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    name_bn: Optional[str] = None
    code: Optional[str] = None
    is_optional: Optional[bool] = None

class SubjectRead(BaseModel):
    id: int; organization_id: int; name: str
    name_bn: Optional[str]; code: Optional[str]; is_optional: bool
    model_config = ConfigDict(from_attributes=True)

# ── ClassSubject ──────────────────────────────────────────────────────────────

class ClassSubjectCreate(BaseModel):
    class_id: int; subject_id: int
    full_marks: int = 100; pass_marks: int = 33

class ClassSubjectUpdate(BaseModel):
    full_marks: Optional[int] = None
    pass_marks: Optional[int] = None

class ClassSubjectRead(BaseModel):
    id: int; organization_id: int; class_id: int
    subject_id: int; full_marks: int; pass_marks: int
    model_config = ConfigDict(from_attributes=True)

# ── Student ───────────────────────────────────────────────────────────────────

class StudentCreate(BaseModel):
    registration_no: str; full_name: str
    gender: Optional[Gender] = None
    dob: Optional[date] = None
    blood_group: Optional[BloodGroup] = None
    village_id: Optional[int] = None
    user_id: Optional[int] = None

class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    gender: Optional[Gender] = None
    dob: Optional[date] = None
    blood_group: Optional[BloodGroup] = None
    village_id: Optional[int] = None
    user_id: Optional[int] = None

class StudentRead(BaseModel):
    id: int; organization_id: int; registration_no: str
    full_name: str; gender: Optional[str]; dob: Optional[date]
    blood_group: Optional[str]; village_id: Optional[int]
    user_id: Optional[int]
    model_config = ConfigDict(from_attributes=True)

# ── Guardian ──────────────────────────────────────────────────────────────────

class GuardianCreate(BaseModel):
    name: str; relation: str
    phone: Optional[str] = None
    email: Optional[str] = None
    is_primary: bool = False

class GuardianUpdate(BaseModel):
    name: Optional[str] = None
    relation: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_primary: Optional[bool] = None

class GuardianRead(BaseModel):
    id: int; organization_id: int; student_id: int
    name: str; relation: str; phone: Optional[str]
    email: Optional[str]; is_primary: bool
    model_config = ConfigDict(from_attributes=True)

# ── Enrollment ────────────────────────────────────────────────────────────────

class EnrollmentCreate(BaseModel):
    student_id: int; section_id: int
    academic_year_id: int
    roll_no: Optional[str] = None
    is_active: bool = True

class EnrollmentUpdate(BaseModel):
    roll_no: Optional[str] = None
    is_active: Optional[bool] = None

class EnrollmentRead(BaseModel):
    id: int; organization_id: int; student_id: int
    section_id: int; academic_year_id: int
    roll_no: Optional[str]; is_active: bool
    model_config = ConfigDict(from_attributes=True)
