import uuid
from datetime import date, time
from typing import Literal

from pydantic import BaseModel, ConfigDict


class ExamTypeBase(BaseModel):
    name: str

class ExamTypeCreate(ExamTypeBase):
    pass

class ExamTypeRead(ExamTypeBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)

class ExamBase(BaseModel):
    name: str
    start_date: date
    end_date: date
    academic_year_id: uuid.UUID
    exam_type_id: uuid.UUID | None = None
    max_failing_subjects: int = 0

class ExamCreate(ExamBase):
    pass

class ExamRead(ExamBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)

class ExamScheduleBase(BaseModel):
    exam_id: uuid.UUID
    class_id: uuid.UUID
    subject_id: uuid.UUID
    exam_date: date
    start_time: time | None = None
    end_time: time | None = None
    full_marks: float = 100.0
    pass_marks: float = 33.0

class ExamScheduleCreate(ExamScheduleBase):
    pass

class ExamScheduleRead(ExamScheduleBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)

class ExamResultBase(BaseModel):
    enrollment_id: uuid.UUID
    exam_schedule_id: uuid.UUID
    obtained_marks: float
    grade: str | None = None
    status: Literal["PRESENT", "ABSENT", "WITHHELD", "EXPELLED"] = "PRESENT"

class ExamResultCreate(ExamResultBase):
    pass

class ExamResultRead(ExamResultBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)

class GradingScaleBase(BaseModel):
    grade_name: str
    min_marks: float
    max_marks: float
    grade_point: float
    is_pass: bool = True

class GradingScaleCreate(GradingScaleBase):
    pass

class GradingScaleRead(GradingScaleBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)
