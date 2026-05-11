<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Checkbox from 'primevue/checkbox';
import Button from 'primevue/button';
import Calendar from 'primevue/calendar';
import type { AcademicYear, AcademicYearCreatePayload, AcademicYearUpdatePayload } from '../types/academic-year.types';
import { academicYearApi } from '../api/academic-year.api';

const props = defineProps<{
  visible: boolean;
  editData?: AcademicYear | null;
}>();

const emit = defineEmits<{
  'update:visible': [val: boolean];
  'saved': [];
}>();

const loading = ref(false);
const errorMsg = ref('');

const form = ref({
  name: '',
  start_date: null as Date | null,
  end_date: null as Date | null,
  is_active: true,
});

watch(() => props.visible, (val) => {
  if (val) {
    if (props.editData) {
      form.value = {
        name: props.editData.name,
        start_date: new Date(props.editData.start_date),
        end_date: new Date(props.editData.end_date),
        is_active: props.editData.is_active,
      };
    } else {
      form.value = { name: '', start_date: null, end_date: null, is_active: true };
    }
    errorMsg.value = '';
  }
});

const dialogVisible = computed({
  get: () => props.visible,
  set: (val: boolean) => emit('update:visible', val)
});

const formatDate = (d: Date | null) => d ? d.toISOString().split('T')[0] : null;

const save = async () => {
  if (!form.value.name || !form.value.start_date || !form.value.end_date) {
    errorMsg.value = 'Please fill all required fields';
    return;
  }
  loading.value = true;
  errorMsg.value = '';
  try {
    if (props.editData) {
      const payload: AcademicYearUpdatePayload = {
        name: form.value.name,
        start_date: formatDate(form.value.start_date),
        end_date: formatDate(form.value.end_date),
        is_active: form.value.is_active,
      };
      await academicYearApi.updateAcademicYear(props.editData.id, payload);
    } else {
      const payload: AcademicYearCreatePayload = {
        name: form.value.name,
        start_date: formatDate(form.value.start_date)!,
        end_date: formatDate(form.value.end_date)!,
        is_active: form.value.is_active,
      };
      await academicYearApi.createAcademicYear(payload);
    }
    emit('saved');
    dialogVisible.value = false;
  } catch (err: any) {
    errorMsg.value = err.response?.data?.message || 'Failed to save academic year';
  } finally { loading.value = false; }
};
</script>

<template>
  <Dialog v-model:visible="dialogVisible" modal :header="editData ? 'Edit Academic Year' : 'Create Academic Year'" :style="{ width: '28rem' }">
    <div v-if="errorMsg" class="ems-error">{{ errorMsg }}</div>
    <div class="flex flex-col gap-4">
      <div class="ems-field">
        <label>Name *</label>
        <InputText v-model="form.name" placeholder="e.g. 2025-2026" autofocus />
      </div>
      <div class="grid grid-cols-2 gap-4">
        <div class="ems-field">
          <label>Start Date *</label>
          <Calendar v-model="form.start_date" dateFormat="yy-mm-dd" showIcon />
        </div>
        <div class="ems-field">
          <label>End Date *</label>
          <Calendar v-model="form.end_date" dateFormat="yy-mm-dd" showIcon />
        </div>
      </div>
      <div class="flex items-center gap-2">
        <Checkbox v-model="form.is_active" :binary="true" inputId="ay_active" />
        <label for="ay_active" class="text-surface-700 dark:text-surface-300">Active</label>
      </div>
    </div>
    <template #footer>
      <Button label="Cancel" text severity="secondary" @click="dialogVisible = false" />
      <Button label="Save" icon="pi pi-check" @click="save" :loading="loading" />
    </template>
  </Dialog>
</template>
