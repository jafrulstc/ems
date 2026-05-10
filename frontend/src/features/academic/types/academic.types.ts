export interface AcademicClass {
  id: number;
  name: string;
  level: number;
  has_groups: boolean;
  is_active: boolean;
  organization_id: number;
}

export interface ClassCreatePayload {
  name: string;
  level: number;
  has_groups?: boolean;
  is_active?: boolean;
}

export interface ClassUpdatePayload {
  name?: string;
  level?: number;
  has_groups?: boolean;
  is_active?: boolean;
}

export interface Section {
  id: number;
  name: string;
  class_id: number;
  class_group_id?: number | null;
  shift_id?: number | null;
  capacity: number;
  is_active: boolean;
  class_name?: string; // Optional joined field
  organization_id: number;
}

export interface SectionCreatePayload {
  name: string;
  class_id: number;
  class_group_id?: number | null;
  shift_id?: number | null;
  capacity?: number;
  is_active?: boolean;
}

export interface SectionUpdatePayload {
  name?: string;
  class_id?: number;
  class_group_id?: number | null;
  shift_id?: number | null;
  capacity?: number;
  is_active?: boolean;
}

export interface Subject {
  id: number;
  name: string;
  code: string;
  credit_hours: number;
  subject_type: string;
  is_active: boolean;
  organization_id: number;
}

export interface SubjectCreatePayload {
  name: string;
  code: string;
  credit_hours?: number;
  subject_type?: string;
  is_active?: boolean;
}

export interface SubjectUpdatePayload {
  name?: string;
  code?: string;
  credit_hours?: number;
  subject_type?: string;
  is_active?: boolean;
}
