import { useApi } from '@/composables/useApi';
import type { MenuItem } from '@/types/core.types';
import type { APIResponse } from '@/types/api.types';

export const menuApi = {
  getTree() {
    return useApi().get<APIResponse<MenuItem[]>>('/core/menus');
  }
};
