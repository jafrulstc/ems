<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useMenuStore } from '@/features/core/stores/menu.store';
import { usePermission } from '@/features/auth/composables/usePermission';
import { useUIStore } from '@/stores/ui.store';
import SidebarItem from './SidebarItem.vue';

const menuStore = useMenuStore();
const { hasPermission, isSuperuser } = usePermission();
const uiStore = useUIStore();

onMounted(() => {
  if (menuStore.tree.length === 0) {
    menuStore.fetchMenuTree();
  }
});

const filterMenu = (items: any[]): any[] => {
  return items
    .filter(item => item.is_active)
    .filter(item => {
      if (isSuperuser.value || !item.permission_key) return true;
      return hasPermission(item.permission_key).value;
    })
    .map(item => ({
      ...item,
      children: item.children ? filterMenu(item.children) : []
    }));
};

const visibleMenu = computed(() => filterMenu(menuStore.tree));
const collapsed = computed(() => uiStore.sidebarCollapsed);
</script>

<template>
  <!-- Mobile drawer -->
  <aside
    :class="[
      'fixed inset-y-0 left-0 z-50 w-72 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col transform lg:hidden',
      uiStore.sidebarMobileOpen ? 'translate-x-0' : '-translate-x-full'
    ]"
    style="transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);"
  >
    <!-- Logo -->
    <div class="h-16 flex items-center gap-3 px-5 border-b border-slate-200 dark:border-slate-800 shrink-0">
      <div class="w-9 h-9 rounded-lg bg-primary-600 text-white flex items-center justify-center font-bold text-lg shadow-sm">
        E
      </div>
      <span class="text-lg font-bold text-slate-900 dark:text-white truncate">EMS</span>
    </div>

    <!-- Mobile nav items -->
    <nav class="flex-1 overflow-y-auto py-3 px-3">
      <ul class="space-y-1">
        <SidebarItem 
          v-for="item in visibleMenu" 
          :key="item.id" 
          :item="item" 
        />
      </ul>
    </nav>
  </aside>

  <!-- Desktop sidebar -->
  <aside
    :class="[
      'hidden lg:flex flex-col bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 shrink-0 h-screen sticky top-0',
      collapsed ? 'w-[72px]' : 'w-64'
    ]"
    style="transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);"
  >
    <!-- Logo -->
    <div class="h-16 flex items-center gap-3 px-5 border-b border-slate-200 dark:border-slate-800 shrink-0">
      <div class="w-9 h-9 rounded-lg bg-primary-600 text-white flex items-center justify-center font-bold text-lg shadow-sm shrink-0">
        E
      </div>
      <span v-if="!collapsed" class="text-lg font-bold text-slate-900 dark:text-white truncate">EMS</span>
    </div>

    <!-- Nav -->
    <nav class="flex-1 overflow-y-auto py-3 px-3">
      <ul class="space-y-1">
        <SidebarItem 
          v-for="item in visibleMenu" 
          :key="item.id" 
          :item="item" 
          :collapsed="collapsed"
        />
      </ul>
    </nav>

    <!-- Sidebar footer -->
    <div class="p-3 border-t border-slate-200 dark:border-slate-800 shrink-0">
      <div class="text-xs text-center text-slate-400 dark:text-slate-600 truncate">
        <span v-if="!collapsed">EMS v1.0</span>
      </div>
    </div>
  </aside>
</template>
