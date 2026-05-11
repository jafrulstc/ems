<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';
import ToggleSwitch from 'primevue/toggleswitch';
import type { User, PermissionOverrideUpsert } from '../types/user.types';
import type { PermissionRead } from '../types/role.types';
import { userApi } from '../api/user.api';
import { permissionApi } from '../api/role.api';

const props = defineProps<{
  visible: boolean;
  user: User | null;
}>();

const emit = defineEmits<{
  'update:visible': [val: boolean];
}>();

const loading = ref(false);
const saving = ref(false);
const errorMsg = ref('');
const allPermissions = ref<PermissionRead[]>([]);
const overrides = ref<Record<string, boolean>>({});

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
  if (!val || !props.user) return;
  errorMsg.value = '';
  loading.value = true;
  try {
    const [permsRes, overridesRes] = await Promise.all([
      permissionApi.getPermissions(),
      userApi.getOverrides(props.user.id),
    ]);
    allPermissions.value = permsRes.data.data ?? [];
    const overrideMap: Record<string, boolean> = {};
    for (const o of (overridesRes.data.data ?? [])) {
      const perm = allPermissions.value.find(p => p.id === o.permission_id);
      if (perm) overrideMap[perm.key] = o.is_granted;
    }
    overrides.value = overrideMap;
  } catch (e) { console.error(e); } finally { loading.value = false; }
});

const close = () => emit('update:visible', false);

const save = async () => {
  if (!props.user) return;
  saving.value = true;
  errorMsg.value = '';
  try {
    const payload: PermissionOverrideUpsert[] = Object.entries(overrides.value).map(
      ([key, is_granted]) => ({ permission_key: key, is_granted })
    );
    await userApi.upsertOverrides(props.user.id, payload);
    close();
  } catch (err: any) {
    errorMsg.value = err.response?.data?.message || 'Failed to save overrides';
  } finally { saving.value = false; }
};
</script>

<template>
  <Dialog :visible="visible" @update:visible="close" modal :header="`Permission Overrides — ${user?.email ?? ''}`" :style="{ width: '42rem' }">
    <div v-if="errorMsg" class="p-3 bg-red-50 dark:bg-red-950 text-red-600 dark:text-red-400 rounded-lg text-sm mb-4">
      {{ errorMsg }}
    </div>
    <div v-if="loading" class="text-center py-8 text-surface-500">Loading permissions...</div>
    <div v-else class="max-h-96 overflow-y-auto flex flex-col gap-6">
      <div v-for="(perms, module) in permissionsByModule" :key="module">
        <h3 class="text-sm font-semibold text-primary-700 dark:text-primary-300 uppercase tracking-wider mb-2">
          {{ (module as string) }}
        </h3>
        <div class="flex flex-col gap-2">
          <div v-for="p in perms" :key="p.key" class="flex items-center justify-between py-1.5 px-3 rounded-lg bg-surface-50 dark:bg-surface-800">
            <div>
              <span class="text-sm font-medium text-surface-800 dark:text-surface-200">{{ p.label }}</span>
              <span class="text-xs text-surface-400 ml-2">{{ p.key }}</span>
            </div>
            <div class="flex items-center gap-2">
              <span :class="['text-xs font-medium', overrides[p.key] ? 'text-green-600' : 'text-red-500']">
                {{ overrides[p.key] ? 'Grant' : (overrides[p.key] === false ? 'Deny' : 'Default' ) }}
              </span>
              <ToggleSwitch v-model="overrides[p.key]" />
            </div>
          </div>
        </div>
      </div>
    </div>
    <template #footer>
      <Button label="Cancel" text severity="secondary" @click="close" />
      <Button label="Save Overrides" icon="pi pi-check" @click="save" :loading="saving" />
    </template>
  </Dialog>
</template>
