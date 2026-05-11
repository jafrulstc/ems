<script setup lang="ts">
import { ref, watch } from 'vue';
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

const close = () => emit('update:visible', false);

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
    close();
  } catch (err: any) {
    errorMsg.value = err.response?.data?.message || 'Failed to save academic year';
  } finally { loading.value = false; }
};
</script>

<template>
  <Dialog :visible="visible" @update:visible="close" modal :header="editData ? 'Edit Academic Year' : 'Create Academic Year'" :style="{ width: '28rem' }">
    <div v-if="errorMsg" class="p-3 bg-red-50 dark:bg-red-950 text-red-600 dark:text-red-400 rounded-lg text-sm mb-4">
      {{ errorMsg }}
    </div>
    <div class="flex flex-col gap-4">
      <div class="flex flex-col gap-2">
        <label class="font-medium text-surface-700 dark:text-surface-300">Name *</label>
        <InputText v-model="form.name" placeholder="e.g. 2025-2026" autofocus />
      </div>
      <div class="grid grid-cols-2 gap-4">
        <div class="flex flex-col gap-2">
          <label class="font-medium text-surface-700 dark:text-surface-300">Start Date *</label>
          <Calendar v-model="form.start_date" dateFormat="yy-mm-dd" showIcon />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium text-surface-700 dark:text-surface-300">End Date *</label>
          <Calendar v-model="form.end_date" dateFormat="yy-mm-dd" showIcon />
        </div>
      </div>
      <div class="flex items-center gap-2">
        <Checkbox v-model="form.is_active" :binary="true" inputId="ay_active" />
        <label for="ay_active" class="text-surface-700 dark:text-surface-300">Active</label>
      </div>
    </div>
    <template #footer>
      <Button label="Cancel" text severity="secondary" @click="close" />
      <Button label="Save" icon="pi pi-check" @click="save" :loading="loading" />
    </template>
  </Dialog>
</template>
