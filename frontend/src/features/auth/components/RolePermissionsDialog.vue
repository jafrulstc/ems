<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import Dialog from 'primevue/dialog';
import Checkbox from 'primevue/checkbox';
import Button from 'primevue/button';
import type { RoleWithPermissions, PermissionRead } from '../types/role.types';
import { roleApi, permissionApi } from '../api/role.api';

const props = defineProps<{
  visible: boolean;
  role: RoleWithPermissions | null;
}>();

const emit = defineEmits<{
  'update:visible': [val: boolean];
  'saved': [];
}>();

const loading = ref(false);
const saving = ref(false);
const errorMsg = ref('');
const allPermissions = ref<PermissionRead[]>([]);
const selectedKeys = ref<string[]>([]);

const permissionsByModule = computed(() => {
  const map: Record<string, PermissionRead[]> = {};
  for (const p of allPermissions.value) {
    const mod = p.module;
    if (!map[mod]) map[mod] = [];
    map[mod].push(p);
  }
  return map;
});

watch(() => props.visible, async (val) => {
  if (!val || !props.role) return;
  errorMsg.value = '';
  loading.value = true;
  try {
    const res = await permissionApi.getPermissions();
    allPermissions.value = res.data.data ?? [];
    selectedKeys.value = props.role.permissions.map(p => p.key);
  } catch (e) { console.error(e); } finally { loading.value = false; }
});

const close = () => emit('update:visible', false);

const toggleAll = (module: string, perms: PermissionRead[]) => {
  const keys = perms.map(p => p.key);
  const allSelected = keys.every(k => selectedKeys.value.includes(k));
  if (allSelected) {
    selectedKeys.value = selectedKeys.value.filter(k => !keys.includes(k));
  } else {
    const newKeys = keys.filter(k => !selectedKeys.value.includes(k));
    selectedKeys.value = [...selectedKeys.value, ...newKeys];
  }
};

const save = async () => {
  if (!props.role) return;
  saving.value = true;
  errorMsg.value = '';
  try {
    await roleApi.assignPermissions(props.role.id, selectedKeys.value);
    emit('saved');
    close();
  } catch (err: any) {
    errorMsg.value = err.response?.data?.message || 'Failed to assign permissions';
  } finally { saving.value = false; }
};
</script>

<template>
  <Dialog :visible="visible" @update:visible="close" modal :header="`Permissions — ${role?.name ?? ''}`" :style="{ width: '42rem' }">
    <div v-if="errorMsg" class="p-3 bg-red-50 dark:bg-red-950 text-red-600 dark:text-red-400 rounded-lg text-sm mb-4">
      {{ errorMsg }}
    </div>
    <div v-if="loading" class="text-center py-8 text-surface-500">Loading permissions...</div>
    <div v-else class="max-h-96 overflow-y-auto flex flex-col gap-6">
      <div v-for="(perms, module) in permissionsByModule" :key="module">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-sm font-semibold text-primary-700 dark:text-primary-300 uppercase tracking-wider">
            {{ (module as string) }}
          </h3>
          <Button
            :label="perms.every(p => selectedKeys.includes(p.key)) ? 'Deselect All' : 'Select All'"
            text size="small" severity="info"
            @click="toggleAll(module as string, perms)"
          />
        </div>
        <div class="flex flex-col gap-1.5">
          <div v-for="p in perms" :key="p.key" class="flex items-center gap-3 py-1.5 px-3 rounded-lg bg-surface-50 dark:bg-surface-800">
            <Checkbox v-model="selectedKeys" :value="p.key" :inputId="`p_${p.key}`" />
            <label :for="`p_${p.key}`" class="text-sm text-surface-800 dark:text-surface-200 flex-1 cursor-pointer">{{ p.label }}</label>
            <span class="text-xs text-surface-400">{{ p.key }}</span>
          </div>
        </div>
      </div>
    </div>
    <template #footer>
      <Button label="Cancel" text severity="secondary" @click="close" />
      <Button label="Assign" icon="pi pi-check" @click="save" :loading="saving" />
    </template>
  </Dialog>
</template>
