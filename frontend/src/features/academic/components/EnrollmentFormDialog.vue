<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Checkbox from 'primevue/checkbox';
import Button from 'primevue/button';
import Dropdown from 'primevue/dropdown';
import type { Enrollment, EnrollmentCreatePayload, EnrollmentUpdatePayload } from '../types/enrollment.types';
import type { Student } from '../types/student.types';
import type { AcademicClass, Section } from '../types/academic.types';
import type { AcademicYear } from '@/features/core/types/academic-year.types';
import { enrollmentApi } from '../api/enrollment.api';
import { studentApi } from '../api/student.api';
import { academicApi } from '../api/academic.api';
import { academicYearApi } from '@/features/core/api/academic-year.api';

const props = defineProps<{
  visible: boolean;
  editData?: Enrollment | null;
}>();

const emit = defineEmits<{
  'update:visible': [val: boolean];
  'saved': [];
}>();

const loading = ref(false);
const errorMsg = ref('');
const students = ref<Student[]>([]);
const classes = ref<AcademicClass[]>([]);
const sections = ref<Section[]>([]);
const academicYears = ref<AcademicYear[]>([]);

const form = ref({
  student_id: null as number | null,
  section_id: null as number | null,
  academic_year_id: null as number | null,
  roll_no: '' as string | null,
  is_active: true,
});

onMounted(async () => {
  try {
    const [stuRes, clRes, ayRes] = await Promise.all([
      studentApi.getStudents(1, 100),
      academicApi.getClasses(1, 100),
      academicYearApi.getAcademicYears(1, 100),
    ]);
    students.value = stuRes.data.data?.items ?? [];
    classes.value = clRes.data.data?.items ?? [];
    academicYears.value = ayRes.data.data?.items ?? [];
  } catch (e) { console.error(e); }
});

watch(() => props.visible, (val) => {
  if (val) {
    if (props.editData) {
      form.value = {
        student_id: props.editData.student_id,
        section_id: props.editData.section_id,
        academic_year_id: props.editData.academic_year_id,
        roll_no: props.editData.roll_no ?? '',
        is_active: props.editData.is_active,
      };
    } else {
      form.value = { student_id: null, section_id: null, academic_year_id: null, roll_no: '', is_active: true };
    }
    errorMsg.value = '';
  }
});

const close = () => emit('update:visible', false);

const save = async () => {
  if (!form.value.student_id || !form.value.section_id || !form.value.academic_year_id) {
    errorMsg.value = 'Please fill all required fields';
    return;
  }
  loading.value = true;
  errorMsg.value = '';
  try {
    if (props.editData) {
      const payload: EnrollmentUpdatePayload = {
        roll_no: form.value.roll_no || null,
        is_active: form.value.is_active,
      };
      await enrollmentApi.updateEnrollment(props.editData.id, payload);
    } else {
      const payload: EnrollmentCreatePayload = {
        student_id: form.value.student_id,
        section_id: form.value.section_id,
        academic_year_id: form.value.academic_year_id,
        roll_no: form.value.roll_no || null,
        is_active: form.value.is_active,
      };
      await enrollmentApi.createEnrollment(payload);
    }
    emit('saved');
    close();
  } catch (err: any) {
    errorMsg.value = err.response?.data?.message || 'Failed to save enrollment';
  } finally { loading.value = false; }
};
</script>

<template>
  <Dialog :visible="visible" @update:visible="close" modal :header="editData ? 'Edit Enrollment' : 'Create Enrollment'" :style="{ width: '30rem' }">
    <div v-if="errorMsg" class="p-3 bg-red-50 dark:bg-red-950 text-red-600 dark:text-red-400 rounded-lg text-sm mb-4">
      {{ errorMsg }}
    </div>
    <div class="flex flex-col gap-4">
      <div class="flex flex-col gap-2">
        <label class="font-medium text-surface-700 dark:text-surface-300">Student *</label>
        <Dropdown v-model="form.student_id" :options="students" optionLabel="full_name" optionValue="id" placeholder="Select Student" :disabled="!!editData" filter />
      </div>
      <div class="flex flex-col gap-2">
        <label class="font-medium text-surface-700 dark:text-surface-300">Academic Year *</label>
        <Dropdown v-model="form.academic_year_id" :options="academicYears" optionLabel="name" optionValue="id" placeholder="Select Year" :disabled="!!editData" />
      </div>
      <div class="flex flex-col gap-2">
        <label class="font-medium text-surface-700 dark:text-surface-300">Section *</label>
        <Dropdown v-model="form.section_id" :options="sections" optionLabel="name" optionValue="id" placeholder="Select Section" :disabled="!!editData" />
      </div>
      <div class="flex flex-col gap-2">
        <label class="font-medium text-surface-700 dark:text-surface-300">Roll Number</label>
        <InputText v-model="form.roll_no" placeholder="Optional" />
      </div>
      <div class="flex items-center gap-2">
        <Checkbox v-model="form.is_active" :binary="true" inputId="enroll_active" />
        <label for="enroll_active" class="text-surface-700 dark:text-surface-300">Active</label>
      </div>
    </div>
    <template #footer>
      <Button label="Cancel" text severity="secondary" @click="close" />
      <Button label="Save" icon="pi pi-check" @click="save" :loading="loading" />
    </template>
  </Dialog>
</template>
