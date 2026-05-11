<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dropdown from 'primevue/dropdown';
import PageHeader from '@/components/shared/PageHeader.vue';
import EmptyState from '@/components/shared/EmptyState.vue';
import { academicApi } from '../api/academic.api';
import type { ClassSubject, AcademicClass, Subject } from '../types/academic.types';
import ClassSubjectFormDialog from '../components/ClassSubjectFormDialog.vue';
import { usePermission } from '@/features/auth/composables/usePermission';
import { useDisplayName } from '@/composables/useDisplayName';

const { hasPermission } = usePermission();
const { displayName } = useDisplayName();
const canEdit = hasPermission('academic.class_subjects.edit');
const canCreate = hasPermission('academic.class_subjects.create');
const canDelete = hasPermission('academic.class_subjects.delete');

const classSubjects = ref<ClassSubject[]>([]);
const classes = ref<AcademicClass[]>([]);
const subjects = ref<Subject[]>([]);
const selectedClass = ref<number | null>(null);
const loading = ref(false);
const dialogVisible = ref(false);
const editingItem = ref<ClassSubject | null>(null);

const classMap = computed(() => {
  const map = new Map<number, string>();
  for (const c of classes.value) map.set(c.id, displayName(c.name, c.name_bn));
  return map;
});

const subjectMap = computed(() => {
  const map = new Map<number, string>();
  for (const s of subjects.value) map.set(s.id, displayName(s.name, s.name_bn));
  return map;
});

const classOptions = computed(() => classes.value.map(c => ({ ...c, displayName: displayName(c.name, c.name_bn) })));

const fetchClasses = async () => {
  try {
    const res = await academicApi.getClasses(1, 100);
    classes.value = res.data.data?.items ?? [];
  } catch (e) { console.error(e); }
};

const fetchSubjects = async () => {
  try {
    const res = await academicApi.getSubjects(1, 100);
    subjects.value = res.data.data?.items ?? [];
  } catch (e) { console.error(e); }
};

const fetchClassSubjects = async () => {
  loading.value = true;
  try {
    const res = await academicApi.getClassSubjects(1, 100);
    classSubjects.value = res.data.data?.items ?? [];
  } catch (e) { console.error(e); } finally { loading.value = false; }
};

onMounted(() => { fetchClasses(); fetchSubjects(); fetchClassSubjects(); });

const filtered = computed(() =>
  selectedClass.value ? classSubjects.value.filter(cs => cs.class_id === selectedClass.value) : classSubjects.value
);

const onClassFilterChange = () => {};
const openNew = () => { editingItem.value = null; dialogVisible.value = true; };
const edit = (data: ClassSubject) => { editingItem.value = data; dialogVisible.value = true; };
const remove = async (id: number) => {
  if (!confirm('Delete this mapping?')) return;
  try { await academicApi.deleteClassSubject(id); fetchClassSubjects(); } catch (e) { console.error(e); }
};
</script>

<template>
  <div>
    <PageHeader title="Class Subjects" subtitle="Map subjects to classes with marks configuration" icon="pi pi-sitemap">
      <template #actions>
        <Button v-if="canCreate" label="Add Mapping" icon="pi pi-plus" @click="openNew" />
      </template>
    </PageHeader>

    <div class="ems-card">
      <div class="mb-4">
        <Dropdown v-model="selectedClass" :options="classOptions" optionLabel="displayName" optionValue="id"
          placeholder="Filter by Class" showClear @change="onClassFilterChange" class="w-full md:w-14rem" />
      </div>
      <DataTable v-if="filtered.length" :value="filtered" :loading="loading" stripedRows responsiveLayout="scroll">
        <Column header="Class Name" sortable style="width: 25%">
          <template #body="{ data }">{{ classMap.get(data.class_id) ?? data.class_name ?? data.class_id }}</template>
        </Column>
        <Column header="Subject Name" sortable style="width: 25%">
          <template #body="{ data }">{{ subjectMap.get(data.subject_id) ?? data.subject_name ?? data.subject_id }}</template>
        </Column>
        <Column field="full_marks" header="Full Marks" sortable style="width: 15%" />
        <Column field="pass_marks" header="Pass Marks" sortable style="width: 15%" />
        <Column v-if="canEdit || canDelete" :exportable="false" style="min-width:8rem">
          <template #body="{ data }">
            <Button v-if="canEdit" icon="pi pi-pencil" text rounded severity="success" class="mr-2" @click="edit(data)" />
            <Button v-if="canDelete" icon="pi pi-trash" text rounded severity="danger" @click="remove(data.id)" />
          </template>
        </Column>
      </DataTable>
      <EmptyState v-else icon="pi pi-sitemap" title="No class-subject mappings found" description="Map subjects to classes to configure marks" />
    </div>

    <ClassSubjectFormDialog v-model:visible="dialogVisible" :edit-data="editingItem" @saved="fetchClassSubjects" />
  </div>
</template>
