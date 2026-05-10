import { useAuthStore } from '@/features/auth/stores/auth.store';
import { computed } from 'vue';

export function usePermission() {
  const authStore = useAuthStore();

  const hasPermission = (key: string) => computed(() => authStore.hasPermission(key));

  return {
    hasPermission,
    isSuperuser: computed(() => !!authStore.user?.is_superuser),
  };
}
