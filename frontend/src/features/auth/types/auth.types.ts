export interface Role {
  id: number;
  organization_id: number;
  name: string;
  description?: string;
}

export interface User {
  id: number;
  email: string;
  username: string | null;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  organization_id: number;
  roles: Role[];
}

export interface UserMeResponse extends User {
  permissions: string[];
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface LoginPayload {
  org_slug: string;
  email: string;
  password: string;
}
