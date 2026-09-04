import uuid
from datetime import date, time

from pydantic import BaseModel, ConfigDict


class DepartmentBase(BaseModel):
    name: str
    level: str | None = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentRead(DepartmentBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)

class AcademicYearBase(BaseModel):
    name: str
    start_date: date
    end_date: date

class AcademicYearCreate(AcademicYearBase):
    pass

class AcademicYearRead(AcademicYearBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)

class YearlyClassSubjectBase(BaseModel):
    academic_year_id: uuid.UUID
    class_id: uuid.UUID
    subject_id: uuid.UUID
    is_main_subject: bool = True
    affects_result_calculation: bool = True

class YearlyClassSubjectCreate(YearlyClassSubjectBase):
    pass

class YearlyClassSubjectRead(YearlyClassSubjectBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)

class ClassBase(BaseModel):
    name: str
    level: str | None = None
    department_id: uuid.UUID | None = None

class ClassCreate(ClassBase):
    pass

class ClassRead(ClassBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    department_name: str | None = None
    model_config = ConfigDict(from_attributes=True)

class SectionBase(BaseModel):
    name: str
    class_id: uuid.UUID
    branch_id: uuid.UUID
    shift_id: uuid.UUID | None = None

class SectionCreate(SectionBase):
    pass

class SectionRead(SectionBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)

class SubjectBase(BaseModel):
    name: str
    code: str

class SubjectCreate(SubjectBase):
    pass

class SubjectRead(SubjectBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)

class ShiftBase(BaseModel):
    name: str
    start_time: time | None = None
    end_time: time | None = None

class ShiftCreate(ShiftBase):
    pass

class ShiftRead(ShiftBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)
