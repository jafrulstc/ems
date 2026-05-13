<script setup lang="ts">
import { ref, onMounted } from 'vue';
import PageHeader from '@/components/shared/PageHeader.vue';
import { reportsApi } from '../api/reports.api';
import type { ExamSummary } from '../types/reports.types';

const summary = ref<ExamSummary | null>(null);
const loading = ref(true);

const fetchSummary = async () => {
  try {
    const res = await reportsApi.getExamSummary();
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
    <PageHeader title="Exam Reports" subtitle="Examination analytics and results" icon="pi pi-file-check" />

    <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
      <!-- Decorative header -->
      <div class="bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-950 dark:to-orange-950 p-8 text-center">
        <div class="w-16 h-16 rounded-2xl bg-amber-100 dark:bg-amber-900 flex items-center justify-center mx-auto mb-4">
          <i class="pi pi-file-check text-amber-600 dark:text-amber-400 text-2xl" />
        </div>
        <h2 class="text-xl font-bold text-slate-900 dark:text-white mb-2">Examination Summary</h2>
        <p class="text-slate-500 dark:text-slate-400 text-sm max-w-md mx-auto">
          Comprehensive summary of examination activities and result computations.
        </p>
      </div>

      <!-- Real Data Content -->
      <div class="p-8">
        <div v-if="loading" class="grid grid-cols-1 md:grid-cols-3 gap-6 animate-pulse">
          <div v-for="i in 3" :key="i" class="h-32 bg-slate-100 dark:bg-slate-800 rounded-xl"></div>
        </div>
        
        <div v-else-if="summary" class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="ems-card flex flex-col items-center justify-center p-8 text-center border-t-4 border-t-amber-500">
            <span class="text-4xl font-bold text-slate-900 dark:text-white">{{ summary.total_exam_types }}</span>
            <span class="text-sm text-slate-500 dark:text-slate-400 mt-2 uppercase tracking-wider font-semibold">Exam Types</span>
          </div>
          <div class="ems-card flex flex-col items-center justify-center p-8 text-center border-t-4 border-t-orange-500">
            <span class="text-4xl font-bold text-slate-900 dark:text-white">{{ summary.total_marks_entered }}</span>
            <span class="text-sm text-slate-500 dark:text-slate-400 mt-2 uppercase tracking-wider font-semibold">Marks Entered</span>
          </div>
          <div class="ems-card flex flex-col items-center justify-center p-8 text-center border-t-4 border-t-red-500">
            <span class="text-4xl font-bold text-slate-900 dark:text-white">{{ summary.total_results_computed }}</span>
            <span class="text-sm text-slate-500 dark:text-slate-400 mt-2 uppercase tracking-wider font-semibold">Results Computed</span>
          </div>
        </div>

        <!-- Detailed Reports Section -->
        <div class="mt-12">
          <h3 class="text-lg font-bold text-slate-900 dark:text-white mb-6">Exam Analytics</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
             <div class="flex items-center gap-4 p-4 border border-slate-200 dark:border-slate-800 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors cursor-pointer group">
                <div class="w-12 h-12 rounded-lg bg-amber-100 dark:bg-amber-900/30 text-amber-600 flex items-center justify-center text-xl">
                  <i class="pi pi-chart-bar" />
                </div>
                <div>
                  <h4 class="font-bold text-slate-800 dark:text-slate-200">Grade Distribution</h4>
                  <p class="text-xs text-slate-500">Analyze GPA and grade frequency across exams</p>
                </div>
                <i class="pi pi-chevron-right ml-auto text-slate-300 group-hover:text-primary-500 transition-colors" />
             </div>
             <div class="flex items-center gap-4 p-4 border border-slate-200 dark:border-slate-800 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors cursor-pointer group">
                <div class="w-12 h-12 rounded-lg bg-orange-100 dark:bg-orange-900/30 text-orange-600 flex items-center justify-center text-xl">
                  <i class="pi pi-file-pdf" />
                </div>
                <div>
                  <h4 class="font-bold text-slate-800 dark:text-slate-200">Tabulation Sheets</h4>
                  <p class="text-xs text-slate-500">Generate and export class-wise tabulation sheets</p>
                </div>
                <i class="pi pi-chevron-right ml-auto text-slate-300 group-hover:text-primary-500 transition-colors" />
             </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
