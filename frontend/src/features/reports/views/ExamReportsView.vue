<script setup lang="ts">
import PageHeader from '@/components/shared/PageHeader.vue';
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
        <h2 class="text-xl font-bold text-slate-900 dark:text-white mb-2">Exam Reports</h2>
        <p class="text-slate-500 dark:text-slate-400 text-sm max-w-md mx-auto">
          Comprehensive examination analytics including results analysis, grade distribution, pass rates, and comparison reports.
        </p>
      </div>

      <!-- Coming soon content -->
      <div class="p-8">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="border border-slate-200 dark:border-slate-700 rounded-xl p-5 text-center opacity-60">
            <i class="pi pi-chart-bar text-2xl text-slate-400 mb-3 block" />
            <h3 class="font-semibold text-slate-700 dark:text-slate-300 text-sm">Results Overview</h3>
            <p class="text-xs text-slate-400 mt-1">Exam results summary and analysis</p>
          </div>
          <div class="border border-slate-200 dark:border-slate-700 rounded-xl p-5 text-center opacity-60">
            <i class="pi pi-sort-alt text-2xl text-slate-400 mb-3 block" />
            <h3 class="font-semibold text-slate-700 dark:text-slate-300 text-sm">Grade Distribution</h3>
            <p class="text-xs text-slate-400 mt-1">GPA and grade frequency analysis</p>
          </div>
          <div class="border border-slate-200 dark:border-slate-700 rounded-xl p-5 text-center opacity-60">
            <i class="pi pi-arrows-h text-2xl text-slate-400 mb-3 block" />
            <h3 class="font-semibold text-slate-700 dark:text-slate-300 text-sm">Comparison Reports</h3>
            <p class="text-xs text-slate-400 mt-1">Cross-exam and year-over-year comparison</p>
          </div>
        </div>

        <div class="mt-8 text-center">
          <span class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 text-sm font-medium">
            <i class="pi pi-clock" />
            Coming Soon
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
