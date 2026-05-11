<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import Checkbox from 'primevue/checkbox';
import Button from 'primevue/button';
import type { AcademicClass, ClassCreatePayload, ClassUpdatePayload } from '../types/academic.types';
import { academicApi } from '../api/academic.api';

const props = defineProps<{ visible: boolean; editData?: AcademicClass | null }>();
const emit = defineEmits<{ 'update:visible': [val: boolean]; 'saved': [] }>();

const dialogVisible = computed({ get: () => props.visible, set: (v: boolean) => emit('update:visible', v) });
const loading = ref(false);
const errorMsg = ref('');

const form = ref({ name: '', name_bn: '' as string | null, numeric_level: null as number | null, is_active: true });

watch(() => props.visible, (val) => {
  if (val) {
    form.value = props.editData
      ? { name: props.editData.name, name_bn: props.editData.name_bn ?? '', numeric_level: props.editData.numeric_level ?? null, is_active: props.editData.is_active }
      : { name: '', name_bn: '', numeric_level: null, is_active: true };
    errorMsg.value = '';
  }
});

const save = async () => {
  loading.value = true; errorMsg.value = '';
  try {
    if (props.editData) {
      await academicApi.updateClass(props.editData.id, form.value as ClassUpdatePayload);
    } else {
      await academicApi.createClass(form.value as ClassCreatePayload);
    }
    emit('saved'); dialogVisible.value = false;
  } catch (err: any) {
    errorMsg.value = err.response?.data?.message || 'Failed to save class';
  } finally { loading.value = false; }
};
</script>

<template>
  <Dialog v-model:visible="dialogVisible" modal :header="editData ? 'Edit Class' : 'Create Class'" :style="{ width: '25rem' }">
    <div v-if="errorMsg" class="ems-error">{{ errorMsg }}</div>
    <div class="flex flex-col gap-4">
      <div class="ems-field">
        <label for="name">Class Name *</label>
        <InputText id="name" v-model="form.name" required autofocus />
      </div>
      <div class="ems-field">
        <label for="name_bn">Name (Bengali)</label>
        <InputText id="name_bn" v-model="form.name_bn" placeholder="বাংলায় নাম (ঐচ্ছিক)" />
      </div>
      <div class="ems-field">
        <label for="numeric_level">Numeric Level</label>
        <InputNumber id="numeric_level" v-model="form.numeric_level" :min="1" placeholder="Optional" />
      </div>
      <div class="flex items-center gap-2 mt-2">
        <Checkbox inputId="is_active" v-model="form.is_active" :binary="true" />
        <label for="is_active">Is Active</label>
      </div>
    </div>
    <template #footer>
      <Button label="Cancel" text severity="secondary" @click="dialogVisible = false" />
      <Button label="Save" icon="pi pi-check" @click="save" :loading="loading" />
    </template>
  </Dialog>
</template>
