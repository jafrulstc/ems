<script setup lang="ts">
import { ref, onMounted } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Tag from 'primevue/tag';
import { academicApi } from '../api/academic.api';
import type { Subject } from '../types/academic.types';
import SubjectFormDialog from '../components/SubjectFormDialog.vue';
import { usePermission } from '@/features/auth/composables/usePermission';

const { hasPermission } = usePermission();
const canEdit = hasPermission('academic.subjects.edit');
const canCreate = hasPermission('academic.subjects.create');

const subjects = ref<Subject[]>([]);
const loading = ref(false);

const dialogVisible = ref(false);
const editingSubject = ref<Subject | null>(null);

const fetchSubjects = async () => {
  loading.value = true;
  try {
    const res = await academicApi.getSubjects(1, 100);
    subjects.value = res.data.data?.items ?? [];
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchSubjects();
});

const openNew = () => {
  editingSubject.value = null;
  dialogVisible.value = true;
};

const edit = (data: Subject) => {
  editingSubject.value = data;
  dialogVisible.value = true;
};
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold text-surface-900 dark:text-surface-0 m-0">Subjects</h1>
        <p class="text-surface-500 m-0 mt-1">Manage academic subjects</p>
      </div>
      <Button v-if="canCreate" label="Add Subject" icon="pi pi-plus" @click="openNew" />
    </div>

    <div class="card bg-surface-0 dark:bg-surface-900 p-4 rounded-xl shadow-sm border border-surface-200 dark:border-surface-800">
      <DataTable :value="subjects" :loading="loading" stripedRows responsiveLayout="scroll">
        <template #empty>
          <div class="text-center p-4">No subjects found.</div>
        </template>
        
        <Column field="code" header="Code" sortable style="width: 15%">
          <template #body="{ data }">
            {{ data.code ?? '—' }}
          </template>
        </Column>
        <Column field="name" header="Subject Name" sortable></Column>
        
        <Column header="Type" style="width: 15%">
          <template #body="{ data }">
            <Tag :severity="data.is_optional ? 'info' : 'danger'" :value="data.is_optional ? 'Optional' : 'Mandatory'" />
          </template>
        </Column>

        <Column v-if="canEdit" :exportable="false" style="min-width:8rem">
          <template #body="slotProps">
            <Button icon="pi pi-pencil" text rounded severity="success" class="mr-2" @click="edit(slotProps.data)" />
          </template>
        </Column>
      </DataTable>
    </div>

    <SubjectFormDialog 
      v-model:visible="dialogVisible" 
      :edit-data="editingSubject"
      @saved="fetchSubjects"
    />
  </div>
</template>
