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
  editData?: Guardian | null;
}>();

const emit = defineEmits<{
  'update:visible': [val: boolean];
  'saved': [];
}>();

const loading = ref(false);
const errorMsg = ref('');

const form = ref<GuardianCreatePayload>({
  guardian_name: '',
  relation: '',
  phone: '',
  father_name: '',
  mother_name: '',
  email: '',
  national_id: '',
  occupation: '',
  is_active: true
});

watch(() => props.visible, (val) => {
  if (val) {
    if (props.editData) {
      form.value = {
        guardian_name: props.editData.guardian_name,
        relation: props.editData.relation,
        phone: props.editData.phone,
        father_name: props.editData.father_name || '',
        mother_name: props.editData.mother_name || '',
        email: props.editData.email || '',
        national_id: props.editData.national_id || '',
        occupation: props.editData.occupation || '',
        is_active: props.editData.is_active
      };
    } else {
      form.value = {
        guardian_name: '',
        relation: '',
        phone: '',
        father_name: '',
        mother_name: '',
        email: '',
        national_id: '',
        occupation: '',
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
  loading.value = true;
  errorMsg.value = '';
  try {
    const payload = { ...form.value };
    // sanitize empty strings to null for optional fields
    payload.father_name = payload.father_name || null;
    payload.mother_name = payload.mother_name || null;
    payload.email = payload.email || null;
    payload.national_id = payload.national_id || null;
    payload.occupation = payload.occupation || null;

    if (props.editData) {
      await studentApi.updateGuardian(props.editData.id, payload as GuardianUpdatePayload);
    } else {
      await studentApi.createGuardian(payload as GuardianCreatePayload);
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
        <label for="guardian_name" class="font-medium">Guardian Name *</label>
        <InputText id="guardian_name" v-model="form.guardian_name" required autofocus />
      </div>

      <div class="flex flex-col gap-2">
        <label for="relation" class="font-medium">Relation *</label>
        <InputText id="relation" v-model="form.relation" placeholder="e.g. Father, Uncle" required />
      </div>

      <div class="flex flex-col gap-2">
        <label for="phone" class="font-medium">Phone Number *</label>
        <InputText id="phone" v-model="form.phone" required />
      </div>

      <div class="flex flex-col gap-2">
        <label for="email" class="font-medium">Email (Optional)</label>
        <InputText id="email" type="email" v-model="form.email" />
      </div>

      <div class="flex flex-col gap-2">
        <label for="father_name" class="font-medium">Father's Name (Optional)</label>
        <InputText id="father_name" v-model="form.father_name" />
      </div>

      <div class="flex flex-col gap-2">
        <label for="mother_name" class="font-medium">Mother's Name (Optional)</label>
        <InputText id="mother_name" v-model="form.mother_name" />
      </div>

      <div class="flex flex-col gap-2">
        <label for="national_id" class="font-medium">National ID (Optional)</label>
        <InputText id="national_id" v-model="form.national_id" />
      </div>

      <div class="flex flex-col gap-2">
        <label for="occupation" class="font-medium">Occupation (Optional)</label>
        <InputText id="occupation" v-model="form.occupation" />
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
