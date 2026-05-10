<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useMenuStore } from '@/features/core/stores/menu.store';
import { usePermission } from '@/features/auth/composables/usePermission';
import { useRouter, useRoute } from 'vue-router';

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

const navigate = (routeName: string | null) => {
  if (routeName) {
    router.push({ name: routeName }).catch(() => {});
  }
};
</script>

<template>
  <aside class="w-64 bg-surface-0 dark:bg-surface-900 border-r border-surface-200 dark:border-surface-800 flex flex-col transition-colors duration-200 shrink-0 h-full overflow-y-auto">
    <div v-if="menuStore.loading" class="p-4 text-surface-500">
      Loading menu...
    </div>
    <ul v-else class="list-none p-4 m-0 flex flex-col gap-2">
      <template v-for="item in visibleMenu" :key="item.id">
        <li>
          <!-- Top level item (Group) -->
          <div 
            v-if="item.children && item.children.length > 0"
            class="text-sm font-semibold text-surface-500 uppercase tracking-wider mb-2 mt-4 select-none"
          >
            <i v-if="item.icon" :class="item.icon" class="mr-2"></i>
            {{ item.label }}
          </div>
          
          <!-- Leaf item if top level has no children but is a link -->
          <button 
            v-else
            @click="navigate(item.route_name)"
            class="w-full flex items-center p-3 rounded-lg cursor-pointer transition-colors hover:bg-surface-100 dark:hover:bg-surface-800 text-surface-700 dark:text-surface-100 font-medium border-none bg-transparent text-left"
            :class="{ 'bg-primary-50 dark:bg-primary-900/40 text-primary-600 dark:text-primary-400': route.name === item.route_name }"
          >
            <i v-if="item.icon" :class="item.icon" class="mr-3 text-lg"></i>
            {{ item.label }}
          </button>

          <!-- Children -->
          <ul v-if="item.children && item.children.length > 0" class="list-none p-0 m-0 flex flex-col gap-1">
            <li v-for="child in item.children" :key="child.id">
              <button 
                @click="navigate(child.route_name)"
                class="w-full flex items-center p-2 pl-4 rounded-lg cursor-pointer transition-colors hover:bg-surface-100 dark:hover:bg-surface-800 text-surface-600 dark:text-surface-300 border-none bg-transparent text-left"
                :class="{ 'bg-primary-50 dark:bg-primary-900/40 text-primary-600 dark:text-primary-400 font-medium': route.name === child.route_name }"
              >
                <i v-if="child.icon" :class="child.icon" class="mr-3"></i>
                <span v-else class="w-2 h-2 rounded-full bg-surface-300 dark:bg-surface-600 mr-4"></span>
                {{ child.label }}
              </button>
            </li>
          </ul>
        </li>
      </template>
    </ul>
  </aside>
</template>
