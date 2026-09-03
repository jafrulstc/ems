import { defineStore } from 'pinia';
import api from '../utils/api';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('access_token') as string | null,
    tenantSlug: localStorage.getItem('tenant_slug') as string | null,
    branchId: localStorage.getItem('branch_id') as string | null,
    user: null as any | null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    async login(email: string, password: string) {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      
      this.token = response.data.access_token;
      this.tenantSlug = response.data.tenant_slug;
      this.branchId = response.data.branch_id ?? null;

      if (this.token) localStorage.setItem('access_token', this.token);
      if (this.tenantSlug) localStorage.setItem('tenant_slug', this.tenantSlug);
      if (this.branchId) localStorage.setItem('branch_id', this.branchId);
      else localStorage.removeItem('branch_id');
    },
    
    logout() {
      this.token = null;
      this.tenantSlug = null;
      this.branchId = null;
      this.user = null;
      localStorage.removeItem('access_token');
      localStorage.removeItem('tenant_slug');
      localStorage.removeItem('branch_id');
    }
  }
});

