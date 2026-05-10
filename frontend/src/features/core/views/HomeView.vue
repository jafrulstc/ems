<script setup lang="ts">
import { useI18n } from 'vue-i18n';
const { t } = useI18n();
</script>

<template>
  <div class="flex flex-col items-center justify-center min-h-[50vh]">
    <div class="text-center p-8 rounded-xl bg-surface-0 dark:bg-surface-900 shadow-sm border border-surface-200 dark:border-surface-800 transition-colors duration-200">
      <i class="pi pi-graduation-cap text-6xl text-primary-500 mb-4 block"></i>
      <h1 class="text-4xl font-bold text-surface-900 dark:text-surface-0 mb-2">
        {{ t('dashboard.welcome') }}
      </h1>
      <p class="text-surface-600 dark:text-surface-400">
        {{ t('dashboard.overview') }}
      </p>
    </div>
  </div>
</template>
