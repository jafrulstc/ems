export interface AcademicClass {
  id: number;
  name: string;
  numeric_level?: number | null;
  is_active: boolean;
  organization_id: number;
}

export interface ClassCreatePayload {
  name: string;
  numeric_level?: number | null;
  is_active?: boolean;
}

export interface ClassUpdatePayload {
  name?: string;
  numeric_level?: number | null;
  is_active?: boolean;
}

export interface Section {
  id: number;
  name: string;
  class_id: number;
  class_name?: string;
  organization_id: number;
}

export interface SectionCreatePayload {
  name: string;
  class_id: number;
}

export interface SectionUpdatePayload {
  name?: string;
  class_id?: number;
}

export interface Subject {
  id: number;
  name: string;
  code?: string | null;
  is_optional: boolean;
  organization_id: number;
}

export interface SubjectCreatePayload {
  name: string;
  code?: string | null;
  is_optional?: boolean;
}

export interface SubjectUpdatePayload {
  name?: string;
  code?: string | null;
  is_optional?: boolean;
}
