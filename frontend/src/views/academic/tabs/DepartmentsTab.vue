<script setup lang="ts">
import CrudTable from '../../../components/CrudTable.vue';
import { AcademicService } from '../../../services/academic.service';

defineProps<{
  departments: any[];
  loading: boolean;
}>();

const emit = defineEmits(['refresh']);

const deptCols = [
  { field: 'name', header: 'Department Name' },
  { field: 'level', header: 'Academic Level (e.g., SSC, HSC, BSC)' },
];
</script>

<template>
  <CrudTable 
    title="Departments" 
    :rows="departments" 
    :columns="deptCols" 
    :loading="loading"
    :createFn="AcademicService.createDepartment"
    :updateFn="AcademicService.updateDepartment"
    :deleteFn="AcademicService.deleteDepartment"
    @refresh="emit('refresh')" 
  />
</template>
