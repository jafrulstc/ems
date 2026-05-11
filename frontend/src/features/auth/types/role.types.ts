export interface PermissionRead {
  id: number;
  key: string;
  label: string;
  module: string;
  action: string;
}

export interface Role {
  id: number;
  organization_id: number;
  name: string;
  description: string | null;
}

export interface RoleWithPermissions extends Role {
  permissions: PermissionRead[];
}

export interface RoleCreatePayload {
  name: string;
  description?: string;
}

export interface RoleUpdatePayload {
  name?: string | null;
  description?: string | null;
}
