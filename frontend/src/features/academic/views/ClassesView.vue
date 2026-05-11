<script setup lang="ts">
import { ref, onMounted } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Tag from 'primevue/tag';
import PageHeader from '@/components/shared/PageHeader.vue';
import EmptyState from '@/components/shared/EmptyState.vue';
import { academicApi } from '../api/academic.api';
import type { AcademicClass } from '../types/academic.types';
import ClassFormDialog from '../components/ClassFormDialog.vue';
import { usePermission } from '@/features/auth/composables/usePermission';
import { useDisplayName } from '@/composables/useDisplayName';

const { hasPermission } = usePermission();
const { displayName } = useDisplayName();
const canEdit = hasPermission('academic.classes.edit');
const canCreate = hasPermission('academic.classes.create');

const classes = ref<AcademicClass[]>([]);
const loading = ref(false);
const dialogVisible = ref(false);
const editingClass = ref<AcademicClass | null>(null);

const fetchClasses = async () => {
  loading.value = true;
  try {
    const res = await academicApi.getClasses(1, 100);
    classes.value = res.data.data?.items ?? [];
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

onMounted(() => { fetchClasses(); });

const openNew = () => { editingClass.value = null; dialogVisible.value = true; };
const edit = (data: AcademicClass) => { editingClass.value = data; dialogVisible.value = true; };
</script>

<template>
  <div>
    <PageHeader title="Classes" subtitle="Manage academic classes and levels" icon="pi pi-bookmark">
      <template #actions>
        <Button v-if="canCreate" label="Add Class" icon="pi pi-plus" @click="openNew" />
      </template>
    </PageHeader>

    <div class="ems-card">
      <DataTable v-if="classes.length" :value="classes" :loading="loading" stripedRows responsiveLayout="scroll">
        <Column field="numeric_level" header="Level" sortable style="width: 15%">
          <template #body="{ data }">{{ data.numeric_level ?? '—' }}</template>
        </Column>
        <Column field="name" header="Name" sortable>
          <template #body="{ data }">{{ displayName(data.name, data.name_bn) }}</template>
        </Column>
        <Column header="Status" style="width: 15%">
          <template #body="{ data }">
            <Tag :severity="data.is_active ? 'success' : 'danger'" :value="data.is_active ? 'Active' : 'Inactive'" />
          </template>
        </Column>
        <Column v-if="canEdit" :exportable="false" style="min-width:8rem">
          <template #body="slotProps">
            <Button icon="pi pi-pencil" text rounded severity="success" class="mr-2" @click="edit(slotProps.data)" />
          </template>
        </Column>
      </DataTable>
      <EmptyState v-else icon="pi pi-bookmark" title="No classes found" description="Create your first class to get started" />
    </div>

    <ClassFormDialog v-model:visible="dialogVisible" :edit-data="editingClass" @saved="fetchClasses" />
  </div>
</template>
