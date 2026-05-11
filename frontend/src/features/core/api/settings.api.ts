import { useApi } from '@/composables/useApi';
import type { APIResponse } from '@/types/api.types';
import type {
  AppSetting, AppSettingCreatePayload, AppSettingUpdatePayload,
} from '../types/settings.types';

export const settingsApi = {
  getSettings() {
    return useApi().get<APIResponse<AppSetting[]>>('/core/settings');
  },

  createSetting(payload: AppSettingCreatePayload) {
    return useApi().post<APIResponse<AppSetting>>('/core/settings', payload);
  },

  updateSetting(key: string, payload: AppSettingUpdatePayload) {
    return useApi().put<APIResponse<AppSetting>>(`/core/settings/${key}`, payload);
  },
};
