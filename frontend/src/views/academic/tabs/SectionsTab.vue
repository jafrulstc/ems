<script setup lang="ts">
import { computed } from 'vue';
import CrudTable from '../../../components/CrudTable.vue';
import { AcademicService } from '../../../services/academic.service';

const props = defineProps<{
  sections: any[];
  branches: any[];
  classes: any[];
  shifts: any[];
  loading: boolean;
}>();

const emit = defineEmits(['refresh']);

const branchOptions = computed(() => props.branches.map(b => ({ label: b.name, value: b.id })));
const classOptions = computed(() => props.classes.map(c => ({ label: c.name, value: c.id })));
const shiftOptions = computed(() => props.shifts.map(s => ({ label: s.name, value: s.id })));

const sectionCols = computed(() => [
  { field: 'name', header: 'Section Name' },
  { field: 'branch_id', header: 'Branch', type: 'select' as const, options: branchOptions.value },
  { field: 'class_id', header: 'Class', type: 'select' as const, options: classOptions.value },
  { field: 'shift_id', header: 'Shift', type: 'select' as const, options: shiftOptions.value },
]);
</script>

<template>
  <CrudTable 
    title="Sections" 
    :rows="sections" 
    :columns="sectionCols" 
    :loading="loading"
    :createFn="AcademicService.createSection"
    :updateFn="AcademicService.updateSection"
    :deleteFn="AcademicService.deleteSection"
    @refresh="emit('refresh')" 
  />
</template>
