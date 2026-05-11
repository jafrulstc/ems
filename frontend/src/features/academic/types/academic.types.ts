export interface AcademicClass {
  id: number;
  name: string;
  name_bn?: string | null;
  numeric_level?: number | null;
  is_active: boolean;
  organization_id: number;
}

export interface ClassCreatePayload {
  name: string;
  name_bn?: string | null;
  numeric_level?: number | null;
  is_active?: boolean;
}

export interface ClassUpdatePayload {
  name?: string;
  name_bn?: string | null;
  numeric_level?: number | null;
  is_active?: boolean;
}

export interface Section {
  id: number;
  name: string;
  name_bn?: string | null;
  class_id: number;
  class_name?: string;
  organization_id: number;
}

export interface SectionCreatePayload {
  name: string;
  name_bn?: string | null;
  class_id: number;
}

export interface SectionUpdatePayload {
  name?: string;
  name_bn?: string | null;
  class_id?: number;
}

export interface Subject {
  id: number;
  name: string;
  name_bn?: string | null;
  code?: string | null;
  is_optional: boolean;
  organization_id: number;
}

export interface SubjectCreatePayload {
  name: string;
  name_bn?: string | null;
  code?: string | null;
  is_optional?: boolean;
}

export interface SubjectUpdatePayload {
  name?: string;
  name_bn?: string | null;
  code?: string | null;
  is_optional?: boolean;
}

export interface ClassSubject {
  id: number;
  organization_id: number;
  class_id: number;
  subject_id: number;
  full_marks: number;
  pass_marks: number;
  class_name?: string;
  subject_name?: string;
  subject_name_bn?: string | null;
}

export interface ClassSubjectCreatePayload {
  class_id: number;
  subject_id: number;
  full_marks?: number;
  pass_marks?: number;
}

export interface ClassSubjectUpdatePayload {
  full_marks?: number;
  pass_marks?: number;
}
