<script setup lang="ts">
import CrudTable from '../../../components/CrudTable.vue';
import { AcademicService } from '../../../services/academic.service';

defineProps<{
  shifts: any[];
  loading: boolean;
}>();

const emit = defineEmits(['refresh']);

const shiftCols = [
  { field: 'name', header: 'Shift Name' },
  { field: 'start_time', header: 'Start Time', type: 'time' as const },
  { field: 'end_time', header: 'End Time', type: 'time' as const },
];
</script>

<template>
  <CrudTable 
    title="Shifts" 
    :rows="shifts" 
    :columns="shiftCols" 
    :loading="loading"
    :createFn="AcademicService.createShift"
    :updateFn="AcademicService.updateShift"
    :deleteFn="AcademicService.deleteShift"
    @refresh="emit('refresh')" 
  />
</template>
