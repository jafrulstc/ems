<script setup lang="ts">
import { ref, onMounted } from 'vue';
import PageHeader from '@/components/shared/PageHeader.vue';
import { reportsApi } from '../api/reports.api';
import type { AcademicSummary } from '../types/reports.types';

const summary = ref<AcademicSummary | null>(null);
const loading = ref(true);

const fetchSummary = async () => {
  try {
    const res = await reportsApi.getAcademicSummary();
    summary.value = res.data.data!;
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

onMounted(fetchSummary);
</script>

<template>
  <div>
    <PageHeader title="Academic Reports" subtitle="Comprehensive academic analytics" icon="pi pi-chart-line" />

    <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
      <!-- Decorative header -->
      <div class="bg-gradient-to-r from-primary-50 to-teal-50 dark:from-primary-950 dark:to-teal-950 p-8 text-center">
        <div class="w-16 h-16 rounded-2xl bg-primary-100 dark:bg-primary-900 flex items-center justify-center mx-auto mb-4">
          <i class="pi pi-chart-line text-primary-600 dark:text-primary-400 text-2xl" />
        </div>
        <h2 class="text-xl font-bold text-slate-900 dark:text-white mb-2">Academic Summary</h2>
        <p class="text-slate-500 dark:text-slate-400 text-sm max-w-md mx-auto">
          Real-time institutional statistics and academic data overview.
        </p>
      </div>

      <!-- Real Data Content -->
      <div class="p-8">
        <div v-if="loading" class="grid grid-cols-1 md:grid-cols-3 gap-6 animate-pulse">
          <div v-for="i in 5" :key="i" class="h-32 bg-slate-100 dark:bg-slate-800 rounded-xl"></div>
        </div>
        
        <div v-else-if="summary" class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6">
          <div class="ems-card flex flex-col items-center justify-center p-6 text-center border-t-4 border-t-blue-500">
            <span class="text-3xl font-bold text-slate-900 dark:text-white">{{ summary.total_students }}</span>
            <span class="text-sm text-slate-500 dark:text-slate-400 mt-1 uppercase tracking-wider font-medium">Students</span>
          </div>
          <div class="ems-card flex flex-col items-center justify-center p-6 text-center border-t-4 border-t-emerald-500">
            <span class="text-3xl font-bold text-slate-900 dark:text-white">{{ summary.total_classes }}</span>
            <span class="text-sm text-slate-500 dark:text-slate-400 mt-1 uppercase tracking-wider font-medium">Classes</span>
          </div>
          <div class="ems-card flex flex-col items-center justify-center p-6 text-center border-t-4 border-t-amber-500">
            <span class="text-3xl font-bold text-slate-900 dark:text-white">{{ summary.total_sections }}</span>
            <span class="text-sm text-slate-500 dark:text-slate-400 mt-1 uppercase tracking-wider font-medium">Sections</span>
          </div>
          <div class="ems-card flex flex-col items-center justify-center p-6 text-center border-t-4 border-t-purple-500">
            <span class="text-3xl font-bold text-slate-900 dark:text-white">{{ summary.total_subjects }}</span>
            <span class="text-sm text-slate-500 dark:text-slate-400 mt-1 uppercase tracking-wider font-medium">Subjects</span>
          </div>
          <div class="ems-card flex flex-col items-center justify-center p-6 text-center border-t-4 border-t-rose-500">
            <span class="text-3xl font-bold text-slate-900 dark:text-white">{{ summary.total_enrollments }}</span>
            <span class="text-sm text-slate-500 dark:text-slate-400 mt-1 uppercase tracking-wider font-medium">Enrollments</span>
          </div>
        </div>

        <!-- Detailed Reports Section -->
        <div class="mt-12">
          <h3 class="text-lg font-bold text-slate-900 dark:text-white mb-6">Detailed Reports</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
             <div class="flex items-center gap-4 p-4 border border-slate-200 dark:border-slate-800 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors cursor-pointer group">
                <div class="w-12 h-12 rounded-lg bg-blue-100 dark:bg-blue-900/30 text-blue-600 flex items-center justify-center text-xl">
                  <i class="pi pi-users" />
                </div>
                <div>
                  <h4 class="font-bold text-slate-800 dark:text-slate-200">Enrollment List</h4>
                  <p class="text-xs text-slate-500">Exportable list of current student enrollments</p>
                </div>
                <i class="pi pi-chevron-right ml-auto text-slate-300 group-hover:text-primary-500 transition-colors" />
             </div>
             <div class="flex items-center gap-4 p-4 border border-slate-200 dark:border-slate-800 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors cursor-pointer group">
                <div class="w-12 h-12 rounded-lg bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 flex items-center justify-center text-xl">
                  <i class="pi pi-book" />
                </div>
                <div>
                  <h4 class="font-bold text-slate-800 dark:text-slate-200">Subject Distribution</h4>
                  <p class="text-xs text-slate-500">Analyze subject allocations across classes</p>
                </div>
                <i class="pi pi-chevron-right ml-auto text-slate-300 group-hover:text-primary-500 transition-colors" />
             </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
