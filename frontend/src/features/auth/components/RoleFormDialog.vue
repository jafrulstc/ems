<script setup lang="ts">
import { ref, watch } from 'vue';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import type { RoleWithPermissions, RoleCreatePayload, RoleUpdatePayload } from '../types/role.types';
import { roleApi } from '../api/role.api';

const props = defineProps<{
  visible: boolean;
  editData?: RoleWithPermissions | null;
}>();

const emit = defineEmits<{
  'update:visible': [val: boolean];
  'saved': [];
}>();

const loading = ref(false);
const errorMsg = ref('');

const form = ref({
  name: '',
  description: '',
});

watch(() => props.visible, (val) => {
  if (val) {
    if (props.editData) {
      form.value = { name: props.editData.name, description: props.editData.description ?? '' };
    } else {
      form.value = { name: '', description: '' };
    }
    errorMsg.value = '';
  }
});

const close = () => emit('update:visible', false);

const save = async () => {
  if (!form.value.name) {
    errorMsg.value = 'Role name is required';
    return;
  }
  loading.value = true;
  errorMsg.value = '';
  try {
    if (props.editData) {
      const payload: RoleUpdatePayload = {
        name: form.value.name,
        description: form.value.description || null,
      };
      await roleApi.updateRole(props.editData.id, payload);
    } else {
      const payload: RoleCreatePayload = {
        name: form.value.name,
        description: form.value.description || undefined,
      };
      await roleApi.createRole(payload);
    }
    emit('saved');
    close();
  } catch (err: any) {
    errorMsg.value = err.response?.data?.message || 'Failed to save role';
  } finally { loading.value = false; }
};
</script>

<template>
  <Dialog :visible="visible" @update:visible="close" modal :header="editData ? 'Edit Role' : 'Create Role'" :style="{ width: '28rem' }">
    <div v-if="errorMsg" class="p-3 bg-red-50 dark:bg-red-950 text-red-600 dark:text-red-400 rounded-lg text-sm mb-4">
      {{ errorMsg }}
    </div>
    <div class="flex flex-col gap-4">
      <div class="flex flex-col gap-2">
        <label class="font-medium text-surface-700 dark:text-surface-300">Name *</label>
        <InputText v-model="form.name" autofocus />
      </div>
      <div class="flex flex-col gap-2">
        <label class="font-medium text-surface-700 dark:text-surface-300">Description</label>
        <InputText v-model="form.description" placeholder="Optional description" />
      </div>
    </div>
    <template #footer>
      <Button label="Cancel" text severity="secondary" @click="close" />
      <Button label="Save" icon="pi pi-check" @click="save" :loading="loading" />
    </template>
  </Dialog>
</template>
