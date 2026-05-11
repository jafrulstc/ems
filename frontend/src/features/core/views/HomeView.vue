<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from '@/features/auth/stores/auth.store';
import { academicApi } from '@/features/academic/api/academic.api';
import { studentApi } from '@/features/academic/api/student.api';
import { useI18n } from 'vue-i18n';

const authStore = useAuthStore();
const { t } = useI18n();

const stats = ref({
  students: 0,
  classes: 0,
  sections: 0,
  subjects: 0,
});
const loading = ref(true);

const userName = computed(() => authStore.user?.full_name || authStore.user?.email || 'User');
const userInitials = computed(() => {
  const name = userName.value;
  return name.split(' ').map((n: string) => n[0]).join('').toUpperCase().slice(0, 2);
});

onMounted(async () => {
  try {
    const [studentsRes, classesRes, sectionsRes, subjectsRes] = await Promise.allSettled([
      studentApi.getStudents(1, 1),
      academicApi.getClasses(1, 1),
      academicApi.getSections(1, 1),
      academicApi.getSubjects(1, 1),
    ]);
    if (studentsRes.status === 'fulfilled') stats.value.students = studentsRes.value.data.data?.total ?? 0;
    if (classesRes.status === 'fulfilled') stats.value.classes = classesRes.value.data.data?.total ?? 0;
    if (sectionsRes.status === 'fulfilled') stats.value.sections = sectionsRes.value.data.data?.total ?? 0;
    if (subjectsRes.status === 'fulfilled') stats.value.subjects = subjectsRes.value.data.data?.total ?? 0;
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
});

const statCards = computed(() => [
  { label: 'Total Students', value: stats.value.students, icon: 'pi pi-users', color: 'bg-primary-500', lightBg: 'bg-primary-50 dark:bg-primary-950', textColor: 'text-primary-600 dark:text-primary-400' },
  { label: 'Classes', value: stats.value.classes, icon: 'pi pi-bookmark', color: 'bg-amber-500', lightBg: 'bg-amber-50 dark:bg-amber-950', textColor: 'text-amber-600 dark:text-amber-400' },
  { label: 'Sections', value: stats.value.sections, icon: 'pi pi-th-large', color: 'bg-blue-500', lightBg: 'bg-blue-50 dark:bg-blue-950', textColor: 'text-blue-600 dark:text-blue-400' },
  { label: 'Subjects', value: stats.value.subjects, icon: 'pi pi-book', color: 'bg-purple-500', lightBg: 'bg-purple-50 dark:bg-purple-950', textColor: 'text-purple-600 dark:text-purple-400' },
]);
</script>

<template>
  <div class="space-y-8">
    <!-- Welcome hero -->
    <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-primary-600 via-primary-700 to-teal-600 p-6 md:p-8 text-white">
      <div class="absolute top-[-20%] right-[-5%] w-64 h-64 bg-white/5 rounded-full" />
      <div class="absolute bottom-[-30%] left-[10%] w-80 h-80 bg-white/5 rounded-full" />

      <div class="relative z-10 flex items-center gap-4">
        <div class="avatar-initials w-14 h-14 text-xl bg-white/20 backdrop-blur-sm">{{ userInitials }}</div>
        <div>
          <h1 class="text-2xl md:text-3xl font-bold">{{ t('dashboard.welcome') }}, {{ userName }}!</h1>
          <p class="text-primary-100 mt-1">Here's an overview of your education system today.</p>
        </div>
      </div>
    </div>

    <!-- Stats grid -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
      <div v-for="card in statCards" :key="card.label" class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5 card-hover">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-sm font-medium text-slate-500 dark:text-slate-400">{{ card.label }}</p>
            <p class="text-3xl font-bold text-slate-900 dark:text-white mt-2">
              <span v-if="loading" class="text-slate-300 dark:text-slate-600">--</span>
              <span v-else>{{ card.value.toLocaleString() }}</span>
            </p>
          </div>
          <div :class="[card.lightBg, 'w-10 h-10 rounded-lg flex items-center justify-center']">
            <i :class="[card.icon, card.textColor]" />
          </div>
        </div>
      </div>
    </div>

    <!-- Quick actions -->
    <div>
      <h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">Quick Actions</h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <router-link to="/academic/students" class="flex items-center gap-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 card-hover cursor-pointer no-underline">
          <div class="w-9 h-9 rounded-lg bg-primary-50 dark:bg-primary-950 flex items-center justify-center">
            <i class="pi pi-user-plus text-primary-600 dark:text-primary-400 text-sm" />
          </div>
          <span class="text-sm font-medium text-slate-700 dark:text-slate-300">Add Student</span>
        </router-link>
        <router-link to="/academic/classes" class="flex items-center gap-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 card-hover cursor-pointer no-underline">
          <div class="w-9 h-9 rounded-lg bg-amber-50 dark:bg-amber-950 flex items-center justify-center">
            <i class="pi pi-bookmark text-amber-600 dark:text-amber-400 text-sm" />
          </div>
          <span class="text-sm font-medium text-slate-700 dark:text-slate-300">Manage Classes</span>
        </router-link>
        <router-link to="/academic/subjects" class="flex items-center gap-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 card-hover cursor-pointer no-underline">
          <div class="w-9 h-9 rounded-lg bg-purple-50 dark:bg-purple-950 flex items-center justify-center">
            <i class="pi pi-book text-purple-600 dark:text-purple-400 text-sm" />
          </div>
          <span class="text-sm font-medium text-slate-700 dark:text-slate-300">Subjects</span>
        </router-link>
        <router-link to="/reports/academic" class="flex items-center gap-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 card-hover cursor-pointer no-underline">
          <div class="w-9 h-9 rounded-lg bg-blue-50 dark:bg-blue-950 flex items-center justify-center">
            <i class="pi pi-chart-bar text-blue-600 dark:text-blue-400 text-sm" />
          </div>
          <span class="text-sm font-medium text-slate-700 dark:text-slate-300">Reports</span>
        </router-link>
      </div>
    </div>

    <!-- Recent activity placeholder -->
    <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
      <h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">Recent Activity</h2>
      <div class="flex flex-col items-center justify-center py-12 text-slate-400 dark:text-slate-600">
        <i class="pi pi-clock text-4xl mb-3" />
        <p class="text-sm font-medium">Activity feed coming soon</p>
        <p class="text-xs mt-1">Recent changes and updates will appear here</p>
      </div>
    </div>
  </div>
</template>
