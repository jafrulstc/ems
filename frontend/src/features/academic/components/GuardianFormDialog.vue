<script setup lang="ts">
import { ref, watch } from 'vue';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Checkbox from 'primevue/checkbox';
import Button from 'primevue/button';
import type { Guardian, GuardianCreatePayload, GuardianUpdatePayload } from '../types/student.types';
import { studentApi } from '../api/student.api';

const props = defineProps<{
  visible: boolean;
  studentId?: number | null;
  editData?: Guardian | null;
}>();

const emit = defineEmits<{
  'update:visible': [val: boolean];
  'saved': [];
}>();

const loading = ref(false);
const errorMsg = ref('');

const form = ref({
  name: '',
  relation: '',
  phone: '' as string | null,
  email: '' as string | null,
  is_primary: false,
});

watch(() => props.visible, (val) => {
  if (val) {
    if (props.editData) {
      form.value = {
        name: props.editData.name,
        relation: props.editData.relation,
        phone: props.editData.phone ?? '',
        email: props.editData.email ?? '',
        is_primary: props.editData.is_primary,
      };
    } else {
      form.value = { name: '', relation: '', phone: '', email: '', is_primary: false };
    }
    errorMsg.value = '';
  }
});

const close = () => {
  emit('update:visible', false);
};

const save = async () => {
  if (!props.studentId && !props.editData) {
    errorMsg.value = 'Student ID is required to create a guardian';
    return;
  }

  loading.value = true;
  errorMsg.value = '';
  try {
    const payload = {
      ...form.value,
      phone: form.value.phone || null,
      email: form.value.email || null,
    };

    if (props.editData) {
      await studentApi.updateGuardian(props.editData.id, payload as GuardianUpdatePayload);
    } else {
      await studentApi.createStudentGuardian(props.studentId!, payload as Omit<GuardianCreatePayload, 'student_id'>);
    }
    emit('saved');
    close();
  } catch (err: any) {
    errorMsg.value = err.response?.data?.message || 'Failed to save guardian';
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
    :header="editData ? 'Edit Guardian' : 'Create Guardian'" 
    :style="{ width: '35rem' }"
  >
    <div v-if="errorMsg" class="p-3 bg-red-100 text-red-600 rounded-md text-sm mb-4">
      {{ errorMsg }}
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="flex flex-col gap-2">
        <label for="name" class="font-medium">Guardian Name *</label>
        <InputText id="name" v-model="form.name" required autofocus />
      </div>

      <div class="flex flex-col gap-2">
        <label for="relation" class="font-medium">Relation *</label>
        <InputText id="relation" v-model="form.relation" placeholder="e.g. Father, Uncle" required />
      </div>

      <div class="flex flex-col gap-2">
        <label for="phone" class="font-medium">Phone Number</label>
        <InputText id="phone" v-model="form.phone" />
      </div>

      <div class="flex flex-col gap-2">
        <label for="email" class="font-medium">Email (Optional)</label>
        <InputText id="email" type="email" v-model="form.email" />
      </div>

      <div class="flex items-center gap-2 mt-2 md:col-span-2">
        <Checkbox inputId="is_primary" v-model="form.is_primary" :binary="true" />
        <label for="is_primary">Primary Guardian</label>
      </div>
    </div>

    <template #footer>
      <Button label="Cancel" text severity="secondary" @click="close" />
      <Button label="Save" @click="save" :loading="loading" />
    </template>
  </Dialog>
</template>
