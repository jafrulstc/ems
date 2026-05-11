import { useApi } from '@/composables/useApi';
import type { LoginPayload, AuthResponse, UserMeResponse } from '@/features/auth/types/auth.types';
import type { APIResponse } from '@/types/api.types';

export const authApi = {
  login(payload: LoginPayload) {
    return useApi().post<APIResponse<AuthResponse>>('/auth/login', payload);
  },

  logout() {
    return useApi().post<APIResponse<null>>('/auth/refresh');
  },

  getMe() {
    return useApi().get<APIResponse<UserMeResponse>>('/auth/me');
  },

  refreshToken() {
    return useApi().post<APIResponse<{ access_token: string }>>('/auth/refresh');
  },
};
