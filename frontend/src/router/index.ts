import { createRouter, createWebHistory } from 'vue-router';
import AppLayout from '../components/shared/AppLayout.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: AppLayout,
      children: [
        {
          path: '',
          name: 'home',
          component: () => import('../features/core/views/HomeView.vue'),
        },
      ],
    },
  ],
});

export default router;
