<script setup lang="ts">
import { ref, watch, computed } from 'vue';
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
  name_bn: '' as string | null,
  description: '' as string | null,
});

watch(() => props.visible, (val) => {
  if (val) {
    if (props.editData) {
      form.value = {
        name: props.editData.name,
        name_bn: props.editData.name_bn ?? '',
        description: props.editData.description ?? '',
      };
    } else {
      form.value = { name: '', name_bn: '', description: '' };
    }
    errorMsg.value = '';
  }
});

const dialogVisible = computed({
  get: () => props.visible,
  set: (val: boolean) => emit('update:visible', val)
});

const save = async () => {
  loading.value = true;
  errorMsg.value = '';
  try {
    const payload = {
      name: form.value.name,
      name_bn: form.value.name_bn || null,
      description: form.value.description || null,
    };
    if (props.editData) {
      await examApi.updateExamType(props.editData.id, payload as ExamTypeUpdatePayload);
    } else {
      await examApi.createExamType(payload as ExamTypeCreatePayload);
    }
    emit('saved');
    dialogVisible.value = false;
  } catch (err: any) {
    errorMsg.value = err.response?.data?.message || 'Failed to save exam type';
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <Dialog
    v-model:visible="dialogVisible"
    modal
    :header="editData ? 'Edit Exam Type' : 'Create Exam Type'"
    :style="{ width: '28rem' }"
  >
    <div v-if="errorMsg" class="ems-error">{{ errorMsg }}</div>

    <div class="flex flex-col gap-4">
      <div class="ems-field">
        <label for="et-name">Name</label>
        <InputText id="et-name" v-model="form.name" placeholder="e.g. Midterm, Final" required autofocus />
      </div>

      <div class="ems-field">
        <label for="et-name-bn">Name (Bengali)</label>
        <InputText id="et-name-bn" v-model="form.name_bn" placeholder="বাংলায় নাম (ঐচ্ছিক)" />
      </div>

      <div class="ems-field">
        <label for="et-desc">Description</label>
        <Textarea id="et-desc" v-model="form.description" rows="3" placeholder="Optional description" />
      </div>
    </div>

    <template #footer>
      <Button label="Cancel" text severity="secondary" @click="dialogVisible = false" />
      <Button label="Save" icon="pi pi-check" @click="save" :loading="loading" />
    </template>
  </Dialog>
</template>
