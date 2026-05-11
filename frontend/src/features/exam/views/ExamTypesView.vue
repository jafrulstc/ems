<script setup lang="ts">
import { ref, onMounted } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Tag from 'primevue/tag';
import PageHeader from '@/components/shared/PageHeader.vue';
import EmptyState from '@/components/shared/EmptyState.vue';
import { examApi } from '../api/exam.api';
import type { ExamType, GradingSystem } from '../types/exam.types';
import ExamTypeFormDialog from '../components/ExamTypeFormDialog.vue';
import GradingSystemView from '../components/GradingSystemView.vue';
import { usePermission } from '@/features/auth/composables/usePermission';
import { useDisplayName } from '@/composables/useDisplayName';

const { hasPermission } = usePermission();
const { displayName } = useDisplayName();
const canEdit = hasPermission('exam.exam_types.edit');
const canCreate = hasPermission('exam.exam_types.create');

const examTypes = ref<ExamType[]>([]);
const gradingSystems = ref<GradingSystem[]>([]);
const loading = ref(false);
const activeTab = ref<'types' | 'grading'>('types');

const dialogVisible = ref(false);
const editingItem = ref<ExamType | null>(null);

const fetchExamTypes = async () => {
  loading.value = true;
  try {
    const res = await examApi.getExamTypes(1, 100);
    examTypes.value = res.data.data?.items ?? [];
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const fetchGradingSystems = async () => {
  try {
    const res = await examApi.getGradingSystems(1, 100);
    gradingSystems.value = res.data.data?.items ?? [];
  } catch (e) {
    console.error(e);
  }
};

onMounted(() => {
  fetchExamTypes();
  fetchGradingSystems();
});

const openNew = () => {
  editingItem.value = null;
  dialogVisible.value = true;
};

const edit = (data: ExamType) => {
  editingItem.value = data;
  dialogVisible.value = true;
};

const remove = async (id: number) => {
  if (!confirm('Delete this exam type?')) return;
  try {
    await examApi.deleteExamType(id);
    fetchExamTypes();
  } catch (e) {
    console.error(e);
  }
};
</script>

<template>
  <div>
    <PageHeader title="Exam Configuration" subtitle="Manage exam types and grading systems" icon="pi pi-cog">
      <template #actions>
        <Button v-if="canCreate && activeTab === 'types'" label="Add Exam Type" icon="pi pi-plus" @click="openNew" />
      </template>
    </PageHeader>

    <div class="flex gap-2 mb-4">
      <Button
        :label="'Exam Types (' + examTypes.length + ')'"
        :severity="activeTab === 'types' ? undefined : 'secondary'"
        size="small"
        @click="activeTab = 'types'"
      />
      <Button
        :label="'Grading Systems (' + gradingSystems.length + ')'"
        :severity="activeTab === 'grading' ? undefined : 'secondary'"
        size="small"
        @click="activeTab = 'grading'"
      />
    </div>

    <!-- Exam Types Tab -->
    <div v-if="activeTab === 'types'" class="ems-card">
      <DataTable v-if="examTypes.length" :value="examTypes" :loading="loading" stripedRows responsiveLayout="scroll">
        <Column field="name" header="Name" sortable>
          <template #body="{ data }">{{ displayName(data.name, data.name_bn) }}</template>
        </Column>
        <Column field="description" header="Description" sortable>
          <template #body="{ data }">
            {{ data.description || '—' }}
          </template>
        </Column>
        <Column v-if="canEdit" :exportable="false" style="min-width:10rem">
          <template #body="{ data }">
            <Button icon="pi pi-pencil" text rounded severity="success" class="mr-1" @click="edit(data)" />
            <Button icon="pi pi-trash" text rounded severity="danger" @click="remove(data.id)" />
          </template>
        </Column>
      </DataTable>
      <EmptyState v-else icon="pi pi-bookmark" title="No exam types" description="Create your first exam type to get started" />
    </div>

    <!-- Grading Systems Tab -->
    <GradingSystemView v-if="activeTab === 'grading'" :grading-systems="gradingSystems" @refresh="fetchGradingSystems" />

    <ExamTypeFormDialog
      v-model:visible="dialogVisible"
      :edit-data="editingItem"
      @saved="fetchExamTypes"
    />
  </div>
</template>
