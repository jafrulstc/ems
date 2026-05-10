<script setup lang="ts">
import AppTopbar from './AppTopbar.vue';
import { RouterView } from 'vue-router';
</script>

<template>
  <div class="min-h-screen bg-surface-50 dark:bg-surface-950 transition-colors duration-200 font-sans text-surface-900 dark:text-surface-0 flex flex-col">
    <AppTopbar />
    
    <div class="flex flex-1 overflow-hidden">
      <!-- AppSidebar will go here later -->
      
      <main class="flex-1 overflow-y-auto p-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>
