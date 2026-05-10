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
