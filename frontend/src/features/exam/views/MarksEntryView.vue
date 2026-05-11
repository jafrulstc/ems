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
import { useDisplayName } from '@/composables/useDisplayName';

const { hasPermission } = usePermission();
const { displayName } = useDisplayName();
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

const examTypeOptions = computed(() => examTypes.value.map(e => ({ ...e, displayName: displayName(e.name, e.name_bn) })));
const classOptions = computed(() => classes.value.map(c => ({ ...c, displayName: displayName(c.name, c.name_bn) })));
const subjectOptions = computed(() => classSubjects.value.map(s => ({ ...s, displayName: displayName(s.name, s.name_bn) })));

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

    <div class="ems-card mb-4">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="ems-field">
          <label>Exam Type *</label>
          <Dropdown v-model="selectedExamType" :options="examTypeOptions" optionLabel="displayName" optionValue="id" placeholder="Select Exam Type" />
        </div>
        <div class="ems-field">
          <label>Class</label>
          <Dropdown v-model="selectedClass" :options="classOptions" optionLabel="displayName" optionValue="id" placeholder="Select Class" showClear />
        </div>
        <div class="ems-field">
          <label>Subject *</label>
          <Dropdown v-model="selectedSubject" :options="subjectOptions" optionLabel="displayName" optionValue="id" placeholder="Select Subject" />
        </div>
      </div>
    </div>

    <div v-if="canShowForm && existingMarks.length" class="ems-card">
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
