<script setup lang="ts">
import { ref, watch } from 'vue';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import Dropdown from 'primevue/dropdown';
import Checkbox from 'primevue/checkbox';
import Button from 'primevue/button';
import type { Subject, SubjectCreatePayload, SubjectUpdatePayload } from '../types/academic.types';
import { academicApi } from '../api/academic.api';

const props = defineProps<{
  visible: boolean;
  editData?: Subject | null;
}>();

const emit = defineEmits<{
  'update:visible': [val: boolean];
  'saved': [];
}>();

const loading = ref(false);
const errorMsg = ref('');

const subjectTypes = [
  { label: 'Mandatory', value: 'mandatory' },
  { label: 'Optional', value: 'optional' },
  { label: 'Elective', value: 'elective' }
];

const form = ref({
  name: '',
  code: '',
  credit_hours: 1,
  subject_type: 'mandatory',
  is_active: true
});

watch(() => props.visible, (val) => {
  if (val) {
    if (props.editData) {
      form.value = {
        name: props.editData.name,
        code: props.editData.code,
        credit_hours: props.editData.credit_hours,
        subject_type: props.editData.subject_type,
        is_active: props.editData.is_active
      };
    } else {
      form.value = { name: '', code: '', credit_hours: 1, subject_type: 'mandatory', is_active: true };
    }
    errorMsg.value = '';
  }
});

const close = () => {
  emit('update:visible', false);
};

const save = async () => {
  loading.value = true;
  errorMsg.value = '';
  try {
    if (props.editData) {
      await academicApi.updateSubject(props.editData.id, form.value as SubjectUpdatePayload);
    } else {
      await academicApi.createSubject(form.value as SubjectCreatePayload);
    }
    emit('saved');
    close();
  } catch (err: any) {
    errorMsg.value = err.response?.data?.message || 'Failed to save subject';
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <Dialog 
    :visible="visible" 
    @update:visible="close" 
    modal 
    :header="editData ? 'Edit Subject' : 'Create Subject'" 
    :style="{ width: '25rem' }"
  >
    <div v-if="errorMsg" class="p-3 bg-red-100 text-red-600 rounded-md text-sm mb-4">
      {{ errorMsg }}
    </div>

    <div class="flex flex-col gap-4">
      <div class="flex flex-col gap-2">
        <label for="name" class="font-medium">Subject Name</label>
        <InputText id="name" v-model="form.name" required autofocus />
      </div>

      <div class="flex flex-col gap-2">
        <label for="code" class="font-medium">Subject Code</label>
        <InputText id="code" v-model="form.code" required />
      </div>
      
      <div class="flex flex-col gap-2">
        <label for="subject_type" class="font-medium">Type</label>
        <Dropdown 
          id="subject_type" 
          v-model="form.subject_type" 
          :options="subjectTypes" 
          optionLabel="label" 
          optionValue="value" 
        />
      </div>

      <div class="flex flex-col gap-2">
        <label for="credit_hours" class="font-medium">Credit Hours</label>
        <InputNumber id="credit_hours" v-model="form.credit_hours" :min="0" :max="10" />
      </div>

      <div class="flex items-center gap-2 mt-2">
        <Checkbox inputId="is_active" v-model="form.is_active" :binary="true" />
        <label for="is_active">Is Active</label>
      </div>
    </div>

    <template #footer>
      <Button label="Cancel" text severity="secondary" @click="close" />
      <Button label="Save" @click="save" :loading="loading" />
    </template>
  </Dialog>
</template>
