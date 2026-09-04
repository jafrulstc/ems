<script setup lang="ts">
import { computed } from 'vue';
import CrudTable from '../../../components/CrudTable.vue';
import { AcademicService } from '../../../services/academic.service';

const props = defineProps<{
  classes: any[];
  departments: any[];
  loading: boolean;
}>();

const emit = defineEmits(['refresh']);

const departmentOptions = computed(() => {
  return props.departments.map(d => ({ label: `${d.name} (${d.level || 'General'})`, value: d.id }));
});

const classCols = computed(() => [
  { field: 'name', header: 'Class Name' },
  { field: 'level', header: 'Level (e.g. SSC, HSC, BSC)' },
  {
    field: 'department_id',
    displayField: 'department_name',
    header: 'Department',
    type: 'select' as const,
    options: departmentOptions.value
  },
]);
</script>

<template>
  <CrudTable 
    title="Classes" 
    :rows="classes" 
    :columns="classCols" 
    :loading="loading"
    :createFn="AcademicService.createClass"
    :updateFn="AcademicService.updateClass"
    :deleteFn="AcademicService.deleteClass"
    @refresh="emit('refresh')" 
  />
</template>
