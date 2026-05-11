export type Gender = 'Male' | 'Female' | 'Other';
export type BloodGroup = 'A+' | 'A-' | 'B+' | 'B-' | 'O+' | 'O-' | 'AB+' | 'AB-';

export interface Student {
  id: number;
  organization_id: number;
  registration_no: string;
  full_name: string;
  gender?: Gender | null;
  dob?: string | null;
  blood_group?: BloodGroup | null;
  village_id?: number | null;
  user_id?: number | null;
}

export interface StudentCreatePayload {
  registration_no: string;
  full_name: string;
  gender?: Gender | null;
  dob?: string | null;
  blood_group?: BloodGroup | null;
  village_id?: number | null;
}

export interface StudentUpdatePayload {
  registration_no?: string;
  full_name?: string;
  gender?: Gender | null;
  dob?: string | null;
  blood_group?: BloodGroup | null;
  village_id?: number | null;
}

export interface Guardian {
  id: number;
  organization_id: number;
  student_id: number;
  name: string;
  relation: string;
  phone?: string | null;
  email?: string | null;
  is_primary: boolean;
}

export interface GuardianCreatePayload {
  student_id: number;
  name: string;
  relation: string;
  phone?: string | null;
  email?: string | null;
  is_primary?: boolean;
}

export interface GuardianUpdatePayload {
  name?: string;
  relation?: string;
  phone?: string | null;
  email?: string | null;
  is_primary?: boolean;
}
