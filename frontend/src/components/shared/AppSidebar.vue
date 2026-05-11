<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useMenuStore } from '@/features/core/stores/menu.store';
import { usePermission } from '@/features/auth/composables/usePermission';
import { useUIStore } from '@/stores/ui.store';
import { useRouter, useRoute } from 'vue-router';

const menuStore = useMenuStore();
const { hasPermission, isSuperuser } = usePermission();
const uiStore = useUIStore();
const router = useRouter();
const route = useRoute();

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
    .map(item => {
      const children = item.children ? filterMenu(item.children) : [];
      return { ...item, children };
    });
};

const visibleMenu = computed(() => filterMenu(menuStore.tree));

const isActive = (routeName: string | null) => {
  if (!routeName) return false;
  return route.name === routeName;
};

const navigate = (routeName: string) => {
  router.push({ name: routeName }).catch(() => {});
  uiStore.closeMobileSidebar();
};

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
        <template v-for="item in visibleMenu" :key="item.id">
          <!-- Item with children -->
          <li v-if="item.children?.length">
            <div class="px-3 py-2 text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
              {{ item.label }}
            </div>
            <ul class="space-y-0.5">
              <li v-for="child in item.children" :key="child.id">
                <button
                  @click="child.route_name && navigate(child.route_name)"
                  :class="[
                    'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium cursor-pointer',
                    isActive(child.route_name)
                      ? 'bg-primary-50 dark:bg-primary-950 text-primary-700 dark:text-primary-300'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-slate-200'
                  ]"
                >
                  <i v-if="child.icon" :class="child.icon" class="text-base w-5 text-center" />
                  <span>{{ child.label }}</span>
                </button>
              </li>
            </ul>
          </li>

          <!-- Item without children -->
          <li v-else>
            <button
              @click="item.route_name && navigate(item.route_name)"
              :class="[
                'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium cursor-pointer',
                isActive(item.route_name)
                  ? 'bg-primary-50 dark:bg-primary-950 text-primary-700 dark:text-primary-300'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-slate-200'
              ]"
            >
              <i v-if="item.icon" :class="item.icon" class="text-base w-5 text-center" />
              <span>{{ item.label }}</span>
            </button>
          </li>
        </template>
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
        <template v-for="item in visibleMenu" :key="item.id">
          <li v-if="item.children?.length">
            <div v-if="!collapsed" class="px-3 py-2 text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
              {{ item.label }}
            </div>
            <div v-else class="my-2 mx-2 border-t border-slate-200 dark:border-slate-700" />
            <ul class="space-y-0.5">
              <li v-for="child in item.children" :key="child.id">
                <button
                  @click="child.route_name && navigate(child.route_name)"
                  :class="[
                    'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium cursor-pointer',
                    isActive(child.route_name)
                      ? 'bg-primary-50 dark:bg-primary-950 text-primary-700 dark:text-primary-300'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-slate-200'
                  ]"
                  :title="collapsed ? child.label : undefined"
                >
                  <i v-if="child.icon" :class="child.icon" class="text-base w-5 text-center shrink-0" />
                  <span v-if="!collapsed" class="truncate">{{ child.label }}</span>
                </button>
              </li>
            </ul>
          </li>

          <li v-else>
            <button
              @click="item.route_name && navigate(item.route_name)"
              :class="[
                'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium cursor-pointer',
                isActive(item.route_name)
                  ? 'bg-primary-50 dark:bg-primary-950 text-primary-700 dark:text-primary-300'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-slate-200'
              ]"
              :title="collapsed ? item.label : undefined"
            >
              <i v-if="item.icon" :class="item.icon" class="text-base w-5 text-center shrink-0" />
              <span v-if="!collapsed" class="truncate">{{ item.label }}</span>
            </button>
          </li>
        </template>
      </ul>
    </nav>
  </aside>
</template>
