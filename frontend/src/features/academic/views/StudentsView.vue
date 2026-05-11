<script setup lang="ts">
import { ref, onMounted } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import PageHeader from '@/components/shared/PageHeader.vue';
import EmptyState from '@/components/shared/EmptyState.vue';
import { studentApi } from '../api/student.api';
import type { Student } from '../types/student.types';
import StudentFormDialog from '../components/StudentFormDialog.vue';
import { usePermission } from '@/features/auth/composables/usePermission';

const { hasPermission } = usePermission();
const canEdit = hasPermission('academic.students.edit');
const canCreate = hasPermission('academic.students.create');

const students = ref<Student[]>([]);
const loading = ref(false);
const searchQuery = ref('');
const dialogVisible = ref(false);
const editingStudent = ref<Student | null>(null);

const fetchStudents = async () => {
  loading.value = true;
  try {
    const res = await studentApi.getStudents(1, 100, searchQuery.value);
    students.value = res.data.data?.items ?? [];
  } catch (e) { console.error(e); } finally { loading.value = false; }
};

onMounted(() => { fetchStudents(); });

let searchTimeout: any = null;
const onSearch = () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => { fetchStudents(); }, 300);
};

const openNew = () => { editingStudent.value = null; dialogVisible.value = true; };
const edit = (data: Student) => { editingStudent.value = data; dialogVisible.value = true; };
</script>

<template>
  <div>
    <PageHeader title="Students" subtitle="Manage student profiles" icon="pi pi-users">
      <template #actions>
        <Button v-if="canCreate" label="Add Student" icon="pi pi-plus" @click="openNew" />
      </template>
    </PageHeader>

    <div class="ems-card">
      <div class="mb-4">
        <span class="p-input-icon-left w-full md:w-auto">
          <i class="pi pi-search" />
          <InputText v-model="searchQuery" placeholder="Search by name or reg no..." @input="onSearch" class="w-full md:w-20rem" />
        </span>
      </div>

      <DataTable v-if="students.length" :value="students" :loading="loading" stripedRows responsiveLayout="scroll">
        <Column field="registration_no" header="Reg. No" sortable style="width: 15%" />
        <Column field="full_name" header="Full Name" sortable />
        <Column field="gender" header="Gender" style="width: 10%">
          <template #body="{ data }">{{ data.gender ?? '—' }}</template>
        </Column>
        <Column v-if="canEdit" :exportable="false" style="min-width:8rem">
          <template #body="slotProps">
            <Button icon="pi pi-pencil" text rounded severity="success" class="mr-2" @click="edit(slotProps.data)" />
          </template>
        </Column>
      </DataTable>
      <EmptyState v-else icon="pi pi-users" title="No students found" description="Add your first student to get started" />
    </div>

    <StudentFormDialog v-model:visible="dialogVisible" :edit-data="editingStudent" @saved="fetchStudents" />
  </div>
</template>
