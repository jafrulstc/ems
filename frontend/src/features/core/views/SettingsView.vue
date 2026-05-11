<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Tag from 'primevue/tag';
import PageHeader from '@/components/shared/PageHeader.vue';
import EmptyState from '@/components/shared/EmptyState.vue';
import { settingsApi } from '../api/settings.api';
import type { AppSetting } from '../types/settings.types';
import SettingFormDialog from '../components/SettingFormDialog.vue';
import { usePermission } from '@/features/auth/composables/usePermission';

const { hasPermission } = usePermission();
const canEdit = hasPermission('core.settings.edit');
const canCreate = hasPermission('core.settings.create');

const settings = ref<AppSetting[]>([]);
const loading = ref(false);
const searchQuery = ref('');
const dialogVisible = ref(false);
const editingSetting = ref<AppSetting | null>(null);

const filteredSettings = computed(() => {
  if (!searchQuery.value) return settings.value;
  const q = searchQuery.value.toLowerCase();
  return settings.value.filter(s =>
    s.key.toLowerCase().includes(q) ||
    (s.value?.toLowerCase().includes(q)) ||
    (s.group?.toLowerCase().includes(q))
  );
});

const fetchSettings = async () => {
  loading.value = true;
  try {
    const res = await settingsApi.getSettings();
    settings.value = res.data.data ?? [];
  } catch (e) { console.error(e); } finally { loading.value = false; }
};

onMounted(() => fetchSettings());

const openNew = () => { editingSetting.value = null; dialogVisible.value = true; };
const edit = (data: AppSetting) => { editingSetting.value = data; dialogVisible.value = true; };
</script>

<template>
  <div>
    <PageHeader title="Settings" subtitle="Manage application settings" icon="pi pi-cog">
      <template #actions>
        <Button v-if="canCreate" label="Add Setting" icon="pi pi-plus" @click="openNew" />
      </template>
    </PageHeader>

    <div class="card bg-surface-0 dark:bg-surface-900 p-4 rounded-xl shadow-sm border border-surface-200 dark:border-surface-800">
      <div class="mb-4">
        <span class="p-input-icon-left w-full md:w-auto">
          <i class="pi pi-search" />
          <InputText v-model="searchQuery" placeholder="Search settings..." class="w-full md:w-20rem" />
        </span>
      </div>

      <DataTable v-if="filteredSettings.length" :value="filteredSettings" :loading="loading" stripedRows responsiveLayout="scroll">
        <Column field="key" header="Key" sortable></Column>
        <Column field="value" header="Value" sortable>
          <template #body="{ data }">{{ data.value || '—' }}</template>
        </Column>
        <Column field="group" header="Group" sortable>
          <template #body="{ data }">
            <Tag v-if="data.group" :value="data.group" severity="info" />
            <span v-else class="text-surface-400">—</span>
          </template>
        </Column>
        <Column v-if="canEdit" :exportable="false" style="min-width:6rem">
          <template #body="{ data }">
            <Button icon="pi pi-pencil" text rounded severity="success" @click="edit(data)" />
          </template>
        </Column>
      </DataTable>
      <EmptyState v-else icon="pi pi-cog" title="No settings found" description="Create your first setting to get started" />
    </div>

    <SettingFormDialog v-model:visible="dialogVisible" :edit-data="editingSetting" @saved="fetchSettings" />
  </div>
</template>
