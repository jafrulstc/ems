export interface AppSetting {
  id: number;
  organization_id: number;
  key: string;
  value: string | null;
  group: string | null;
}

export interface AppSettingCreatePayload {
  key: string;
  value?: string;
  group?: string;
}

export interface AppSettingUpdatePayload {
  value?: string;
  group?: string;
}
