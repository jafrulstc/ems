import { defineStore } from 'pinia';
import { ref } from 'vue';
import { menuApi } from '@/features/core/api/menu.api';
import type { MenuItem } from '@/types/core.types';

export const useMenuStore = defineStore('menu', () => {
  const tree = ref<MenuItem[]>([]);
  const loading = ref(false);

  const fetchMenuTree = async () => {
    loading.value = true;
    try {
      const res = await menuApi.getTree();
      tree.value = res.data.data ?? [];
    } catch (e) {
      tree.value = [];
    } finally {
      loading.value = false;
    }
  };

  return {
    tree,
    loading,
    fetchMenuTree
  };
});
