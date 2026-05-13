<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useUIStore } from '@/stores/ui.store';

const props = defineProps<{
  item: any;
  collapsed?: boolean;
}>();

const router = useRouter();
const route = useRoute();
const uiStore = useUIStore();

const isExpanded = ref(false);

const isActive = (routeName: string | null) => {
  if (!routeName) return false;
  return route.name === routeName;
};

// Auto-expand if a child is active
if (props.item.children?.some((child: any) => isActive(child.route_name))) {
  isExpanded.value = true;
}

const toggle = () => {
  isExpanded.value = !isExpanded.value;
};

const navigate = (routeName: string) => {
  router.push({ name: routeName }).catch(() => {});
  uiStore.closeMobileSidebar();
};
</script>

<template>
  <li v-if="item.children?.length">
    <!-- Group Header -->
    <button
      v-if="!collapsed"
      @click="toggle"
      class="w-full flex items-center justify-between px-3 py-2 text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider hover:bg-slate-50 dark:hover:bg-slate-800/50 rounded-lg transition-colors group"
    >
      <div class="flex items-center gap-3">
        <i v-if="item.icon" :class="item.icon" class="text-sm w-5 text-center" />
        <span>{{ item.label }}</span>
      </div>
      <i 
        :class="[
          'pi pi-chevron-down text-[10px] transition-transform duration-200',
          isExpanded ? 'rotate-180' : ''
        ]" 
      />
    </button>
    <div v-else class="my-2 mx-2 border-t border-slate-200 dark:border-slate-700" />
    
    <!-- Children List -->
    <ul v-show="isExpanded || collapsed" class="space-y-0.5 mt-1">
      <li v-for="child in item.children" :key="child.id">
        <button
          @click="child.route_name && navigate(child.route_name)"
          :class="[
            'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium cursor-pointer transition-colors',
            isActive(child.route_name)
              ? 'bg-primary-50 dark:bg-primary-950/50 text-primary-700 dark:text-primary-300'
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

  <!-- Single Item -->
  <li v-else>
    <button
      @click="item.route_name && navigate(item.route_name)"
      :class="[
        'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium cursor-pointer transition-colors',
        isActive(item.route_name)
          ? 'bg-primary-50 dark:bg-primary-950/50 text-primary-700 dark:text-primary-300'
          : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-slate-200'
      ]"
      :title="collapsed ? item.label : undefined"
    >
      <i v-if="item.icon" :class="item.icon" class="text-base w-5 text-center shrink-0" />
      <span v-if="!collapsed" class="truncate">{{ item.label }}</span>
    </button>
  </li>
</template>
