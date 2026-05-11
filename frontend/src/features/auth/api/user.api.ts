import { useApi } from '@/composables/useApi';
import type { APIResponse, PaginatedResponse } from '@/types/api.types';
import type {
  User, UserCreatePayload, UserUpdatePayload,
  PermissionOverrideRead, PermissionOverrideUpsert,
} from '../types/user.types';

export const userApi = {
  getUsers(page = 1, size = 50) {
    return useApi().get<PaginatedResponse<User>>(`/auth/users?page=${page}&size=${size}`);
  },

  createUser(payload: UserCreatePayload) {
    return useApi().post<APIResponse<User>>('/auth/users', payload);
  },

  getUser(id: number) {
    return useApi().get<APIResponse<User>>(`/auth/users/${id}`);
  },

  updateUser(id: number, payload: UserUpdatePayload) {
    return useApi().put<APIResponse<User>>(`/auth/users/${id}`, payload);
  },

  deleteUser(id: number) {
    return useApi().delete<APIResponse<null>>(`/auth/users/${id}`);
  },

  getOverrides(id: number) {
    return useApi().get<APIResponse<PermissionOverrideRead[]>>(`/auth/users/${id}/overrides`);
  },

  upsertOverrides(id: number, overrides: PermissionOverrideUpsert[]) {
    return useApi().put<APIResponse<PermissionOverrideRead[]>>(`/auth/users/${id}/overrides`, overrides);
  },

  setRoles(id: number, roleIds: number[]) {
    return useApi().put<APIResponse<User>>(`/auth/users/${id}/roles`, roleIds);
  },
};
