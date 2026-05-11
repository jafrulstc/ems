import { useApi } from '@/composables/useApi';
import type { APIResponse } from '@/types/api.types';
import type {
  RoleWithPermissions, RoleCreatePayload, RoleUpdatePayload,
} from '../types/role.types';
import type { PermissionRead } from '../types/role.types';

export const roleApi = {
  getRoles() {
    return useApi().get<APIResponse<RoleWithPermissions[]>>('/auth/roles');
  },

  createRole(payload: RoleCreatePayload) {
    return useApi().post<APIResponse<RoleWithPermissions>>('/auth/roles', payload);
  },

  updateRole(id: number, payload: RoleUpdatePayload) {
    return useApi().put<APIResponse<RoleWithPermissions>>(`/auth/roles/${id}`, payload);
  },

  deleteRole(id: number) {
    return useApi().delete<APIResponse<null>>(`/auth/roles/${id}`);
  },

  assignPermissions(id: number, permissionKeys: string[]) {
    return useApi().post<APIResponse<RoleWithPermissions>>(`/auth/roles/${id}/permissions`, permissionKeys);
  },
};

export const permissionApi = {
  getPermissions() {
    return useApi().get<APIResponse<PermissionRead[]>>('/auth/permissions');
  },
};
