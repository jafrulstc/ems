<script setup lang="ts">
import { ref, watch } from 'vue';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Button from 'primevue/button';
import type { ExamType, ExamTypeCreatePayload, ExamTypeUpdatePayload } from '../types/exam.types';
import { examApi } from '../api/exam.api';

const props = defineProps<{
  visible: boolean;
  editData?: ExamType | null;
}>();

const emit = defineEmits<{
  'update:visible': [val: boolean];
  'saved': [];
}>();

const loading = ref(false);
const errorMsg = ref('');

const form = ref({
  name: '',
  description: '' as string | null,
});

watch(() => props.visible, (val) => {
  if (val) {
    if (props.editData) {
      form.value = {
        name: props.editData.name,
        description: props.editData.description ?? '',
      };
    } else {
      form.value = { name: '', description: '' };
    }
    errorMsg.value = '';
  }
});

const close = () => emit('update:visible', false);

const save = async () => {
  loading.value = true;
  errorMsg.value = '';
  try {
    const payload = {
      name: form.value.name,
      description: form.value.description || null,
    };
    if (props.editData) {
      await examApi.updateExamType(props.editData.id, payload as ExamTypeUpdatePayload);
    } else {
      await examApi.createExamType(payload as ExamTypeCreatePayload);
    }
    emit('saved');
    close();
  } catch (err: any) {
    errorMsg.value = err.response?.data?.message || 'Failed to save exam type';
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
    :header="editData ? 'Edit Exam Type' : 'Create Exam Type'"
    :style="{ width: '28rem' }"
  >
    <div v-if="errorMsg" class="p-3 bg-red-50 dark:bg-red-950 text-red-600 dark:text-red-400 rounded-lg text-sm mb-4">
      {{ errorMsg }}
    </div>

    <div class="flex flex-col gap-4">
      <div class="flex flex-col gap-2">
        <label for="et-name" class="font-medium text-surface-700 dark:text-surface-300">Name</label>
        <InputText id="et-name" v-model="form.name" placeholder="e.g. Midterm, Final" required autofocus />
      </div>

      <div class="flex flex-col gap-2">
        <label for="et-desc" class="font-medium text-surface-700 dark:text-surface-300">Description</label>
        <Textarea id="et-desc" v-model="form.description" rows="3" placeholder="Optional description" />
      </div>
    </div>

    <template #footer>
      <Button label="Cancel" text severity="secondary" @click="close" />
      <Button label="Save" icon="pi pi-check" @click="save" :loading="loading" />
    </template>
  </Dialog>
</template>
