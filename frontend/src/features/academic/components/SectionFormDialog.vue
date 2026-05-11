<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Dropdown from 'primevue/dropdown';
import type { Section, SectionCreatePayload, SectionUpdatePayload, AcademicClass } from '../types/academic.types';
import { academicApi } from '../api/academic.api';

const props = defineProps<{
  visible: boolean;
  editData?: Section | null;
}>();

const emit = defineEmits<{
  'update:visible': [val: boolean];
  'saved': [];
}>();

const loading = ref(false);
const errorMsg = ref('');
const classes = ref<AcademicClass[]>([]);

const form = ref({
  name: '',
  class_id: null as number | null,
});

onMounted(async () => {
  try {
    const res = await academicApi.getClasses(1, 100);
    classes.value = res.data.data?.items ?? [];
  } catch (e) {
    console.error('Failed to load classes', e);
  }
});

watch(() => props.visible, (val) => {
  if (val) {
    if (props.editData) {
      form.value = {
        name: props.editData.name,
        class_id: props.editData.class_id,
      };
    } else {
      form.value = { name: '', class_id: null };
    }
    errorMsg.value = '';
  }
});

const close = () => {
  emit('update:visible', false);
};

const save = async () => {
  if (!form.value.class_id) {
    errorMsg.value = 'Please select a class';
    return;
  }
  
  loading.value = true;
  errorMsg.value = '';
  try {
    if (props.editData) {
      await academicApi.updateSection(props.editData.id, { name: form.value.name } as SectionUpdatePayload);
    } else {
      await academicApi.createSection(form.value as SectionCreatePayload);
    }
    emit('saved');
    close();
  } catch (err: any) {
    errorMsg.value = err.response?.data?.message || 'Failed to save section';
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
    :header="editData ? 'Edit Section' : 'Create Section'" 
    :style="{ width: '25rem' }"
  >
    <div v-if="errorMsg" class="p-3 bg-red-100 text-red-600 rounded-md text-sm mb-4">
      {{ errorMsg }}
    </div>

    <div class="flex flex-col gap-4">
      <div class="flex flex-col gap-2">
        <label for="class_id" class="font-medium">Class</label>
        <Dropdown 
          id="class_id" 
          v-model="form.class_id" 
          :options="classes" 
          optionLabel="name" 
          optionValue="id" 
          placeholder="Select a Class" 
          :disabled="!!editData"
          required 
        />
      </div>

      <div class="flex flex-col gap-2">
        <label for="name" class="font-medium">Section Name (e.g. A, Rose)</label>
        <InputText id="name" v-model="form.name" required />
      </div>
    </div>

    <template #footer>
      <Button label="Cancel" text severity="secondary" @click="close" />
      <Button label="Save" @click="save" :loading="loading" />
    </template>
  </Dialog>
</template>
