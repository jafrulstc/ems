<script setup lang="ts">
import { ref, onMounted } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Tag from 'primevue/tag';
import { academicApi } from '../api/academic.api';
import type { AcademicClass } from '../types/academic.types';
import ClassFormDialog from '../components/ClassFormDialog.vue';
import { usePermission } from '@/features/auth/composables/usePermission';

const { hasPermission } = usePermission();
const canEdit = hasPermission('academic.classes.edit');
const canCreate = hasPermission('academic.classes.create');

const classes = ref<AcademicClass[]>([]);
const loading = ref(false);

const dialogVisible = ref(false);
const editingClass = ref<AcademicClass | null>(null);

const fetchClasses = async () => {
  loading.value = true;
  try {
    const res = await academicApi.getClasses(1, 100); // simplify pagination for now
    classes.value = res.data.data.items;
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchClasses();
});

const openNew = () => {
  editingClass.value = null;
  dialogVisible.value = true;
};

const edit = (data: AcademicClass) => {
  editingClass.value = data;
  dialogVisible.value = true;
};
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold text-surface-900 dark:text-surface-0 m-0">Classes</h1>
        <p class="text-surface-500 m-0 mt-1">Manage academic classes and levels</p>
      </div>
      <Button v-if="canCreate" label="Add Class" icon="pi pi-plus" @click="openNew" />
    </div>

    <div class="card bg-surface-0 dark:bg-surface-900 p-4 rounded-xl shadow-sm border border-surface-200 dark:border-surface-800">
      <DataTable :value="classes" :loading="loading" stripedRows responsiveLayout="scroll">
        <template #empty>
          <div class="text-center p-4">No classes found.</div>
        </template>
        
        <Column field="level" header="Level" sortable style="width: 10%"></Column>
        <Column field="name" header="Name" sortable></Column>
        
        <Column header="Groups" style="width: 15%">
          <template #body="{ data }">
            <Tag :severity="data.has_groups ? 'info' : 'secondary'" :value="data.has_groups ? 'Yes' : 'No'" />
          </template>
        </Column>
        
        <Column header="Status" style="width: 15%">
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

    <ClassFormDialog 
      v-model:visible="dialogVisible" 
      :edit-data="editingClass"
      @saved="fetchClasses"
    />
  </div>
</template>
