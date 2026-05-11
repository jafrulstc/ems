<script setup lang="ts">
defineProps<{
  icon?: string;
  title: string;
  description?: string;
}>();
</script>

<template>
  <div class="flex flex-col items-center justify-center py-16">
    <div class="w-16 h-16 rounded-2xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center mb-4">
      <i :class="[icon || 'pi pi-inbox', 'text-2xl text-slate-400 dark:text-slate-500']" />
    </div>
    <p class="text-base font-medium text-slate-500 dark:text-slate-400">{{ title }}</p>
    <p v-if="description" class="text-sm text-slate-400 dark:text-slate-500 mt-1 text-center max-w-sm">{{ description }}</p>
  </div>
</template>
