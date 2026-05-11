<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dropdown from 'primevue/dropdown';
import PageHeader from '@/components/shared/PageHeader.vue';
import EmptyState from '@/components/shared/EmptyState.vue';
import { academicApi } from '../api/academic.api';
import type { Section, AcademicClass } from '../types/academic.types';
import SectionFormDialog from '../components/SectionFormDialog.vue';
import { usePermission } from '@/features/auth/composables/usePermission';

const { hasPermission } = usePermission();
const canEdit = hasPermission('academic.sections.edit');
const canCreate = hasPermission('academic.sections.create');

const sections = ref<Section[]>([]);
const classes = ref<AcademicClass[]>([]);
const selectedClass = ref<number | null>(null);
const loading = ref(false);
const dialogVisible = ref(false);
const editingSection = ref<Section | null>(null);

const classMap = computed(() => {
  const map = new Map<number, string>();
  for (const c of classes.value) { map.set(c.id, c.name); }
  return map;
});

const fetchClasses = async () => {
  try {
    const res = await academicApi.getClasses(1, 100);
    classes.value = res.data.data?.items ?? [];
  } catch (e) { console.error(e); }
};

const fetchSections = async () => {
  loading.value = true;
  try {
    const res = await academicApi.getSections(1, 100, selectedClass.value || undefined);
    sections.value = res.data.data?.items ?? [];
  } catch (e) { console.error(e); } finally { loading.value = false; }
};

onMounted(() => { fetchClasses(); fetchSections(); });
const onClassFilterChange = () => { fetchSections(); };
const openNew = () => { editingSection.value = null; dialogVisible.value = true; };
const edit = (data: Section) => { editingSection.value = data; dialogVisible.value = true; };
</script>

<template>
  <div>
    <PageHeader title="Sections" subtitle="Manage sections within classes" icon="pi pi-th-large">
      <template #actions>
        <Button v-if="canCreate" label="Add Section" icon="pi pi-plus" @click="openNew" />
      </template>
    </PageHeader>

    <div class="ems-card">
      <div class="mb-4">
        <Dropdown v-model="selectedClass" :options="classes" optionLabel="name" optionValue="id"
          placeholder="Filter by Class" showClear @change="onClassFilterChange" class="w-full md:w-14rem" />
      </div>

      <DataTable v-if="sections.length" :value="sections" :loading="loading" stripedRows responsiveLayout="scroll">
        <Column header="Class" sortable style="width: 30%">
          <template #body="{ data }">{{ classMap.get(data.class_id) ?? data.class_id }}</template>
        </Column>
        <Column field="name" header="Section Name" sortable />
        <Column v-if="canEdit" :exportable="false" style="min-width:8rem">
          <template #body="slotProps">
            <Button icon="pi pi-pencil" text rounded severity="success" class="mr-2" @click="edit(slotProps.data)" />
          </template>
        </Column>
      </DataTable>
      <EmptyState v-else icon="pi pi-th-large" title="No sections found" description="Create a section to organize students within classes" />
    </div>

    <SectionFormDialog v-model:visible="dialogVisible" :edit-data="editingSection" @saved="fetchSections" />
  </div>
</template>
