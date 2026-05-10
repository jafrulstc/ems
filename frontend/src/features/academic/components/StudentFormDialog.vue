<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Calendar from 'primevue/calendar';
import Dropdown from 'primevue/dropdown';
import Checkbox from 'primevue/checkbox';
import Button from 'primevue/button';
import GeoAddressSelector from './GeoAddressSelector.vue';
import type { Student, StudentCreatePayload, StudentUpdatePayload, Guardian } from '../types/student.types';
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
const guardians = ref<Guardian[]>([]);

const genderOptions = [
  { label: 'Male', value: 'M' },
  { label: 'Female', value: 'F' },
  { label: 'Other', value: 'O' }
];

const bloodGroups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'].map(bg => ({ label: bg, value: bg }));

const form = ref<any>({
  student_id: '',
  first_name: '',
  last_name: '',
  date_of_birth: null,
  gender: 'M',
  blood_group: null,
  religion: '',
  village_id: null,
  address_line: '',
  guardian_id: null,
  is_active: true
});

onMounted(async () => {
  try {
    const res = await studentApi.getGuardians(1, 1000); // Load all for dropdown
    guardians.value = res.data.data.items;
  } catch (e) {
    console.error('Failed to load guardians', e);
  }
});

watch(() => props.visible, (val) => {
  if (val) {
    if (props.editData) {
      form.value = {
        student_id: props.editData.student_id,
        first_name: props.editData.first_name,
        last_name: props.editData.last_name,
        date_of_birth: props.editData.date_of_birth ? new Date(props.editData.date_of_birth) : null,
        gender: props.editData.gender,
        blood_group: props.editData.blood_group,
        religion: props.editData.religion || '',
        village_id: props.editData.village_id,
        address_line: props.editData.address_line || '',
        guardian_id: props.editData.guardian_id,
        is_active: props.editData.is_active
      };
    } else {
      form.value = {
        student_id: '',
        first_name: '',
        last_name: '',
        date_of_birth: null,
        gender: 'M',
        blood_group: null,
        religion: '',
        village_id: null,
        address_line: '',
        guardian_id: null,
        is_active: true
      };
    }
    errorMsg.value = '';
  }
});

const close = () => {
  emit('update:visible', false);
};

const save = async () => {
  if (!form.value.guardian_id) {
    errorMsg.value = 'Please select a guardian.';
    return;
  }
  if (!form.value.date_of_birth) {
    errorMsg.value = 'Please select a date of birth.';
    return;
  }

  loading.value = true;
  errorMsg.value = '';
  
  try {
    const payload = { ...form.value };
    payload.date_of_birth = format(payload.date_of_birth, 'yyyy-MM-dd');
    payload.blood_group = payload.blood_group || null;
    payload.religion = payload.religion || null;
    payload.village_id = payload.village_id || null;
    payload.address_line = payload.address_line || null;

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
      <!-- Basic Info -->
      <div class="flex flex-col gap-2">
        <label for="student_id" class="font-medium">Student ID / Roll *</label>
        <InputText id="student_id" v-model="form.student_id" required autofocus />
      </div>

      <div class="flex flex-col gap-2">
        <label for="guardian_id" class="font-medium">Guardian *</label>
        <Dropdown 
          id="guardian_id" 
          v-model="form.guardian_id" 
          :options="guardians" 
          optionLabel="guardian_name" 
          optionValue="id" 
          placeholder="Select Guardian" 
          filter
          required 
        />
      </div>

      <div class="flex flex-col gap-2">
        <label for="first_name" class="font-medium">First Name *</label>
        <InputText id="first_name" v-model="form.first_name" required />
      </div>

      <div class="flex flex-col gap-2">
        <label for="last_name" class="font-medium">Last Name *</label>
        <InputText id="last_name" v-model="form.last_name" required />
      </div>

      <div class="flex flex-col gap-2">
        <label for="dob" class="font-medium">Date of Birth *</label>
        <Calendar id="dob" v-model="form.date_of_birth" dateFormat="yy-mm-dd" :showIcon="true" required />
      </div>

      <div class="flex flex-col gap-2">
        <label for="gender" class="font-medium">Gender *</label>
        <Dropdown id="gender" v-model="form.gender" :options="genderOptions" optionLabel="label" optionValue="value" required />
      </div>

      <!-- Optional Demographics -->
      <div class="flex flex-col gap-2">
        <label for="blood_group" class="font-medium">Blood Group</label>
        <Dropdown id="blood_group" v-model="form.blood_group" :options="bloodGroups" optionLabel="label" optionValue="value" placeholder="Select" showClear />
      </div>

      <div class="flex flex-col gap-2">
        <label for="religion" class="font-medium">Religion</label>
        <InputText id="religion" v-model="form.religion" />
      </div>

      <!-- Address -->
      <div class="col-span-1 md:col-span-2 pt-2 border-t border-surface-200 dark:border-surface-700 mt-2">
        <h3 class="text-lg font-semibold mb-3">Address</h3>
        <GeoAddressSelector v-model="form.village_id" class="mb-3" />
        
        <div class="flex flex-col gap-2">
          <label for="address_line" class="font-medium text-sm">Street Address / House No.</label>
          <InputText id="address_line" v-model="form.address_line" class="w-full" />
        </div>
      </div>

      <div class="flex items-center gap-2 mt-2 md:col-span-2">
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
