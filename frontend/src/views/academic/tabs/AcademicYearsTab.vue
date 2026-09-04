<script setup lang="ts">
import CrudTable from '../../../components/CrudTable.vue';
import { AcademicService } from '../../../services/academic.service';

defineProps<{
  years: any[];
  loading: boolean;
}>();

const emit = defineEmits(['refresh']);

const yearCols = [
  { field: 'name', header: 'Year Name' },
  { field: 'start_date', header: 'Start Date', type: 'date' as const },
  { field: 'end_date', header: 'End Date', type: 'date' as const },
];
</script>

<template>
  <CrudTable 
    title="Academic Years" 
    :rows="years" 
    :columns="yearCols" 
    :loading="loading"
    :createFn="AcademicService.createYear"
    :updateFn="AcademicService.updateYear"
    :deleteFn="AcademicService.deleteYear"
    @refresh="emit('refresh')" 
  />
</template>
