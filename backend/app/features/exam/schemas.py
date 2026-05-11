"""Pydantic schemas for the Exam feature."""
from datetime import date, time
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict

AttendanceStatus = Literal["Present", "Absent", "Late"]

# ── ExamType ──────────────────────────────────────────────────────────────────

class ExamTypeCreate(BaseModel):
    name: str
    name_bn: Optional[str] = None
    description: Optional[str] = None

class ExamTypeUpdate(BaseModel):
    name: Optional[str] = None
    name_bn: Optional[str] = None
    description: Optional[str] = None

class ExamTypeRead(BaseModel):
    id: int; organization_id: int; name: str; name_bn: Optional[str]; description: Optional[str]
    model_config = ConfigDict(from_attributes=True)

# ── ExamRoutine ───────────────────────────────────────────────────────────────

class RoutineCreate(BaseModel):
    exam_type_id: int; class_id: int; subject_id: int; academic_year_id: int
    exam_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None

class RoutineUpdate(BaseModel):
    exam_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None

class RoutineRead(BaseModel):
    id: int; organization_id: int; exam_type_id: int
    class_id: int; subject_id: int; academic_year_id: int
    exam_date: Optional[date]; start_time: Optional[time]; end_time: Optional[time]
    model_config = ConfigDict(from_attributes=True)

# ── GradingSystem + GradingRule ───────────────────────────────────────────────

class GradingRuleCreate(BaseModel):
    min_marks: float; max_marks: float
    grade: str; grade_point: float
    remarks: Optional[str] = None

class GradingRuleRead(BaseModel):
    id: int; organization_id: int; grading_system_id: int
    min_marks: float; max_marks: float; grade: str; grade_point: float
    remarks: Optional[str]
    model_config = ConfigDict(from_attributes=True)

class GradingSystemCreate(BaseModel):
    name: str
    is_default: bool = False
    rules: List[GradingRuleCreate] = []

class GradingSystemUpdate(BaseModel):
    name: Optional[str] = None
    is_default: Optional[bool] = None

class GradingSystemRead(BaseModel):
    id: int; organization_id: int; name: str; is_default: bool
    rules: List[GradingRuleRead] = []
    model_config = ConfigDict(from_attributes=True)

# ── Mark ──────────────────────────────────────────────────────────────────────

class MarkEntry(BaseModel):
    enrollment_id: int
    class_subject_id: int
    marks_obtained: Optional[float] = None
    is_absent: bool = False

class MarkBulkCreate(BaseModel):
    exam_type_id: int
    entries: List[MarkEntry]

class MarkRead(BaseModel):
    id: int; organization_id: int; enrollment_id: int
    class_subject_id: int; exam_type_id: int
    marks_obtained: Optional[float]; is_absent: bool
    model_config = ConfigDict(from_attributes=True)

# ── AttendanceRecord ──────────────────────────────────────────────────────────

class AttendanceEntry(BaseModel):
    enrollment_id: int
    status: AttendanceStatus

class AttendanceBulkCreate(BaseModel):
    record_date: date
    entries: List[AttendanceEntry]

class AttendanceRead(BaseModel):
    id: int; organization_id: int; enrollment_id: int
    record_date: date; status: str
    model_config = ConfigDict(from_attributes=True)

# ── Result ────────────────────────────────────────────────────────────────────

class ResultGenerateRequest(BaseModel):
    exam_type_id: int
    enrollment_ids: Optional[List[int]] = None  # None = generate for all in org
    grading_system_id: Optional[int] = None     # None = use default

class ResultRead(BaseModel):
    id: int; organization_id: int; enrollment_id: int; exam_type_id: int
    total_full_marks: int; total_obtained_marks: float
    percentage: float; grade: str; grade_point: float
    is_pass: bool; remarks: Optional[str]
    model_config = ConfigDict(from_attributes=True)

# ── ExamBoard ─────────────────────────────────────────────────────────────────

class ExamBoardCreate(BaseModel):
    name: str
    code: Optional[str] = None
    description: Optional[str] = None

class ExamBoardUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None

class ExamBoardRead(BaseModel):
    id: int; organization_id: int; name: str
    code: Optional[str]; description: Optional[str]
    model_config = ConfigDict(from_attributes=True)

# ── ExamRegistration ──────────────────────────────────────────────────────────

class ExamRegistrationCreate(BaseModel):
    enrollment_id: int
    exam_type_id: int
    exam_board_id: Optional[int] = None
    board_roll_no: Optional[str] = None
    board_registration_no: Optional[str] = None

class ExamRegistrationBulkCreate(BaseModel):
    exam_type_id: int
    exam_board_id: Optional[int] = None
    enrollment_ids: List[int]

class ExamRegistrationUpdate(BaseModel):
    exam_board_id: Optional[int] = None
    board_roll_no: Optional[str] = None
    board_registration_no: Optional[str] = None

class ExamRegistrationRead(BaseModel):
    id: int; organization_id: int; enrollment_id: int
    exam_type_id: int; exam_board_id: Optional[int]
    board_roll_no: Optional[str]; board_registration_no: Optional[str]
    model_config = ConfigDict(from_attributes=True)
