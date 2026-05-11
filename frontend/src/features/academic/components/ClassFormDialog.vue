<script setup lang="ts">
import { ref, watch } from 'vue';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import Checkbox from 'primevue/checkbox';
import Button from 'primevue/button';
import type { AcademicClass, ClassCreatePayload, ClassUpdatePayload } from '../types/academic.types';
import { academicApi } from '../api/academic.api';

const props = defineProps<{
  visible: boolean;
  editData?: AcademicClass | null;
}>();

const emit = defineEmits<{
  'update:visible': [val: boolean];
  'saved': [];
}>();

const loading = ref(false);
const errorMsg = ref('');

const form = ref({
  name: '',
  numeric_level: null as number | null,
  is_active: true
});

watch(() => props.visible, (val) => {
  if (val) {
    if (props.editData) {
      form.value = {
        name: props.editData.name,
        numeric_level: props.editData.numeric_level ?? null,
        is_active: props.editData.is_active
      };
    } else {
      form.value = { name: '', numeric_level: null, is_active: true };
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
      await academicApi.updateClass(props.editData.id, form.value as ClassUpdatePayload);
    } else {
      await academicApi.createClass(form.value as ClassCreatePayload);
    }
    emit('saved');
    close();
  } catch (err: any) {
    errorMsg.value = err.response?.data?.message || 'Failed to save class';
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
    :header="editData ? 'Edit Class' : 'Create Class'" 
    :style="{ width: '25rem' }"
  >
    <div v-if="errorMsg" class="p-3 bg-red-100 text-red-600 rounded-md text-sm mb-4">
      {{ errorMsg }}
    </div>

    <div class="flex flex-col gap-4">
      <div class="flex flex-col gap-2">
        <label for="name" class="font-medium">Class Name</label>
        <InputText id="name" v-model="form.name" required autofocus />
      </div>

      <div class="flex flex-col gap-2">
        <label for="numeric_level" class="font-medium">Numeric Level</label>
        <InputNumber id="numeric_level" v-model="form.numeric_level" :min="1" placeholder="Optional" />
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
