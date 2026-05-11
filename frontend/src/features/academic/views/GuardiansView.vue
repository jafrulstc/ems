<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import PageHeader from '@/components/shared/PageHeader.vue';
import EmptyState from '@/components/shared/EmptyState.vue';
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
  } catch (e) { console.error(e); } finally { loading.value = false; }
};

onMounted(() => {
  const qStudentId = route.query.student_id;
  if (qStudentId) { studentId.value = Number(qStudentId); fetchGuardians(); }
});

const openNew = () => { if (!studentId.value) return; editingGuardian.value = null; dialogVisible.value = true; };
const edit = (data: Guardian) => { editingGuardian.value = data; dialogVisible.value = true; };
</script>

<template>
  <div>
    <PageHeader title="Guardians" subtitle="Manage student parents and guardians" icon="pi pi-user-minus">
      <template #actions>
        <Button v-if="canCreate && studentId" label="Add Guardian" icon="pi pi-plus" @click="openNew" />
      </template>
    </PageHeader>

    <EmptyState v-if="!studentId" icon="pi pi-users" title="Select a student" description="Choose a student to view their guardians" />

    <div v-else class="ems-card">
      <DataTable v-if="guardians.length" :value="guardians" :loading="loading" stripedRows responsiveLayout="scroll">
        <Column field="name" header="Name" sortable />
        <Column field="relation" header="Relation" />
        <Column field="phone" header="Phone">
          <template #body="{ data }">{{ data.phone ?? '—' }}</template>
        </Column>
        <Column field="email" header="Email">
          <template #body="{ data }">{{ data.email ?? '—' }}</template>
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
      <EmptyState v-else icon="pi pi-user-minus" title="No guardians found" description="Add a guardian for this student" />
    </div>

    <GuardianFormDialog v-model:visible="dialogVisible" :student-id="studentId" :edit-data="editingGuardian" @saved="fetchGuardians" />
  </div>
</template>
