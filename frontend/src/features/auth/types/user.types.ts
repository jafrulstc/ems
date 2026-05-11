import type { Role } from './role.types';

export interface User {
  id: number;
  organization_id: number;
  email: string;
  username: string | null;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  roles: Role[];
}

export interface UserCreatePayload {
  email: string;
  password: string;
  username?: string;
  full_name?: string;
  is_active?: boolean;
  is_superuser?: boolean;
}

export interface UserUpdatePayload {
  username?: string | null;
  full_name?: string | null;
  is_active?: boolean | null;
  password?: string | null;
}

export interface PermissionOverrideRead {
  id: number;
  user_id: number;
  permission_id: number;
  is_granted: boolean;
}

export interface PermissionOverrideUpsert {
  permission_key: string;
  is_granted: boolean;
}
