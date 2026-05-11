<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Checkbox from 'primevue/checkbox';
import Dropdown from 'primevue/dropdown';
import Button from 'primevue/button';
import type { User, UserCreatePayload, UserUpdatePayload } from '../types/user.types';
import type { RoleWithPermissions } from '../types/role.types';
import { userApi } from '../api/user.api';
import { roleApi } from '../api/role.api';

const props = defineProps<{
  visible: boolean;
  editData?: User | null;
}>();

const emit = defineEmits<{
  'update:visible': [val: boolean];
  'saved': [];
}>();

const loading = ref(false);
const errorMsg = ref('');
const roles = ref<RoleWithPermissions[]>([]);

const form = ref({
  email: '',
  password: '',
  username: '',
  full_name: '',
  is_active: true,
  is_superuser: false,
  role_ids: [] as number[],
});

onMounted(async () => {
  try {
    const res = await roleApi.getRoles();
    roles.value = res.data.data ?? [];
  } catch (e) { console.error(e); }
});

watch(() => props.visible, (val) => {
  if (val) {
    if (props.editData) {
      form.value = {
        email: props.editData.email,
        password: '',
        username: props.editData.username ?? '',
        full_name: props.editData.full_name ?? '',
        is_active: props.editData.is_active,
        is_superuser: props.editData.is_superuser,
        role_ids: props.editData.roles.map(r => r.id),
      };
    } else {
      form.value = { email: '', password: '', username: '', full_name: '', is_active: true, is_superuser: false, role_ids: [] };
    }
    errorMsg.value = '';
  }
});

const roleOptions = ref<{ label: string; value: number }[]>([]);
watch(roles, (val) => {
  roleOptions.value = val.map(r => ({ label: r.name, value: r.id }));
}, { immediate: true });

const dialogVisible = computed({
  get: () => props.visible,
  set: (val: boolean) => emit('update:visible', val)
});

const save = async () => {
  loading.value = true;
  errorMsg.value = '';
  try {
    if (props.editData) {
      const payload: UserUpdatePayload = {
        username: form.value.username || null,
        full_name: form.value.full_name || null,
        is_active: form.value.is_active,
        password: form.value.password || null,
      };
      await userApi.updateUser(props.editData.id, payload);
      if (form.value.role_ids.length > 0 || props.editData.roles.length > 0) {
        await userApi.setRoles(props.editData.id, form.value.role_ids);
      }
    } else {
      if (!form.value.email || !form.value.password) {
        errorMsg.value = 'Email and password are required';
        loading.value = false;
        return;
      }
      const payload: UserCreatePayload = {
        email: form.value.email,
        password: form.value.password,
        username: form.value.username || undefined,
        full_name: form.value.full_name || undefined,
        is_active: form.value.is_active,
        is_superuser: form.value.is_superuser,
      };
      const res = await userApi.createUser(payload);
      const userId = res.data.data?.id;
      if (userId && form.value.role_ids.length > 0) {
        await userApi.setRoles(userId, form.value.role_ids);
      }
    }
    emit('saved');
    dialogVisible.value = false;
  } catch (err: any) {
    errorMsg.value = err.response?.data?.message || 'Failed to save user';
  } finally { loading.value = false; }
};
</script>

<template>
  <Dialog v-model:visible="dialogVisible" modal :header="editData ? 'Edit User' : 'Create User'" :style="{ width: '32rem' }">
    <div v-if="errorMsg" class="ems-error">{{ errorMsg }}</div>
    <div class="flex flex-col gap-4">
      <div class="ems-field">
        <label>Email *</label>
        <InputText v-model="form.email" :disabled="!!editData" autofocus />
      </div>
      <div class="ems-field">
        <label>{{ editData ? 'New Password' : 'Password *' }}</label>
        <Password v-model="form.password" :feedback="!editData" toggleMask :placeholder="editData ? 'Leave blank to keep' : ''" />
      </div>
      <div class="grid grid-cols-2 gap-4">
        <div class="ems-field">
          <label>Username</label>
          <InputText v-model="form.username" />
        </div>
        <div class="ems-field">
          <label>Full Name</label>
          <InputText v-model="form.full_name" />
        </div>
      </div>
      <div class="ems-field">
        <label>Roles</label>
        <Dropdown v-model="form.role_ids" :options="roleOptions" optionLabel="label" optionValue="value" multiple placeholder="Select roles" showClear />
      </div>
      <div class="flex items-center gap-6">
        <div class="flex items-center gap-2">
          <Checkbox v-model="form.is_active" :binary="true" inputId="u_active" />
          <label for="u_active" class="text-surface-700 dark:text-surface-300">Active</label>
        </div>
        <div class="flex items-center gap-2">
          <Checkbox v-model="form.is_superuser" :binary="true" inputId="u_superuser" />
          <label for="u_superuser" class="text-surface-700 dark:text-surface-300">Superuser</label>
        </div>
      </div>
    </div>
    <template #footer>
      <Button label="Cancel" text severity="secondary" @click="dialogVisible = false" />
      <Button label="Save" icon="pi pi-check" @click="save" :loading="loading" />
    </template>
  </Dialog>
</template>
