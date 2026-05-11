<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import { studentApi } from '../api/student.api';
import type { Guardian } from '../types/student.types';
import GuardianFormDialog from '../components/GuardianFormDialog.vue';
import { usePermission } from '@/features/auth/composables/usePermission';

const route = useRoute();
const { hasPermission } = usePermission();
const canEdit = hasPermission('academic.guardians.edit');
const canCreate = hasPermission('academic.guardians.create');

const guardians = ref<Guardian[]>([]);
const loading = ref(false);
const studentId = ref<number | null>(null);

const dialogVisible = ref(false);
const editingGuardian = ref<Guardian | null>(null);

const fetchGuardians = async () => {
  if (!studentId.value) return;
  loading.value = true;
  try {
    const res = await studentApi.getStudentGuardians(studentId.value);
    guardians.value = res.data.data ?? [];
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  // Student ID can come from query param or be selected
  const qStudentId = route.query.student_id;
  if (qStudentId) {
    studentId.value = Number(qStudentId);
    fetchGuardians();
  }
});

const openNew = () => {
  if (!studentId.value) return;
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
      <Button v-if="canCreate && studentId" label="Add Guardian" icon="pi pi-plus" @click="openNew" />
    </div>

    <div v-if="!studentId" class="p-4 bg-surface-100 dark:bg-surface-800 rounded-lg text-center">
      <p class="text-surface-500">Select a student to view their guardians.</p>
    </div>

    <div v-else class="card bg-surface-0 dark:bg-surface-900 p-4 rounded-xl shadow-sm border border-surface-200 dark:border-surface-800">
      <DataTable :value="guardians" :loading="loading" stripedRows responsiveLayout="scroll">
        <template #empty>
          <div class="text-center p-4">No guardians found.</div>
        </template>
        
        <Column field="name" header="Name" sortable></Column>
        <Column field="relation" header="Relation"></Column>
        <Column field="phone" header="Phone">
          <template #body="{ data }">
            {{ data.phone ?? '—' }}
          </template>
        </Column>
        <Column field="email" header="Email">
          <template #body="{ data }">
            {{ data.email ?? '—' }}
          </template>
        </Column>
        
        <Column header="Primary" style="width: 10%">
          <template #body="{ data }">
            <span v-if="data.is_primary" class="text-green-600 font-semibold">Yes</span>
            <span v-else class="text-surface-400">No</span>
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
      :student-id="studentId"
      :edit-data="editingGuardian"
      @saved="fetchGuardians"
    />
  </div>
</template>
