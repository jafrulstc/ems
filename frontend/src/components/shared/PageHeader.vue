<script setup lang="ts">
defineProps<{
  title: string;
  subtitle?: string;
  icon?: string;
}>();
</script>

<template>
  <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
    <div class="flex items-center gap-3">
      <div v-if="icon" class="w-10 h-10 rounded-xl bg-primary-50 dark:bg-primary-950 flex items-center justify-center shrink-0">
        <i :class="[icon, 'text-primary-600 dark:text-primary-400']" />
      </div>
      <div>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-white leading-tight">{{ title }}</h1>
        <p v-if="subtitle" class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">{{ subtitle }}</p>
      </div>
    </div>
    <div class="flex items-center gap-2">
      <slot name="actions" />
    </div>
  </div>
</template>
