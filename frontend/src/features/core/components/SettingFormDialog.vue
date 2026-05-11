<script setup lang="ts">
import { ref, watch } from 'vue';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import type { AppSetting, AppSettingCreatePayload, AppSettingUpdatePayload } from '../types/settings.types';
import { settingsApi } from '../api/settings.api';

const props = defineProps<{
  visible: boolean;
  editData?: AppSetting | null;
}>();

const emit = defineEmits<{
  'update:visible': [val: boolean];
  'saved': [];
}>();

const loading = ref(false);
const errorMsg = ref('');

const form = ref({
  key: '',
  value: '',
  group: '',
});

watch(() => props.visible, (val) => {
  if (val) {
    if (props.editData) {
      form.value = {
        key: props.editData.key,
        value: props.editData.value ?? '',
        group: props.editData.group ?? '',
      };
    } else {
      form.value = { key: '', value: '', group: '' };
    }
    errorMsg.value = '';
  }
});

const close = () => emit('update:visible', false);

const save = async () => {
  if (!form.value.key) {
    errorMsg.value = 'Setting key is required';
    return;
  }
  loading.value = true;
  errorMsg.value = '';
  try {
    if (props.editData) {
      const payload: AppSettingUpdatePayload = {
        value: form.value.value,
        group: form.value.group || undefined,
      };
      await settingsApi.updateSetting(props.editData.key, payload);
    } else {
      const payload: AppSettingCreatePayload = {
        key: form.value.key,
        value: form.value.value || undefined,
        group: form.value.group || undefined,
      };
      await settingsApi.createSetting(payload);
    }
    emit('saved');
    close();
  } catch (err: any) {
    errorMsg.value = err.response?.data?.message || 'Failed to save setting';
  } finally { loading.value = false; }
};
</script>

<template>
  <Dialog :visible="visible" @update:visible="close" modal :header="editData ? 'Edit Setting' : 'Create Setting'" :style="{ width: '28rem' }">
    <div v-if="errorMsg" class="p-3 bg-red-50 dark:bg-red-950 text-red-600 dark:text-red-400 rounded-lg text-sm mb-4">
      {{ errorMsg }}
    </div>
    <div class="flex flex-col gap-4">
      <div class="flex flex-col gap-2">
        <label class="font-medium text-surface-700 dark:text-surface-300">Key *</label>
        <InputText v-model="form.key" :disabled="!!editData" autofocus />
      </div>
      <div class="flex flex-col gap-2">
        <label class="font-medium text-surface-700 dark:text-surface-300">Value</label>
        <InputText v-model="form.value" />
      </div>
      <div class="flex flex-col gap-2">
        <label class="font-medium text-surface-700 dark:text-surface-300">Group</label>
        <InputText v-model="form.group" placeholder="e.g. general, email" />
      </div>
    </div>
    <template #footer>
      <Button label="Cancel" text severity="secondary" @click="close" />
      <Button label="Save" icon="pi pi-check" @click="save" :loading="loading" />
    </template>
  </Dialog>
</template>
