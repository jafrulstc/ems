<script setup lang="ts">
import { ref, watch } from 'vue';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Calendar from 'primevue/calendar';
import Dropdown from 'primevue/dropdown';
import Button from 'primevue/button';
import GeoAddressSelector from './GeoAddressSelector.vue';
import type { Student, StudentCreatePayload, StudentUpdatePayload } from '../types/student.types';
import { studentApi } from '../api/student.api';
import { format } from 'date-fns';

const props = defineProps<{
  visible: boolean;
  editData?: Student | null;
}>();

const emit = defineEmits<{
  'update:visible': [val: boolean];
  'saved': [];
}>();

const loading = ref(false);
const errorMsg = ref('');

const genderOptions = [
  { label: 'Male', value: 'Male' },
  { label: 'Female', value: 'Female' },
  { label: 'Other', value: 'Other' }
];

const bloodGroups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'].map(bg => ({ label: bg, value: bg }));

const form = ref({
  registration_no: '',
  full_name: '',
  dob: null as Date | null,
  gender: null as string | null,
  blood_group: null as string | null,
  village_id: null as number | null,
});

watch(() => props.visible, (val) => {
  if (val) {
    if (props.editData) {
      form.value = {
        registration_no: props.editData.registration_no,
        full_name: props.editData.full_name,
        dob: props.editData.dob ? new Date(props.editData.dob) : null,
        gender: props.editData.gender ?? null,
        blood_group: props.editData.blood_group ?? null,
        village_id: props.editData.village_id ?? null,
      };
    } else {
      form.value = {
        registration_no: '',
        full_name: '',
        dob: null,
        gender: null,
        blood_group: null,
        village_id: null,
      };
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
      dob: form.value.dob ? format(form.value.dob, 'yyyy-MM-dd') : null,
    };

    if (props.editData) {
      await studentApi.updateStudent(props.editData.id, payload as StudentUpdatePayload);
    } else {
      await studentApi.createStudent(payload as StudentCreatePayload);
    }
    emit('saved');
    close();
  } catch (err: any) {
    errorMsg.value = err.response?.data?.message || 'Failed to save student';
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
    :header="editData ? 'Edit Student' : 'Create Student'" 
    :style="{ width: '50rem' }"
  >
    <div v-if="errorMsg" class="p-3 bg-red-100 text-red-600 rounded-md text-sm mb-4">
      {{ errorMsg }}
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="flex flex-col gap-2">
        <label for="registration_no" class="font-medium">Registration No *</label>
        <InputText id="registration_no" v-model="form.registration_no" required autofocus />
      </div>

      <div class="flex flex-col gap-2">
        <label for="full_name" class="font-medium">Full Name *</label>
        <InputText id="full_name" v-model="form.full_name" required />
      </div>

      <div class="flex flex-col gap-2">
        <label for="dob" class="font-medium">Date of Birth</label>
        <Calendar id="dob" v-model="form.dob" dateFormat="yy-mm-dd" :showIcon="true" />
      </div>

      <div class="flex flex-col gap-2">
        <label for="gender" class="font-medium">Gender</label>
        <Dropdown id="gender" v-model="form.gender" :options="genderOptions" optionLabel="label" optionValue="value" placeholder="Select" showClear />
      </div>

      <div class="flex flex-col gap-2">
        <label for="blood_group" class="font-medium">Blood Group</label>
        <Dropdown id="blood_group" v-model="form.blood_group" :options="bloodGroups" optionLabel="label" optionValue="value" placeholder="Select" showClear />
      </div>

      <!-- Address -->
      <div class="col-span-1 md:col-span-2 pt-2 border-t border-surface-200 dark:border-surface-700 mt-2">
        <h3 class="text-lg font-semibold mb-3">Address</h3>
        <GeoAddressSelector v-model="form.village_id" />
      </div>
    </div>

    <template #footer>
      <Button label="Cancel" text severity="secondary" @click="close" />
      <Button label="Save" @click="save" :loading="loading" />
    </template>
  </Dialog>
</template>
