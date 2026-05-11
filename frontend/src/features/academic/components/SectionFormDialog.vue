<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Dropdown from 'primevue/dropdown';
import type { Section, SectionCreatePayload, SectionUpdatePayload, AcademicClass } from '../types/academic.types';
import { academicApi } from '../api/academic.api';

const props = defineProps<{ visible: boolean; editData?: Section | null }>();
const emit = defineEmits<{ 'update:visible': [val: boolean]; 'saved': [] }>();

const dialogVisible = computed({ get: () => props.visible, set: (v: boolean) => emit('update:visible', v) });
const loading = ref(false);
const errorMsg = ref('');
const classes = ref<AcademicClass[]>([]);
const form = ref({ name: '', name_bn: '' as string | null, class_id: null as number | null });

onMounted(async () => {
  try {
    const res = await academicApi.getClasses(1, 100);
    classes.value = res.data.data?.items ?? [];
  } catch (e) { console.error('Failed to load classes', e); }
});

watch(() => props.visible, (val) => {
  if (val) {
    form.value = props.editData
      ? { name: props.editData.name, name_bn: props.editData.name_bn ?? '', class_id: props.editData.class_id }
      : { name: '', name_bn: '', class_id: null };
    errorMsg.value = '';
  }
});

const save = async () => {
  if (!form.value.class_id) { errorMsg.value = 'Please select a class'; return; }
  loading.value = true; errorMsg.value = '';
  try {
    if (props.editData) {
      await academicApi.updateSection(props.editData.id, { name: form.value.name } as SectionUpdatePayload);
    } else {
      await academicApi.createSection(form.value as SectionCreatePayload);
    }
    emit('saved'); dialogVisible.value = false;
  } catch (err: any) {
    errorMsg.value = err.response?.data?.message || 'Failed to save section';
  } finally { loading.value = false; }
};
</script>

<template>
  <Dialog v-model:visible="dialogVisible" modal :header="editData ? 'Edit Section' : 'Create Section'" :style="{ width: '25rem' }">
    <div v-if="errorMsg" class="ems-error">{{ errorMsg }}</div>
    <div class="flex flex-col gap-4">
      <div class="ems-field">
        <label for="class_id">Class</label>
        <Dropdown id="class_id" v-model="form.class_id" :options="classes" optionLabel="name" optionValue="id"
          placeholder="Select a Class" :disabled="!!editData" required />
      </div>
      <div class="ems-field">
        <label for="name">Section Name (e.g. A, Rose)</label>
        <InputText id="name" v-model="form.name" required />
      </div>
      <div class="ems-field">
        <label for="name_bn">Name (Bengali)</label>
        <InputText id="name_bn" v-model="form.name_bn" placeholder="বাংলায় নাম (ঐচ্ছিক)" />
      </div>
    </div>
    <template #footer>
      <Button label="Cancel" text severity="secondary" @click="dialogVisible = false" />
      <Button label="Save" icon="pi pi-check" @click="save" :loading="loading" />
    </template>
  </Dialog>
</template>
