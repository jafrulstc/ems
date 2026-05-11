<script setup lang="ts">
import { ref, watch } from 'vue';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
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

const form = ref({
  name: '',
  code: '' as string | null,
  is_optional: false,
});

watch(() => props.visible, (val) => {
  if (val) {
    if (props.editData) {
      form.value = {
        name: props.editData.name,
        code: props.editData.code ?? '',
        is_optional: props.editData.is_optional,
      };
    } else {
      form.value = { name: '', code: '', is_optional: false };
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
    const payload = {
      ...form.value,
      code: form.value.code || null,
    };

    if (props.editData) {
      await academicApi.updateSubject(props.editData.id, payload as SubjectUpdatePayload);
    } else {
      await academicApi.createSubject(payload as SubjectCreatePayload);
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
        <label for="code" class="font-medium">Subject Code (Optional)</label>
        <InputText id="code" v-model="form.code" />
      </div>

      <div class="flex items-center gap-2 mt-2">
        <Checkbox inputId="is_optional" v-model="form.is_optional" :binary="true" />
        <label for="is_optional">Optional Subject</label>
      </div>
    </div>

    <template #footer>
      <Button label="Cancel" text severity="secondary" @click="close" />
      <Button label="Save" @click="save" :loading="loading" />
    </template>
  </Dialog>
</template>
