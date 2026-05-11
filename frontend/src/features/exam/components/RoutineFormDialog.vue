<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue';
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';
import Dropdown from 'primevue/dropdown';
import Calendar from 'primevue/calendar';
import type { Routine, RoutineCreatePayload, RoutineUpdatePayload } from '../types/exam.types';
import type { ExamType } from '../types/exam.types';
import type { AcademicClass, Subject } from '@/features/academic/types/academic.types';
import type { AcademicYear } from '@/features/core/types/academic-year.types';
import { examApi } from '../api/exam.api';
import { academicApi } from '@/features/academic/api/academic.api';
import { academicYearApi } from '@/features/core/api/academic-year.api';

const props = defineProps<{
  visible: boolean;
  editData?: Routine | null;
}>();

const emit = defineEmits<{
  'update:visible': [val: boolean];
  'saved': [];
}>();

const loading = ref(false);
const errorMsg = ref('');
const examTypes = ref<ExamType[]>([]);
const classes = ref<AcademicClass[]>([]);
const subjects = ref<Subject[]>([]);
const academicYears = ref<AcademicYear[]>([]);

const form = ref({
  exam_type_id: null as number | null,
  class_id: null as number | null,
  subject_id: null as number | null,
  academic_year_id: null as number | null,
  exam_date: null as Date | null,
  start_time: null as Date | null,
  end_time: null as Date | null,
});

onMounted(async () => {
  try {
    const [etRes, clRes, subRes, ayRes] = await Promise.all([
      examApi.getExamTypes(1, 100),
      academicApi.getClasses(1, 100),
      academicApi.getSubjects(1, 100),
      academicYearApi.getAcademicYears(1, 100),
    ]);
    examTypes.value = etRes.data.data?.items ?? [];
    classes.value = clRes.data.data?.items ?? [];
    subjects.value = subRes.data.data?.items ?? [];
    academicYears.value = ayRes.data.data?.items ?? [];
  } catch (e) {
    console.error('Failed to load dropdown data', e);
  }
});

watch(() => props.visible, (val) => {
  if (val) {
    if (props.editData) {
      form.value = {
        exam_type_id: props.editData.exam_type_id,
        class_id: props.editData.class_id,
        subject_id: props.editData.subject_id,
        academic_year_id: props.editData.academic_year_id,
        exam_date: props.editData.exam_date ? new Date(props.editData.exam_date) : null,
        start_time: props.editData.start_time ? new Date(`1970-01-01T${props.editData.start_time}`) : null,
        end_time: props.editData.end_time ? new Date(`1970-01-01T${props.editData.end_time}`) : null,
      };
    } else {
      form.value = { exam_type_id: null, class_id: null, subject_id: null, academic_year_id: null, exam_date: null, start_time: null, end_time: null };
    }
    errorMsg.value = '';
  }
});

const dialogVisible = computed({
  get: () => props.visible,
  set: (val: boolean) => emit('update:visible', val)
});

const formatDate = (d: Date | null) => d ? d.toISOString().split('T')[0] : null;
const formatTime = (d: Date | null) => d ? d.toTimeString().slice(0, 5) : null;

const save = async () => {
  if (!form.value.exam_type_id || !form.value.class_id || !form.value.subject_id || !form.value.academic_year_id) {
    errorMsg.value = 'Please fill all required fields';
    return;
  }
  loading.value = true;
  errorMsg.value = '';
  try {
    if (props.editData) {
      const payload: RoutineUpdatePayload = {
        exam_date: formatDate(form.value.exam_date),
        start_time: formatTime(form.value.start_time),
        end_time: formatTime(form.value.end_time),
      };
      await examApi.updateRoutine(props.editData.id, payload);
    } else {
      const payload: RoutineCreatePayload = {
        exam_type_id: form.value.exam_type_id,
        class_id: form.value.class_id,
        subject_id: form.value.subject_id,
        academic_year_id: form.value.academic_year_id,
        exam_date: formatDate(form.value.exam_date),
        start_time: formatTime(form.value.start_time),
        end_time: formatTime(form.value.end_time),
      };
      await examApi.createRoutine(payload);
    }
    emit('saved');
    dialogVisible.value = false;
  } catch (err: any) {
    errorMsg.value = err.response?.data?.message || 'Failed to save routine';
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <Dialog v-model:visible="dialogVisible" modal :header="editData ? 'Edit Routine' : 'Create Routine'" :style="{ width: '32rem' }">
    <div v-if="errorMsg" class="ems-error">{{ errorMsg }}</div>
    <div class="flex flex-col gap-4">
      <div class="grid grid-cols-2 gap-4">
        <div class="ems-field">
          <label>Exam Type *</label>
          <Dropdown v-model="form.exam_type_id" :options="examTypes" optionLabel="name" optionValue="id" placeholder="Select" :disabled="!!editData" />
        </div>
        <div class="ems-field">
          <label>Academic Year *</label>
          <Dropdown v-model="form.academic_year_id" :options="academicYears" optionLabel="name" optionValue="id" placeholder="Select" :disabled="!!editData" />
        </div>
      </div>
      <div class="grid grid-cols-2 gap-4">
        <div class="ems-field">
          <label>Class *</label>
          <Dropdown v-model="form.class_id" :options="classes" optionLabel="name" optionValue="id" placeholder="Select" :disabled="!!editData" />
        </div>
        <div class="ems-field">
          <label>Subject *</label>
          <Dropdown v-model="form.subject_id" :options="subjects" optionLabel="name" optionValue="id" placeholder="Select" :disabled="!!editData" />
        </div>
      </div>
      <div class="ems-field">
        <label>Exam Date</label>
        <Calendar v-model="form.exam_date" dateFormat="yy-mm-dd" showIcon />
      </div>
      <div class="grid grid-cols-2 gap-4">
        <div class="ems-field">
          <label>Start Time</label>
          <Calendar v-model="form.start_time" :timeOnly="true" hourFormat="24" />
        </div>
        <div class="ems-field">
          <label>End Time</label>
          <Calendar v-model="form.end_time" :timeOnly="true" hourFormat="24" />
        </div>
      </div>
    </div>
    <template #footer>
      <Button label="Cancel" text severity="secondary" @click="dialogVisible = false" />
      <Button label="Save" icon="pi pi-check" @click="save" :loading="loading" />
    </template>
  </Dialog>
</template>
