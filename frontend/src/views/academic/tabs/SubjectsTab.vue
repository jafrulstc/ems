<script setup lang="ts">
import { computed } from 'vue';
import CrudTable from '../../../components/CrudTable.vue';
import { AcademicService } from '../../../services/academic.service';

const props = defineProps<{
  subjects: any[];
  loading: boolean;
}>();

const emit = defineEmits(['refresh']);

const subjectCols = computed(() => [
  { field: 'name', header: 'Subject Name' },
  { field: 'code', header: 'Code' },
]);
</script>

<template>
  <CrudTable 
    title="Subjects" 
    :rows="subjects" 
    :columns="subjectCols" 
    :loading="loading"
    :createFn="AcademicService.createSubject"
    :updateFn="AcademicService.updateSubject"
    :deleteFn="AcademicService.deleteSubject"
    @refresh="emit('refresh')" 
  />
</template>
