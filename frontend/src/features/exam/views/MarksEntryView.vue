<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import Button from 'primevue/button';
import Dropdown from 'primevue/dropdown';
import PageHeader from '@/components/shared/PageHeader.vue';
import { examApi } from '../api/exam.api';
import { academicApi } from '@/features/academic/api/academic.api';
import type { ExamType, Mark } from '../types/exam.types';
import type { AcademicClass, Subject } from '@/features/academic/types/academic.types';
import MarksEntryForm from '../components/MarksEntryForm.vue';
import { usePermission } from '@/features/auth/composables/usePermission';

const { hasPermission } = usePermission();
const canCreate = hasPermission('exam.marks.create');

const examTypes = ref<ExamType[]>([]);
const classes = ref<AcademicClass[]>([]);
const subjects = ref<Subject[]>([]);
const selectedExamType = ref<number | null>(null);
const selectedClass = ref<number | null>(null);
const selectedSubject = ref<number | null>(null);

const existingMarks = ref<Mark[]>([]);
const loadingMarks = ref(false);

const classSubjects = computed(() => {
  // For simplicity, show all subjects; backend filters by class_subject
  return subjects.value;
});

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

const fetchMarks = async () => {
  if (!selectedExamType.value || !selectedSubject.value) return;
  loadingMarks.value = true;
  try {
    const res = await examApi.getMarksBySubject(selectedExamType.value, selectedSubject.value);
    existingMarks.value = res.data.data ?? [];
  } catch (e) {
    console.error(e);
    existingMarks.value = [];
  } finally {
    loadingMarks.value = false;
  }
};

const canShowForm = computed(() => selectedExamType.value !== null && selectedSubject.value !== null);

onMounted(() => fetchDropdowns());
</script>

<template>
  <div>
    <PageHeader title="Marks Entry" subtitle="Enter and manage student marks" icon="pi pi-pencil">
      <template #actions>
        <Button label="Load Marks" icon="pi pi-search" :loading="loadingMarks" :disabled="!canShowForm" @click="fetchMarks" />
      </template>
    </PageHeader>

    <div class="card bg-surface-0 dark:bg-surface-900 p-5 rounded-xl shadow-sm border border-surface-200 dark:border-surface-800 mb-4">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="flex flex-col gap-2">
          <label class="font-medium text-surface-700 dark:text-surface-300">Exam Type *</label>
          <Dropdown v-model="selectedExamType" :options="examTypes" optionLabel="name" optionValue="id" placeholder="Select Exam Type" />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium text-surface-700 dark:text-surface-300">Class</label>
          <Dropdown v-model="selectedClass" :options="classes" optionLabel="name" optionValue="id" placeholder="Select Class" showClear />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium text-surface-700 dark:text-surface-300">Subject *</label>
          <Dropdown v-model="selectedSubject" :options="classSubjects" optionLabel="name" optionValue="id" placeholder="Select Subject" />
        </div>
      </div>
    </div>

    <div v-if="canShowForm && existingMarks.length" class="card bg-surface-0 dark:bg-surface-900 p-5 rounded-xl shadow-sm border border-surface-200 dark:border-surface-800">
      <MarksEntryForm
        :existing-marks="existingMarks"
        :exam-type-id="selectedExamType!"
        :class-subject-id="selectedSubject!"
        @saved="fetchMarks"
      />
    </div>
    <div v-else-if="canShowForm && !loadingMarks" class="text-center p-8 text-surface-400">
      Click "Load Marks" to fetch existing marks for this exam and subject.
    </div>
  </div>
</template>
