<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dropdown from 'primevue/dropdown';
import Tag from 'primevue/tag';
import Dialog from 'primevue/dialog';
import InputNumber from 'primevue/inputnumber';
import PageHeader from '@/components/shared/PageHeader.vue';
import EmptyState from '@/components/shared/EmptyState.vue';
import { examApi } from '../api/exam.api';
import type { ExamType, Result, ResultGeneratePayload, GradingSystem } from '../types/exam.types';
import { usePermission } from '@/features/auth/composables/usePermission';

const { hasPermission } = usePermission();
const canView = hasPermission('exam.results.view');
const canCreate = hasPermission('exam.results.create');

const results = ref<Result[]>([]);
const examTypes = ref<ExamType[]>([]);
const gradingSystems = ref<GradingSystem[]>([]);
const selectedExamType = ref<number | null>(null);
const loading = ref(false);
const generateDialogVisible = ref(false);
const generateLoading = ref(false);
const generateError = ref('');
const generateForm = ref<ResultGeneratePayload>({ exam_type_id: null, grading_system_id: null });

const examTypeMap = computed(() => new Map(examTypes.value.map(e => [e.id, e.name])));

const fetchExamTypes = async () => {
  try {
    const res = await examApi.getExamTypes(1, 100);
    examTypes.value = res.data.data?.items ?? [];
  } catch (e) { console.error(e); }
};

const fetchGradingSystems = async () => {
  try {
    const res = await examApi.getGradingSystems(1, 100);
    gradingSystems.value = res.data.data?.items ?? [];
  } catch (e) { console.error(e); }
};

const fetchResults = async () => {
  if (!selectedExamType.value) return;
  loading.value = true;
  try {
    const res = await examApi.getResults(selectedExamType.value);
    results.value = res.data.data ?? [];
  } catch (e) { console.error(e); } finally { loading.value = false; }
};

onMounted(() => { fetchExamTypes(); fetchGradingSystems(); });

const openGenerate = () => {
  generateForm.value = { exam_type_id: selectedExamType.value, grading_system_id: null };
  generateError.value = '';
  generateDialogVisible.value = true;
};

const generateResults = async () => {
  if (!generateForm.value.exam_type_id) return;
  generateLoading.value = true;
  generateError.value = '';
  try {
    await examApi.generateResults(generateForm.value);
    generateDialogVisible.value = false;
    if (selectedExamType.value) fetchResults();
  } catch (err: any) {
    generateError.value = err.response?.data?.message || 'Failed to generate results';
  } finally { generateLoading.value = false; }
};
</script>

<template>
  <div>
    <PageHeader title="Results" subtitle="View and generate exam results" icon="pi pi-chart-bar">
      <template #actions>
        <Button label="View Results" icon="pi pi-search" :disabled="!selectedExamType" @click="fetchResults" class="mr-2" />
        <Button v-if="canCreate" label="Generate Results" icon="pi pi-cog" severity="success" @click="openGenerate" />
      </template>
    </PageHeader>

    <div class="card bg-surface-0 dark:bg-surface-900 p-5 rounded-xl shadow-sm border border-surface-200 dark:border-surface-800 mb-4">
      <div class="w-full md:w-64">
        <label class="font-medium text-surface-700 dark:text-surface-300 mb-2 block">Select Exam Type</label>
        <Dropdown v-model="selectedExamType" :options="examTypes" optionLabel="name" optionValue="id" placeholder="Choose Exam Type" class="w-full" />
      </div>
    </div>

    <div class="card bg-surface-0 dark:bg-surface-900 p-4 rounded-xl shadow-sm border border-surface-200 dark:border-surface-800">
      <DataTable v-if="results.length" :value="results" :loading="loading" stripedRows responsiveLayout="scroll">
        <Column field="enrollment_id" header="Enrollment" sortable></Column>
        <Column header="Exam Type">
          <template #body="{ data }">{{ examTypeMap.get(data.exam_type_id) ?? data.exam_type_id }}</template>
        </Column>
        <Column field="total_obtained_marks" header="Obtained" sortable></Column>
        <Column field="total_full_marks" header="Full Marks" sortable></Column>
        <Column field="percentage" header="%" sortable>
          <template #body="{ data }">{{ data.percentage.toFixed(1) }}%</template>
        </Column>
        <Column field="grade" header="Grade" sortable>
          <template #body="{ data }">
            <Tag :severity="data.is_pass ? 'success' : 'danger'" :value="data.grade" />
          </template>
        </Column>
        <Column field="grade_point" header="Point" sortable></Column>
        <Column header="Status">
          <template #body="{ data }">
            <Tag :severity="data.is_pass ? 'success' : 'danger'" :value="data.is_pass ? 'Pass' : 'Fail'" />
          </template>
        </Column>
      </DataTable>
      <EmptyState v-else icon="pi pi-chart-bar" title="No results" description="Select an exam type and click View Results" />
    </div>

    <!-- Generate Dialog -->
    <Dialog v-model:visible="generateDialogVisible" modal header="Generate Results" :style="{ width: '28rem' }">
      <div v-if="generateError" class="p-3 bg-red-50 dark:bg-red-950 text-red-600 dark:text-red-400 rounded-lg text-sm mb-4">
        {{ generateError }}
      </div>
      <div class="flex flex-col gap-4">
        <div class="flex flex-col gap-2">
          <label class="font-medium text-surface-700 dark:text-surface-300">Exam Type *</label>
          <Dropdown v-model="generateForm.exam_type_id" :options="examTypes" optionLabel="name" optionValue="id" placeholder="Select" />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium text-surface-700 dark:text-surface-300">Grading System</label>
          <Dropdown v-model="generateForm.grading_system_id" :options="gradingSystems" optionLabel="name" optionValue="id" placeholder="Default" showClear />
        </div>
        <p class="text-xs text-surface-500">Leave enrollment IDs empty to generate for all students.</p>
      </div>
      <template #footer>
        <Button label="Cancel" text severity="secondary" @click="generateDialogVisible = false" />
        <Button label="Generate" icon="pi pi-cog" @click="generateResults" :loading="generateLoading" />
      </template>
    </Dialog>
  </div>
</template>
