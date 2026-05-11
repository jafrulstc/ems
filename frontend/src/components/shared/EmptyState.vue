<script setup lang="ts">
defineProps<{
  icon?: string;
  title: string;
  description?: string;
}>();
</script>

<template>
  <div class="flex flex-col items-center justify-center py-16 text-slate-400 dark:text-slate-600">
    <i :class="[icon || 'pi pi-inbox', 'text-5xl mb-4']" />
    <p class="text-base font-medium text-slate-500 dark:text-slate-400">{{ title }}</p>
    <p v-if="description" class="text-sm mt-1">{{ description }}</p>
  </div>
</template>
