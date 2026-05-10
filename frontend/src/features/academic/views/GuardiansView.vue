<script setup lang="ts">
import { ref, onMounted } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Tag from 'primevue/tag';
import InputText from 'primevue/inputtext';
import { studentApi } from '../api/student.api';
import type { Guardian } from '../types/student.types';
import GuardianFormDialog from '../components/GuardianFormDialog.vue';
import { usePermission } from '@/features/auth/composables/usePermission';

const { hasPermission } = usePermission();
const canEdit = hasPermission('academic.guardians.edit');
const canCreate = hasPermission('academic.guardians.create');

const guardians = ref<Guardian[]>([]);
const loading = ref(false);
const searchQuery = ref('');

const dialogVisible = ref(false);
const editingGuardian = ref<Guardian | null>(null);

const fetchGuardians = async () => {
  loading.value = true;
  try {
    const res = await studentApi.getGuardians(1, 100, searchQuery.value);
    guardians.value = res.data.data.items;
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchGuardians();
});

let searchTimeout: any = null;
const onSearch = () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    fetchGuardians();
  }, 300);
};

const openNew = () => {
  editingGuardian.value = null;
  dialogVisible.value = true;
};

const edit = (data: Guardian) => {
  editingGuardian.value = data;
  dialogVisible.value = true;
};
</script>

<template>
  <div>
    <div class="flex flex-col md:flex-row md:justify-between items-start md:items-center mb-6 gap-4">
      <div>
        <h1 class="text-2xl font-bold text-surface-900 dark:text-surface-0 m-0">Guardians</h1>
        <p class="text-surface-500 m-0 mt-1">Manage student parents and guardians</p>
      </div>
      <Button v-if="canCreate" label="Add Guardian" icon="pi pi-plus" @click="openNew" />
    </div>

    <div class="card bg-surface-0 dark:bg-surface-900 p-4 rounded-xl shadow-sm border border-surface-200 dark:border-surface-800">
      <div class="mb-4">
        <span class="p-input-icon-left w-full md:w-auto">
          <i class="pi pi-search" />
          <InputText v-model="searchQuery" placeholder="Search by name, phone..." @input="onSearch" class="w-full md:w-20rem" />
        </span>
      </div>

      <DataTable :value="guardians" :loading="loading" stripedRows responsiveLayout="scroll">
        <template #empty>
          <div class="text-center p-4">No guardians found.</div>
        </template>
        
        <Column field="guardian_name" header="Name" sortable></Column>
        <Column field="relation" header="Relation"></Column>
        <Column field="phone" header="Phone"></Column>
        <Column field="email" header="Email"></Column>
        
        <Column header="Status" style="width: 10%">
          <template #body="{ data }">
            <Tag :severity="data.is_active ? 'success' : 'danger'" :value="data.is_active ? 'Active' : 'Inactive'" />
          </template>
        </Column>

        <Column v-if="canEdit" :exportable="false" style="min-width:8rem">
          <template #body="slotProps">
            <Button icon="pi pi-pencil" text rounded severity="success" class="mr-2" @click="edit(slotProps.data)" />
          </template>
        </Column>
      </DataTable>
    </div>

    <GuardianFormDialog 
      v-model:visible="dialogVisible" 
      :edit-data="editingGuardian"
      @saved="fetchGuardians"
    />
  </div>
</template>
