import type { Router } from 'vue-router';
import { useAuthStore } from '@/features/auth/stores/auth.store';

export function setupGuards(router: Router) {
  router.beforeEach(async (to, from, next) => {
    const authStore = useAuthStore();
    
    // Ensure auth state is initialized (e.g., fetch user profile on first load)
    if (!authStore.initialized) {
      await authStore.fetchMe();
    }

    const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false);
    const isAuthenticated = authStore.isAuthenticated;

    if (requiresAuth && !isAuthenticated) {
      next({ name: 'login', query: { redirect: to.fullPath } });
    } else if (to.name === 'login' && isAuthenticated) {
      next({ name: 'home' });
    } else {
      next();
    }
  });
}
