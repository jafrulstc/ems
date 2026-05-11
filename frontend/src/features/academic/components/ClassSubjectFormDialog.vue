<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue';
import Dialog from 'primevue/dialog';
import Dropdown from 'primevue/dropdown';
import InputNumber from 'primevue/inputnumber';
import Button from 'primevue/button';
import type { ClassSubject, ClassSubjectCreatePayload, ClassSubjectUpdatePayload, AcademicClass, Subject } from '../types/academic.types';
import { academicApi } from '../api/academic.api';

const props = defineProps<{ visible: boolean; editData?: ClassSubject | null }>();
const emit = defineEmits<{ 'update:visible': [val: boolean]; 'saved': [] }>();

const dialogVisible = computed({ get: () => props.visible, set: (v: boolean) => emit('update:visible', v) });
const loading = ref(false);
const errorMsg = ref('');
const classes = ref<AcademicClass[]>([]);
const subjects = ref<Subject[]>([]);
const form = ref({ class_id: null as number | null, subject_id: null as number | null, full_marks: 100, pass_marks: 33 });

onMounted(async () => {
  try {
    const [clsRes, subRes] = await Promise.all([
      academicApi.getClasses(1, 100),
      academicApi.getSubjects(1, 100),
    ]);
    classes.value = clsRes.data.data?.items ?? [];
    subjects.value = subRes.data.data?.items ?? [];
  } catch (e) { console.error('Failed to load classes/subjects', e); }
});

watch(() => props.visible, (val) => {
  if (val) {
    form.value = props.editData
      ? { class_id: props.editData.class_id, subject_id: props.editData.subject_id, full_marks: props.editData.full_marks, pass_marks: props.editData.pass_marks }
      : { class_id: null, subject_id: null, full_marks: 100, pass_marks: 33 };
    errorMsg.value = '';
  }
});

const save = async () => {
  if (!form.value.class_id || !form.value.subject_id) { errorMsg.value = 'Please select class and subject'; return; }
  loading.value = true; errorMsg.value = '';
  try {
    if (props.editData) {
      await academicApi.updateClassSubject(props.editData.id, { full_marks: form.value.full_marks, pass_marks: form.value.pass_marks } as ClassSubjectUpdatePayload);
    } else {
      await academicApi.createClassSubject(form.value as ClassSubjectCreatePayload);
    }
    emit('saved'); dialogVisible.value = false;
  } catch (err: any) {
    errorMsg.value = err.response?.data?.message || 'Failed to save mapping';
  } finally { loading.value = false; }
};
</script>

<template>
  <Dialog v-model:visible="dialogVisible" modal :header="editData ? 'Edit Mapping' : 'Create Mapping'" :style="{ width: '28rem' }">
    <div v-if="errorMsg" class="ems-error">{{ errorMsg }}</div>
    <div class="flex flex-col gap-4">
      <div class="ems-field">
        <label for="cs-class">Class *</label>
        <Dropdown id="cs-class" v-model="form.class_id" :options="classes" optionLabel="name" optionValue="id"
          placeholder="Select Class" :disabled="!!editData" required />
      </div>
      <div class="ems-field">
        <label for="cs-subject">Subject *</label>
        <Dropdown id="cs-subject" v-model="form.subject_id" :options="subjects" optionLabel="name" optionValue="id"
          placeholder="Select Subject" :disabled="!!editData" required />
      </div>
      <div class="ems-field">
        <label for="cs-full">Full Marks</label>
        <InputNumber id="cs-full" v-model="form.full_marks" :min="1" />
      </div>
      <div class="ems-field">
        <label for="cs-pass">Pass Marks</label>
        <InputNumber id="cs-pass" v-model="form.pass_marks" :min="0" />
      </div>
    </div>
    <template #footer>
      <Button label="Cancel" text severity="secondary" @click="dialogVisible = false" />
      <Button label="Save" icon="pi pi-check" @click="save" :loading="loading" />
    </template>
  </Dialog>
</template>
