import type { Router } from 'vue-router';
import { useAuthStore } from '@/features/auth/stores/auth.store';

export function setupGuards(router: Router) {
  router.beforeEach(async (to, from) => {
    const authStore = useAuthStore();
    
    if (!authStore.initialized) {
      await authStore.fetchMe();
    }

    const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false);
    const isAuthenticated = authStore.isAuthenticated;

    if (requiresAuth && !isAuthenticated) {
      return { name: 'login', query: { redirect: to.fullPath } };
    } else if (to.name === 'login' && isAuthenticated) {
      return { name: 'home' };
    }
  });
}
