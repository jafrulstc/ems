<script setup lang="ts">
import { ref, computed } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import InputNumber from 'primevue/inputnumber';
import Checkbox from 'primevue/checkbox';
import Tag from 'primevue/tag';
import type { Mark, MarkEntry, MarkBulkCreatePayload } from '../types/exam.types';
import { examApi } from '../api/exam.api';

const props = defineProps<{
  existingMarks: Mark[];
  examTypeId: number;
  classSubjectId: number;
}>();

const emit = defineEmits<{
  'saved': [];
}>();

const loading = ref(false);
const errorMsg = ref('');

const entries = ref<Map<number, { marks_obtained: number | null; is_absent: boolean }>>(new Map());

const initEntries = () => {
  const map = new Map<number, { marks_obtained: number | null; is_absent: boolean }>();
  for (const m of props.existingMarks) {
    map.set(m.enrollment_id, { marks_obtained: m.marks_obtained ?? null, is_absent: m.is_absent });
  }
  entries.value = map;
};

initEntries();

const rows = computed(() => {
  const seen = new Set<number>();
  const result: { enrollment_id: number; marks_obtained: number | null; is_absent: boolean }[] = [];
  for (const m of props.existingMarks) {
    if (!seen.has(m.enrollment_id)) {
      seen.add(m.enrollment_id);
      const entry = entries.value.get(m.enrollment_id) ?? { marks_obtained: null, is_absent: false };
      result.push({ enrollment_id: m.enrollment_id, marks_obtained: entry.marks_obtained, is_absent: entry.is_absent });
    }
  }
  return result;
});

const updateEntry = (enrollmentId: number, field: 'marks_obtained' | 'is_absent', value: number | null | boolean) => {
  const existing = entries.value.get(enrollmentId) ?? { marks_obtained: null, is_absent: false };
  entries.value.set(enrollmentId, { ...existing, [field]: value });
};

const save = async () => {
  loading.value = true;
  errorMsg.value = '';
  try {
    const bulkEntries: MarkEntry[] = [];
    for (const [enrollmentId, entry] of entries.value) {
      bulkEntries.push({
        enrollment_id: enrollmentId,
        class_subject_id: props.classSubjectId,
        marks_obtained: entry.is_absent ? null : entry.marks_obtained,
        is_absent: entry.is_absent,
      });
    }
    const payload: MarkBulkCreatePayload = {
      exam_type_id: props.examTypeId,
      entries: bulkEntries,
    };
    await examApi.bulkCreateMarks(payload);
    emit('saved');
  } catch (err: any) {
    errorMsg.value = err.response?.data?.message || 'Failed to save marks';
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div>
    <div v-if="errorMsg" class="p-3 bg-red-50 dark:bg-red-950 text-red-600 dark:text-red-400 rounded-lg text-sm mb-4">
      {{ errorMsg }}
    </div>

    <DataTable v-if="rows.length" :value="rows" stripedRows responsiveLayout="scroll">
      <Column header="Enrollment ID" field="enrollment_id" style="width: 25%" />
      <Column header="Marks Obtained" style="width: 40%">
        <template #body="{ data }">
          <InputNumber
            v-model="data.marks_obtained"
            :disabled="data.is_absent"
            :min="0"
            :max="100"
            placeholder="Enter marks"
            class="w-full"
            @input="updateEntry(data.enrollment_id, 'marks_obtained', ($event.value as number | null) ?? null)"
          />
        </template>
      </Column>
      <Column header="Absent" style="width: 20%">
        <template #body="{ data }">
          <Checkbox v-model="data.is_absent" :binary="true" @change="updateEntry(data.enrollment_id, 'is_absent', data.is_absent)" />
        </template>
      </Column>
      <Column header="Status" style="width: 15%">
        <template #body="{ data }">
          <Tag v-if="data.is_absent" severity="danger" value="Absent" />
          <Tag v-else-if="data.marks_obtained !== null" severity="success" value="Marked" />
          <Tag v-else severity="secondary" value="Pending" />
        </template>
      </Column>
    </DataTable>
    <div v-else class="text-center p-8 text-surface-400">No students found for this subject.</div>

    <div class="flex justify-end gap-2 mt-4" v-if="rows.length">
      <Button label="Save Marks" icon="pi pi-check" @click="save" :loading="loading" />
    </div>
  </div>
</template>
