<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Checkbox from 'primevue/checkbox';
import Button from 'primevue/button';
import type { Subject, SubjectCreatePayload, SubjectUpdatePayload } from '../types/academic.types';
import { academicApi } from '../api/academic.api';

const props = defineProps<{ visible: boolean; editData?: Subject | null }>();
const emit = defineEmits<{ 'update:visible': [val: boolean]; 'saved': [] }>();

const dialogVisible = computed({ get: () => props.visible, set: (v: boolean) => emit('update:visible', v) });
const loading = ref(false);
const errorMsg = ref('');
const form = ref({ name: '', name_bn: '' as string | null, code: '' as string | null, is_optional: false });

watch(() => props.visible, (val) => {
  if (val) {
    form.value = props.editData
      ? { name: props.editData.name, name_bn: props.editData.name_bn ?? '', code: props.editData.code ?? '', is_optional: props.editData.is_optional }
      : { name: '', name_bn: '', code: '', is_optional: false };
    errorMsg.value = '';
  }
});

const save = async () => {
  loading.value = true; errorMsg.value = '';
  try {
    const payload = { ...form.value, code: form.value.code || null };
    if (props.editData) {
      await academicApi.updateSubject(props.editData.id, payload as SubjectUpdatePayload);
    } else {
      await academicApi.createSubject(payload as SubjectCreatePayload);
    }
    emit('saved'); dialogVisible.value = false;
  } catch (err: any) {
    errorMsg.value = err.response?.data?.message || 'Failed to save subject';
  } finally { loading.value = false; }
};
</script>

<template>
  <Dialog v-model:visible="dialogVisible" modal :header="editData ? 'Edit Subject' : 'Create Subject'" :style="{ width: '25rem' }">
    <div v-if="errorMsg" class="ems-error">{{ errorMsg }}</div>
    <div class="flex flex-col gap-4">
      <div class="ems-field">
        <label for="name">Subject Name *</label>
        <InputText id="name" v-model="form.name" required autofocus />
      </div>
      <div class="ems-field">
        <label for="name_bn">Name (Bengali)</label>
        <InputText id="name_bn" v-model="form.name_bn" placeholder="বাংলায় নাম (ঐচ্ছিক)" />
      </div>
      <div class="ems-field">
        <label for="code">Subject Code</label>
        <InputText id="code" v-model="form.code" placeholder="Optional" />
      </div>
      <div class="flex items-center gap-2 mt-2">
        <Checkbox inputId="is_optional" v-model="form.is_optional" :binary="true" />
        <label for="is_optional">Optional Subject</label>
      </div>
    </div>
    <template #footer>
      <Button label="Cancel" text severity="secondary" @click="dialogVisible = false" />
      <Button label="Save" icon="pi pi-check" @click="save" :loading="loading" />
    </template>
  </Dialog>
</template>
