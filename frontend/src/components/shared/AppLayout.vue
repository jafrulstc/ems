<script setup lang="ts">
import AppTopbar from './AppTopbar.vue';
import AppSidebar from './AppSidebar.vue';
import { useUIStore } from '@/stores/ui.store';
import { RouterView } from 'vue-router';

const uiStore = useUIStore();
</script>

<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-950 font-sans text-slate-900 dark:text-slate-100 flex">
    <!-- Mobile overlay -->
    <Transition name="fade">
      <div
        v-if="uiStore.sidebarMobileOpen"
        class="fixed inset-0 bg-black/40 backdrop-blur-sm z-40 lg:hidden"
        @click="uiStore.closeMobileSidebar"
      />
    </Transition>

    <!-- Sidebar -->
    <AppSidebar />

    <!-- Main content area -->
    <div class="flex-1 flex flex-col min-w-0">
      <AppTopbar />

      <main class="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8">
        <RouterView v-slot="{ Component }">
          <Transition name="page" mode="out-in">
            <component :is="Component" />
          </Transition>
        </RouterView>

        <!-- Footer -->
        <footer class="mt-8 pt-6 border-t border-slate-200 dark:border-slate-800 text-center text-sm text-slate-400 dark:text-slate-600">
          <p>&copy; {{ new Date().getFullYear() }} Education Management System. All rights reserved.</p>
        </footer>
      </main>
    </div>
  </div>
</template>
