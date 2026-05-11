<script setup lang="ts">
import { ref, onMounted } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Tag from 'primevue/tag';
import PageHeader from '@/components/shared/PageHeader.vue';
import EmptyState from '@/components/shared/EmptyState.vue';
import { academicApi } from '../api/academic.api';
import type { Subject } from '../types/academic.types';
import SubjectFormDialog from '../components/SubjectFormDialog.vue';
import { usePermission } from '@/features/auth/composables/usePermission';

const { hasPermission } = usePermission();
const canEdit = hasPermission('academic.subjects.edit');
const canCreate = hasPermission('academic.subjects.create');

const subjects = ref<Subject[]>([]);
const loading = ref(false);
const dialogVisible = ref(false);
const editingSubject = ref<Subject | null>(null);

const fetchSubjects = async () => {
  loading.value = true;
  try {
    const res = await academicApi.getSubjects(1, 100);
    subjects.value = res.data.data?.items ?? [];
  } catch (e) { console.error(e); } finally { loading.value = false; }
};

onMounted(() => { fetchSubjects(); });
const openNew = () => { editingSubject.value = null; dialogVisible.value = true; };
const edit = (data: Subject) => { editingSubject.value = data; dialogVisible.value = true; };
</script>

<template>
  <div>
    <PageHeader title="Subjects" subtitle="Manage academic subjects" icon="pi pi-book">
      <template #actions>
        <Button v-if="canCreate" label="Add Subject" icon="pi pi-plus" @click="openNew" />
      </template>
    </PageHeader>

    <div class="ems-card">
      <DataTable v-if="subjects.length" :value="subjects" :loading="loading" stripedRows responsiveLayout="scroll">
        <Column field="code" header="Code" sortable style="width: 15%">
          <template #body="{ data }">{{ data.code ?? '—' }}</template>
        </Column>
        <Column field="name" header="Subject Name" sortable />
        <Column header="Type" style="width: 15%">
          <template #body="{ data }">
            <Tag :severity="data.is_optional ? 'info' : 'danger'" :value="data.is_optional ? 'Optional' : 'Mandatory'" />
          </template>
        </Column>
        <Column v-if="canEdit" :exportable="false" style="min-width:8rem">
          <template #body="slotProps">
            <Button icon="pi pi-pencil" text rounded severity="success" class="mr-2" @click="edit(slotProps.data)" />
          </template>
        </Column>
      </DataTable>
      <EmptyState v-else icon="pi pi-book" title="No subjects found" description="Create your first subject to get started" />
    </div>

    <SubjectFormDialog v-model:visible="dialogVisible" :edit-data="editingSubject" @saved="fetchSubjects" />
  </div>
</template>
