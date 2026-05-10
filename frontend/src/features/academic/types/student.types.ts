export interface Guardian {
  id: number;
  organization_id: number;
  user_id?: number;
  father_name?: string;
  mother_name?: string;
  guardian_name: string;
  relation: string;
  phone: string;
  email?: string;
  national_id?: string;
  occupation?: string;
  is_active: boolean;
}

export interface GuardianCreatePayload {
  user_id?: number | null;
  father_name?: string | null;
  mother_name?: string | null;
  guardian_name: string;
  relation: string;
  phone: string;
  email?: string | null;
  national_id?: string | null;
  occupation?: string | null;
  is_active?: boolean;
}

export interface GuardianUpdatePayload {
  user_id?: number | null;
  father_name?: string | null;
  mother_name?: string | null;
  guardian_name?: string;
  relation?: string;
  phone?: string;
  email?: string | null;
  national_id?: string | null;
  occupation?: string | null;
  is_active?: boolean;
}

export interface Student {
  id: number;
  organization_id: number;
  user_id?: number;
  student_id: string;
  first_name: string;
  last_name: string;
  date_of_birth: string; // ISO format date
  gender: string;
  blood_group?: string;
  religion?: string;
  village_id?: number;
  address_line?: string;
  guardian_id: number;
  guardian_name?: string; // Optional joined field
  is_active: boolean;
}

export interface StudentCreatePayload {
  user_id?: number | null;
  student_id: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: string;
  blood_group?: string | null;
  religion?: string | null;
  village_id?: number | null;
  address_line?: string | null;
  guardian_id: number;
  is_active?: boolean;
}

export interface StudentUpdatePayload {
  user_id?: number | null;
  student_id?: string;
  first_name?: string;
  last_name?: string;
  date_of_birth?: string;
  gender?: string;
  blood_group?: string | null;
  religion?: string | null;
  village_id?: number | null;
  address_line?: string | null;
  guardian_id?: number;
  is_active?: boolean;
}
