import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict


class GuardianBase(BaseModel):
    name: str
    phone: str
    email: str | None = None

class GuardianCreate(GuardianBase):
    pass

class GuardianRead(GuardianBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)

class StudentBase(BaseModel):
    student_id_no: int
    full_name: str
    date_of_birth: date
    gender: str
    blood_group: str | None = None
    address: str | None = None
    profile_picture_url: str | None = None
    guardian_id: uuid.UUID | None = None
    branch_id: uuid.UUID

class StudentCreate(StudentBase):
    pass

class StudentRead(StudentBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)

class EnrollmentBase(BaseModel):
    roll_number: str | None = None
    enrollment_date: date
    student_id: uuid.UUID
    academic_year_id: uuid.UUID
    class_id: uuid.UUID
    section_id: uuid.UUID | None = None
    branch_id: uuid.UUID
    status: str = "active"

class EnrollmentCreate(EnrollmentBase):
    pass

class EnrollmentRead(EnrollmentBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)
