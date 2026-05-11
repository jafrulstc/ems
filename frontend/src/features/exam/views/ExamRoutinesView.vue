<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dropdown from 'primevue/dropdown';
import Tag from 'primevue/tag';
import PageHeader from '@/components/shared/PageHeader.vue';
import EmptyState from '@/components/shared/EmptyState.vue';
import { examApi } from '../api/exam.api';
import { academicApi } from '@/features/academic/api/academic.api';
import type { Routine, ExamType } from '../types/exam.types';
import type { AcademicClass, Subject } from '@/features/academic/types/academic.types';
import RoutineFormDialog from '../components/RoutineFormDialog.vue';
import { usePermission } from '@/features/auth/composables/usePermission';

const { hasPermission } = usePermission();
const canEdit = hasPermission('exam.routines.edit');
const canCreate = hasPermission('exam.routines.create');

const routines = ref<Routine[]>([]);
const examTypes = ref<ExamType[]>([]);
const classes = ref<AcademicClass[]>([]);
const subjects = ref<Subject[]>([]);
const selectedExamType = ref<number | null>(null);
const loading = ref(false);
const dialogVisible = ref(false);
const editingItem = ref<Routine | null>(null);

const examTypeMap = computed(() => new Map(examTypes.value.map(e => [e.id, e.name])));
const classMap = computed(() => new Map(classes.value.map(c => [c.id, c.name])));
const subjectMap = computed(() => new Map(subjects.value.map(s => [s.id, s.name])));

const fetchDropdowns = async () => {
  try {
    const [etRes, clRes, subRes] = await Promise.all([
      examApi.getExamTypes(1, 100),
      academicApi.getClasses(1, 100),
      academicApi.getSubjects(1, 100),
    ]);
    examTypes.value = etRes.data.data?.items ?? [];
    classes.value = clRes.data.data?.items ?? [];
    subjects.value = subRes.data.data?.items ?? [];
  } catch (e) { console.error(e); }
};

const fetchRoutines = async () => {
  loading.value = true;
  try {
    if (selectedExamType.value) {
      const res = await examApi.getRoutinesByExam(selectedExamType.value);
      routines.value = res.data.data ?? [];
    } else {
      const res = await examApi.getRoutines(1, 100);
      routines.value = res.data.data?.items ?? [];
    }
  } catch (e) { console.error(e); } finally { loading.value = false; }
};

onMounted(() => { fetchDropdowns(); fetchRoutines(); });

const openNew = () => { editingItem.value = null; dialogVisible.value = true; };
const edit = (data: Routine) => { editingItem.value = data; dialogVisible.value = true; };

const remove = async (id: number) => {
  if (!confirm('Delete this routine?')) return;
  try { await examApi.deleteRoutine(id); fetchRoutines(); } catch (e) { console.error(e); }
};
</script>

<template>
  <div>
    <PageHeader title="Exam Routines" subtitle="Schedule and manage exam routines" icon="pi pi-calendar">
      <template #actions>
        <Button v-if="canCreate" label="Add Routine" icon="pi pi-plus" @click="openNew" />
      </template>
    </PageHeader>

    <div class="card bg-surface-0 dark:bg-surface-900 p-4 rounded-xl shadow-sm border border-surface-200 dark:border-surface-800">
      <div class="mb-4">
        <Dropdown v-model="selectedExamType" :options="examTypes" optionLabel="name" optionValue="id" placeholder="Filter by Exam Type" showClear @change="fetchRoutines" class="w-full md:w-64" />
      </div>

      <DataTable v-if="routines.length" :value="routines" :loading="loading" stripedRows responsiveLayout="scroll">
        <Column header="Exam Type" sortable>
          <template #body="{ data }">{{ examTypeMap.get(data.exam_type_id) ?? data.exam_type_id }}</template>
        </Column>
        <Column header="Class" sortable>
          <template #body="{ data }">{{ classMap.get(data.class_id) ?? data.class_id }}</template>
        </Column>
        <Column header="Subject" sortable>
          <template #body="{ data }">{{ subjectMap.get(data.subject_id) ?? data.subject_id }}</template>
        </Column>
        <Column field="exam_date" header="Date" sortable>
          <template #body="{ data }">{{ data.exam_date || '—' }}</template>
        </Column>
        <Column header="Time">
          <template #body="{ data }">
            <span v-if="data.start_time">{{ data.start_time }} – {{ data.end_time }}</span>
            <span v-else class="text-surface-400">—</span>
          </template>
        </Column>
        <Column v-if="canEdit" :exportable="false" style="min-width:10rem">
          <template #body="{ data }">
            <Button icon="pi pi-pencil" text rounded severity="success" class="mr-1" @click="edit(data)" />
            <Button icon="pi pi-trash" text rounded severity="danger" @click="remove(data.id)" />
          </template>
        </Column>
      </DataTable>
      <EmptyState v-else icon="pi pi-calendar" title="No routines" description="Create exam routines to schedule exams" />
    </div>

    <RoutineFormDialog v-model:visible="dialogVisible" :edit-data="editingItem" @saved="fetchRoutines" />
  </div>
</template>
