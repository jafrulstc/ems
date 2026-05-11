<script setup lang="ts">
import PageHeader from '@/components/shared/PageHeader.vue';
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
        <h2 class="text-xl font-bold text-slate-900 dark:text-white mb-2">Academic Reports</h2>
        <p class="text-slate-500 dark:text-slate-400 text-sm max-w-md mx-auto">
          Detailed academic analytics including enrollment trends, class performance, subject-wise analysis, and more.
        </p>
      </div>

      <!-- Coming soon content -->
      <div class="p-8">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="border border-slate-200 dark:border-slate-700 rounded-xl p-5 text-center opacity-60">
            <i class="pi pi-users text-2xl text-slate-400 mb-3 block" />
            <h3 class="font-semibold text-slate-700 dark:text-slate-300 text-sm">Enrollment Reports</h3>
            <p class="text-xs text-slate-400 mt-1">Student enrollment trends and statistics</p>
          </div>
          <div class="border border-slate-200 dark:border-slate-700 rounded-xl p-5 text-center opacity-60">
            <i class="pi pi-bookmark text-2xl text-slate-400 mb-3 block" />
            <h3 class="font-semibold text-slate-700 dark:text-slate-300 text-sm">Class Performance</h3>
            <p class="text-xs text-slate-400 mt-1">Class-wise academic performance</p>
          </div>
          <div class="border border-slate-200 dark:border-slate-700 rounded-xl p-5 text-center opacity-60">
            <i class="pi pi-book text-2xl text-slate-400 mb-3 block" />
            <h3 class="font-semibold text-slate-700 dark:text-slate-300 text-sm">Subject Analysis</h3>
            <p class="text-xs text-slate-400 mt-1">Subject-wise results and trends</p>
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
