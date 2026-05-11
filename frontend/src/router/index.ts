import { createRouter, createWebHistory } from 'vue-router';
import AppLayout from '../components/shared/AppLayout.vue';
import { setupGuards } from './guards';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/features/auth/views/LoginView.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/',
      component: AppLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'home',
          component: () => import('@/features/core/views/HomeView.vue'),
        },
        {
          path: 'academic/classes',
          name: 'academic.classes',
          component: () => import('@/features/academic/views/ClassesView.vue'),
        },
        {
          path: 'academic/sections',
          name: 'academic.sections',
          component: () => import('@/features/academic/views/SectionsView.vue'),
        },
        {
          path: 'academic/subjects',
          name: 'academic.subjects',
          component: () => import('@/features/academic/views/SubjectsView.vue'),
        },
        {
          path: 'academic/students',
          name: 'academic.students',
          component: () => import('@/features/academic/views/StudentsView.vue'),
        },
        {
          path: 'academic/guardians',
          name: 'academic.guardians',
          component: () => import('@/features/academic/views/GuardiansView.vue'),
        },
        {
          path: 'academic/enrollments',
          name: 'academic.enrollments',
          component: () => import('@/features/academic/views/EnrollmentsView.vue'),
        },
        {
          path: 'academic/class-subjects',
          name: 'academic.class-subjects',
          component: () => import('@/features/academic/views/ClassSubjectsView.vue'),
        },
        {
          path: 'exam/types',
          name: 'exam.types',
          component: () => import('@/features/exam/views/ExamTypesView.vue'),
        },
        {
          path: 'exam/routines',
          name: 'exam.routines',
          component: () => import('@/features/exam/views/ExamRoutinesView.vue'),
        },
        {
          path: 'exam/marks',
          name: 'exam.marks',
          component: () => import('@/features/exam/views/MarksEntryView.vue'),
        },
        {
          path: 'exam/results',
          name: 'exam.results',
          component: () => import('@/features/exam/views/ResultsView.vue'),
        },
        {
          path: 'core/academic-years',
          name: 'core.academic_years',
          component: () => import('@/features/core/views/AcademicYearsView.vue'),
        },
        {
          path: 'auth/users',
          name: 'auth.users',
          component: () => import('@/features/auth/views/UsersView.vue'),
        },
        {
          path: 'auth/roles',
          name: 'auth.roles',
          component: () => import('@/features/auth/views/RolesView.vue'),
        },
        {
          path: 'core/settings',
          name: 'core.settings',
          component: () => import('@/features/core/views/SettingsView.vue'),
        },
        {
          path: 'reports/academic',
          name: 'reports.academic',
          component: () => import('@/features/reports/views/AcademicReportsView.vue'),
        },
        {
          path: 'reports/exam',
          name: 'reports.exam',
          component: () => import('@/features/reports/views/ExamReportsView.vue'),
        },
      ],
    },
  ],
});

setupGuards(router);

export default router;
