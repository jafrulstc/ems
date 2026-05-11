// ── ExamType ──────────────────────────────────────────────────────────────────

export interface ExamType {
  id: number;
  organization_id: number;
  name: string;
  description?: string | null;
}

export interface ExamTypeCreatePayload {
  name: string;
  description?: string | null;
}

export interface ExamTypeUpdatePayload {
  name?: string | null;
  description?: string | null;
}

// ── ExamBoard ─────────────────────────────────────────────────────────────────

export interface ExamBoard {
  id: number;
  organization_id: number;
  name: string;
  code?: string | null;
  description?: string | null;
}

export interface ExamBoardCreatePayload {
  name: string;
  code?: string | null;
  description?: string | null;
}

export interface ExamBoardUpdatePayload {
  name?: string | null;
  code?: string | null;
  description?: string | null;
}

// ── Routine ───────────────────────────────────────────────────────────────────

export interface Routine {
  id: number;
  organization_id: number;
  exam_type_id: number;
  class_id: number;
  subject_id: number;
  academic_year_id: number;
  exam_date?: string | null;
  start_time?: string | null;
  end_time?: string | null;
}

export interface RoutineCreatePayload {
  exam_type_id: number;
  class_id: number;
  subject_id: number;
  academic_year_id: number;
  exam_date?: string | null;
  start_time?: string | null;
  end_time?: string | null;
}

export interface RoutineUpdatePayload {
  exam_date?: string | null;
  start_time?: string | null;
  end_time?: string | null;
}

// ── GradingSystem + GradingRule ───────────────────────────────────────────────

export interface GradingRule {
  id: number;
  organization_id: number;
  grading_system_id: number;
  min_marks: number;
  max_marks: number;
  grade: string;
  grade_point: number;
  remarks?: string | null;
}

export interface GradingRuleCreatePayload {
  min_marks: number;
  max_marks: number;
  grade: string;
  grade_point: number;
  remarks?: string | null;
}

export interface GradingSystem {
  id: number;
  organization_id: number;
  name: string;
  is_default: boolean;
  rules: GradingRule[];
}

export interface GradingSystemCreatePayload {
  name: string;
  is_default?: boolean;
  rules?: GradingRuleCreatePayload[];
}

export interface GradingSystemUpdatePayload {
  name?: string | null;
  is_default?: boolean | null;
}

// ── Mark ──────────────────────────────────────────────────────────────────────

export interface Mark {
  id: number;
  organization_id: number;
  enrollment_id: number;
  class_subject_id: number;
  exam_type_id: number;
  marks_obtained?: number | null;
  is_absent: boolean;
}

export interface MarkEntry {
  enrollment_id: number;
  class_subject_id: number;
  marks_obtained?: number | null;
  is_absent: boolean;
}

export interface MarkBulkCreatePayload {
  exam_type_id: number;
  entries: MarkEntry[];
}

// ── Attendance ────────────────────────────────────────────────────────────────

export type AttendanceStatus = 'Present' | 'Absent' | 'Late';

export interface AttendanceRecord {
  id: number;
  organization_id: number;
  enrollment_id: number;
  record_date: string;
  status: string;
}

export interface AttendanceEntry {
  enrollment_id: number;
  status: AttendanceStatus;
}

export interface AttendanceBulkCreatePayload {
  record_date: string;
  entries: AttendanceEntry[];
}

// ── Result ────────────────────────────────────────────────────────────────────

export interface Result {
  id: number;
  organization_id: number;
  enrollment_id: number;
  exam_type_id: number;
  total_full_marks: number;
  total_obtained_marks: number;
  percentage: number;
  grade: string;
  grade_point: number;
  is_pass: boolean;
  remarks?: string | null;
}

export interface ResultGeneratePayload {
  exam_type_id: number | null;
  enrollment_ids?: number[] | null;
  grading_system_id?: number | null;
}

// ── ExamRegistration ──────────────────────────────────────────────────────────

export interface ExamRegistration {
  id: number;
  organization_id: number;
  enrollment_id: number;
  exam_type_id: number;
  exam_board_id?: number | null;
  board_roll_no?: string | null;
  board_registration_no?: string | null;
}

export interface ExamRegistrationCreatePayload {
  enrollment_id: number;
  exam_type_id: number;
  exam_board_id?: number | null;
  board_roll_no?: string | null;
  board_registration_no?: string | null;
}

export interface ExamRegistrationUpdatePayload {
  exam_board_id?: number | null;
  board_roll_no?: string | null;
  board_registration_no?: string | null;
}
