<script setup lang="ts">
import { ref, watch, computed } from 'vue';
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

const dialogVisible = computed({
  get: () => props.visible,
  set: (val: boolean) => emit('update:visible', val)
});

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
    dialogVisible.value = false;
  } catch (err: any) {
    errorMsg.value = err.response?.data?.message || 'Failed to save role';
  } finally { loading.value = false; }
};
</script>

<template>
  <Dialog v-model:visible="dialogVisible" modal :header="editData ? 'Edit Role' : 'Create Role'" :style="{ width: '28rem' }">
    <div v-if="errorMsg" class="ems-error">{{ errorMsg }}</div>
    <div class="flex flex-col gap-4">
      <div class="ems-field">
        <label>Name *</label>
        <InputText v-model="form.name" autofocus />
      </div>
      <div class="ems-field">
        <label>Description</label>
        <InputText v-model="form.description" placeholder="Optional description" />
      </div>
    </div>
    <template #footer>
      <Button label="Cancel" text severity="secondary" @click="dialogVisible = false" />
      <Button label="Save" icon="pi pi-check" @click="save" :loading="loading" />
    </template>
  </Dialog>
</template>
