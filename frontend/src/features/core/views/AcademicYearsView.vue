<script setup lang="ts">
import { ref, onMounted } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Tag from 'primevue/tag';
import PageHeader from '@/components/shared/PageHeader.vue';
import EmptyState from '@/components/shared/EmptyState.vue';
import { academicYearApi } from '../api/academic-year.api';
import type { AcademicYear } from '../types/academic-year.types';
import AcademicYearFormDialog from '../components/AcademicYearFormDialog.vue';
import { usePermission } from '@/features/auth/composables/usePermission';

const { hasPermission } = usePermission();
const canEdit = hasPermission('core.academic_years.edit');
const canCreate = hasPermission('core.academic_years.create');
const canDelete = hasPermission('core.academic_years.delete');

const academicYears = ref<AcademicYear[]>([]);
const loading = ref(false);
const dialogVisible = ref(false);
const editingItem = ref<AcademicYear | null>(null);

const fetchAcademicYears = async () => {
  loading.value = true;
  try {
    const res = await academicYearApi.getAcademicYears(1, 100);
    academicYears.value = res.data.data?.items ?? [];
  } catch (e) { console.error(e); } finally { loading.value = false; }
};

onMounted(() => fetchAcademicYears());

const openNew = () => { editingItem.value = null; dialogVisible.value = true; };
const edit = (data: AcademicYear) => { editingItem.value = data; dialogVisible.value = true; };

const remove = async (id: number) => {
  if (!confirm('Delete this academic year?')) return;
  try { await academicYearApi.deleteAcademicYear(id); fetchAcademicYears(); } catch (e) { console.error(e); }
};
</script>

<template>
  <div>
    <PageHeader title="Academic Years" subtitle="Manage academic year periods" icon="pi pi-calendar-plus">
      <template #actions>
        <Button v-if="canCreate" label="Add Year" icon="pi pi-plus" @click="openNew" />
      </template>
    </PageHeader>

    <div class="card bg-surface-0 dark:bg-surface-900 p-4 rounded-xl shadow-sm border border-surface-200 dark:border-surface-800">
      <DataTable v-if="academicYears.length" :value="academicYears" :loading="loading" stripedRows responsiveLayout="scroll">
        <Column field="name" header="Name" sortable></Column>
        <Column field="start_date" header="Start Date" sortable></Column>
        <Column field="end_date" header="End Date" sortable></Column>
        <Column header="Status" style="width: 8rem">
          <template #body="{ data }">
            <Tag :severity="data.is_active ? 'success' : 'danger'" :value="data.is_active ? 'Active' : 'Inactive'" />
          </template>
        </Column>
        <Column v-if="canEdit || canDelete" :exportable="false" style="min-width:10rem">
          <template #body="{ data }">
            <Button v-if="canEdit" icon="pi pi-pencil" text rounded severity="success" class="mr-1" @click="edit(data)" />
            <Button v-if="canDelete" icon="pi pi-trash" text rounded severity="danger" @click="remove(data.id)" />
          </template>
        </Column>
      </DataTable>
      <EmptyState v-else icon="pi pi-calendar-plus" title="No academic years" description="Create your first academic year to get started" />
    </div>

    <AcademicYearFormDialog v-model:visible="dialogVisible" :edit-data="editingItem" @saved="fetchAcademicYears" />
  </div>
</template>
