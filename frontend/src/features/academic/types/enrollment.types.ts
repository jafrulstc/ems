export interface Enrollment {
  id: number;
  organization_id: number;
  student_id: number;
  section_id: number;
  academic_year_id: number;
  roll_no?: string | null;
  is_active: boolean;
}

export interface EnrollmentCreatePayload {
  student_id: number;
  section_id: number;
  academic_year_id: number;
  roll_no?: string | null;
  is_active?: boolean;
}

export interface EnrollmentUpdatePayload {
  roll_no?: string | null;
  is_active?: boolean | null;
}
