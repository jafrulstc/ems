<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Checkbox from 'primevue/checkbox';
import Button from 'primevue/button';
import type { Guardian, GuardianCreatePayload, GuardianUpdatePayload } from '../types/student.types';
import { studentApi } from '../api/student.api';

const props = defineProps<{ visible: boolean; studentId?: number | null; editData?: Guardian | null }>();
const emit = defineEmits<{ 'update:visible': [val: boolean]; 'saved': [] }>();

const dialogVisible = computed({ get: () => props.visible, set: (v: boolean) => emit('update:visible', v) });
const loading = ref(false);
const errorMsg = ref('');
const form = ref({ name: '', relation: '', phone: '' as string | null, email: '' as string | null, is_primary: false });

watch(() => props.visible, (val) => {
  if (val) {
    form.value = props.editData
      ? { name: props.editData.name, relation: props.editData.relation, phone: props.editData.phone ?? '',
          email: props.editData.email ?? '', is_primary: props.editData.is_primary }
      : { name: '', relation: '', phone: '', email: '', is_primary: false };
    errorMsg.value = '';
  }
});

const save = async () => {
  if (!props.studentId && !props.editData) { errorMsg.value = 'Student ID is required'; return; }
  loading.value = true; errorMsg.value = '';
  try {
    const payload = { ...form.value, phone: form.value.phone || null, email: form.value.email || null };
    if (props.editData) {
      await studentApi.updateGuardian(props.editData.id, payload as GuardianUpdatePayload);
    } else {
      await studentApi.createStudentGuardian(props.studentId!, payload as Omit<GuardianCreatePayload, 'student_id'>);
    }
    emit('saved'); dialogVisible.value = false;
  } catch (err: any) {
    errorMsg.value = err.response?.data?.message || 'Failed to save guardian';
  } finally { loading.value = false; }
};
</script>

<template>
  <Dialog v-model:visible="dialogVisible" modal :header="editData ? 'Edit Guardian' : 'Create Guardian'" :style="{ width: '35rem' }">
    <div v-if="errorMsg" class="ems-error">{{ errorMsg }}</div>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="ems-field">
        <label for="name">Guardian Name *</label>
        <InputText id="name" v-model="form.name" required autofocus />
      </div>
      <div class="ems-field">
        <label for="relation">Relation *</label>
        <InputText id="relation" v-model="form.relation" placeholder="e.g. Father, Uncle" required />
      </div>
      <div class="ems-field">
        <label for="phone">Phone Number</label>
        <InputText id="phone" v-model="form.phone" />
      </div>
      <div class="ems-field">
        <label for="email">Email</label>
        <InputText id="email" type="email" v-model="form.email" />
      </div>
      <div class="flex items-center gap-2 mt-2 md:col-span-2">
        <Checkbox inputId="is_primary" v-model="form.is_primary" :binary="true" />
        <label for="is_primary">Primary Guardian</label>
      </div>
    </div>
    <template #footer>
      <Button label="Cancel" text severity="secondary" @click="dialogVisible = false" />
      <Button label="Save" icon="pi pi-check" @click="save" :loading="loading" />
    </template>
  </Dialog>
</template>
