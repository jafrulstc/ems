<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useMenuStore } from '@/features/core/stores/menu.store';
import { usePermission } from '@/features/auth/composables/usePermission';
import { useRouter, useRoute } from 'vue-router';
import PanelMenu from 'primevue/panelmenu';

const menuStore = useMenuStore();
const { hasPermission, isSuperuser } = usePermission();
const router = useRouter();
const route = useRoute();

onMounted(() => {
  if (menuStore.tree.length === 0) {
    menuStore.fetchMenuTree();
  }
});

// Filter menu items recursively based on permissions
const filterMenu = (items: any[]): any[] => {
  return items
    .filter(item => item.is_active)
    .filter(item => {
      // If superuser or no permission required, allow
      if (isSuperuser.value || !item.permission_key) return true;
      return hasPermission(item.permission_key).value;
    })
    .map(item => {
      const children = item.children ? filterMenu(item.children) : [];
      return { ...item, children };
    });
};

const visibleMenu = computed(() => filterMenu(menuStore.tree));

// Map the visible backend menu to PrimeVue's PanelMenu structure
const mapToPanelMenu = (items: any[]): any[] => {
  return items.map(item => {
    const transformed: any = {
      label: item.label,
      icon: item.icon,
    };
    
    if (item.route_name) {
      transformed.command = () => {
        router.push({ name: item.route_name }).catch(() => {});
      };
    }
    
    if (item.children && item.children.length > 0) {
      transformed.items = mapToPanelMenu(item.children);
    }
    
    return transformed;
  });
};

const panelMenuModel = computed(() => mapToPanelMenu(visibleMenu.value));
</script>

<template>
  <aside class="w-64 bg-surface-0 dark:bg-surface-900 border-r border-surface-200 dark:border-surface-800 flex flex-col transition-colors duration-200 shrink-0 h-full overflow-y-auto">
    <div v-if="menuStore.loading" class="p-4 text-surface-500">
      Loading menu...
    </div>
    <div v-else class="p-3">
      <PanelMenu :model="panelMenuModel" class="w-full" />
    </div>
  </aside>
</template>
