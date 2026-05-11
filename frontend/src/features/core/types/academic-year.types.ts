export interface AcademicYear {
  id: number;
  organization_id: number;
  name: string;
  start_date: string;
  end_date: string;
  is_active: boolean;
}

export interface AcademicYearCreatePayload {
  name: string;
  start_date: string;
  end_date: string;
  is_active?: boolean;
}

export interface AcademicYearUpdatePayload {
  name?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  is_active?: boolean | null;
}
