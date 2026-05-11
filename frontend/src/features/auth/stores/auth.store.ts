import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { authApi } from '@/features/auth/api/auth.api';
import type { LoginPayload, User } from '@/features/auth/types/auth.types';

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('access_token'));
  const user = ref<User | null>(null);
  const permissions = ref<string[]>([]);
  const loading = ref(false);
  const initialized = ref(false);

  const isAuthenticated = computed(() => !!token.value && !!user.value);

  const setToken = (newToken: string) => {
    token.value = newToken;
    localStorage.setItem('access_token', newToken);
  };

  const clearAuth = () => {
    token.value = null;
    user.value = null;
    permissions.value = [];
    localStorage.removeItem('access_token');
  };

  const fetchMe = async () => {
    if (!token.value) {
      initialized.value = true;
      return;
    }
    try {
      const res = await authApi.getMe();
      const meData = res.data.data!;
      user.value = {
        id: meData.id,
        email: meData.email,
        username: meData.username ?? null,
        full_name: meData.full_name ?? null,
        is_active: meData.is_active,
        is_superuser: meData.is_superuser,
        organization_id: meData.organization_id,
        roles: meData.roles ?? [],
      };
      permissions.value = meData.permissions ?? [];
    } catch (e) {
      clearAuth();
    } finally {
      initialized.value = true;
    }
  };

  const login = async (payload: LoginPayload) => {
    loading.value = true;
    try {
      const res = await authApi.login(payload);
      setToken(res.data.data!.access_token);
      await fetchMe();
    } finally {
      loading.value = false;
    }
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch (e) {
      // ignore
    } finally {
      clearAuth();
    }
  };

  const hasPermission = (key: string): boolean => {
    if (user.value?.is_superuser) return true;
    return permissions.value.includes(key);
  };

  return {
    token,
    user,
    permissions,
    loading,
    initialized,
    isAuthenticated,
    login,
    logout,
    fetchMe,
    hasPermission,
  };
});
