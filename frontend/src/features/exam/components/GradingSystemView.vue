<script setup lang="ts">
import { ref, computed } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Tag from 'primevue/tag';
import Dialog from 'primevue/dialog';
import InputNumber from 'primevue/inputnumber';
import InputText from 'primevue/inputtext';
import type { GradingSystem, GradingRuleCreatePayload } from '../types/exam.types';
import { examApi } from '../api/exam.api';
import { usePermission } from '@/features/auth/composables/usePermission';

const props = defineProps<{
  gradingSystems: GradingSystem[];
}>();

const emit = defineEmits<{ 'refresh': [] }>();

const { hasPermission } = usePermission();
const canEdit = hasPermission('exam.grading.edit');
const canCreate = hasPermission('exam.grading.create');
const canDelete = hasPermission('exam.grading.delete');

const expandedRows = ref<(GradingSystem | null)[]>([]);
const ruleDialogVisible = ref(false);
const selectedSystem = ref<GradingSystem | null>(null);
const ruleLoading = ref(false);
const ruleError = ref('');
const ruleForm = ref<GradingRuleCreatePayload>({ min_marks: 0, max_marks: 0, grade: '', grade_point: 0, remarks: '' });

const openAddRule = (system: GradingSystem) => {
  selectedSystem.value = system;
  ruleForm.value = { min_marks: 0, max_marks: 0, grade: '', grade_point: 0, remarks: '' };
  ruleError.value = '';
  ruleDialogVisible.value = true;
};

const saveRule = async () => {
  if (!selectedSystem.value) return;
  ruleLoading.value = true;
  ruleError.value = '';
  try {
    await examApi.addGradingRule(selectedSystem.value.id, ruleForm.value);
    ruleDialogVisible.value = false;
    emit('refresh');
  } catch (err: any) {
    ruleError.value = err.response?.data?.message || 'Failed to add rule';
  } finally {
    ruleLoading.value = false;
  }
};

const removeSystem = async (id: number) => {
  if (!confirm('Delete this grading system?')) return;
  try { await examApi.deleteGradingSystem(id); emit('refresh'); } catch (e) { console.error(e); }
};
</script>

<template>
  <div class="ems-card">
    <DataTable v-if="gradingSystems.length" :value="gradingSystems" v-model:expandedRows="expandedRows" stripedRows>
      <Column expander style="width: 3rem" />
      <Column field="name" header="Name" sortable></Column>
      <Column header="Default" style="width: 8rem">
        <template #body="{ data }">
          <Tag v-if="data.is_default" severity="success" value="Default" />
          <Tag v-else severity="secondary" value="No" />
        </template>
      </Column>
      <Column header="Rules" style="width: 6rem">
        <template #body="{ data }">{{ data.rules?.length ?? 0 }}</template>
      </Column>
      <Column v-if="canEdit || canDelete" :exportable="false" style="min-width: 10rem">
        <template #body="{ data }">
          <Button v-if="canEdit" icon="pi pi-plus" text rounded severity="info" class="mr-1" @click="openAddRule(data)" title="Add Rule" />
          <Button v-if="canDelete" icon="pi pi-trash" text rounded severity="danger" @click="removeSystem(data.id)" />
        </template>
      </Column>
      <template #expansion="{ data }">
        <div class="p-3">
          <DataTable v-if="data.rules?.length" :value="data.rules" size="small" stripedRows>
            <Column field="grade" header="Grade" style="width: 6rem" />
            <Column field="grade_point" header="Point" style="width: 6rem" />
            <Column field="min_marks" header="Min" style="width: 6rem" />
            <Column field="max_marks" header="Max" style="width: 6rem" />
            <Column field="remarks" header="Remarks">
              <template #body="{ data: r }">{{ r.remarks || '—' }}</template>
            </Column>
          </DataTable>
          <p v-else class="text-surface-400 text-sm p-2">No rules defined yet.</p>
        </div>
      </template>
    </DataTable>
    <div v-else class="text-center p-4 text-surface-400">No grading systems found.</div>
  </div>

  <!-- Add Rule Dialog -->
  <Dialog v-model:visible="ruleDialogVisible" modal header="Add Grading Rule" :style="{ width: '28rem' }">
    <div v-if="ruleError" class="ems-error">{{ ruleError }}</div>
    <div class="flex flex-col gap-4">
      <div class="grid grid-cols-2 gap-4">
        <div class="ems-field">
          <label>Grade</label>
          <InputText v-model="ruleForm.grade" placeholder="A+" />
        </div>
        <div class="ems-field">
          <label>Grade Point</label>
          <InputNumber v-model="ruleForm.grade_point" :minFractionDigits="1" :maxFractionDigits="2" />
        </div>
      </div>
      <div class="grid grid-cols-2 gap-4">
        <div class="ems-field">
          <label>Min Marks</label>
          <InputNumber v-model="ruleForm.min_marks" :minFractionDigits="1" />
        </div>
        <div class="ems-field">
          <label>Max Marks</label>
          <InputNumber v-model="ruleForm.max_marks" :minFractionDigits="1" />
        </div>
      </div>
      <div class="ems-field">
        <label>Remarks</label>
        <InputText v-model="ruleForm.remarks" placeholder="Optional" />
      </div>
    </div>
    <template #footer>
      <Button label="Cancel" text severity="secondary" @click="ruleDialogVisible = false" />
      <Button label="Add Rule" icon="pi pi-check" @click="saveRule" :loading="ruleLoading" />
    </template>
  </Dialog>
</template>
