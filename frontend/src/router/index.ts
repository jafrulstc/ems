import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/auth/LoginView.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/',
      component: () => import('../layouts/DashboardLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'dashboard',
          component: () => import('../views/dashboard/DashboardView.vue')
        },
        {
          path: 'academic-setup',
          name: 'academic-setup',
          component: () => import('../views/academic/AcademicSetupView.vue')
        },
        {
          path: 'students',
          name: 'students',
          component: () => import('../views/students/StudentListView.vue')
        },
        {
          path: 'exam-setup',
          name: 'exam-setup',
          component: () => import('../views/exams/ExamSetupView.vue')
        },
        {
          path: 'mark-entry',
          redirect: { name: 'exam-setup' }
        },
        {
          path: 'tenant-setup',
          name: 'tenant-setup',
          component: () => import('../views/settings/TenantSetupView.vue')
        }
      ]
    }
  ]
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  const isAuthenticated = authStore.isAuthenticated;

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'login' });
  } else if (to.meta.requiresGuest && isAuthenticated) {
    next({ name: 'dashboard' });
  } else {
    next();
  }
});

export default router;
