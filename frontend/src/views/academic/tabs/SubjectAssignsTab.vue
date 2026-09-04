<script setup lang="ts">
import { ref, computed } from 'vue';
import CrudTable from '../../../components/CrudTable.vue';
import { AcademicService } from '../../../services/academic.service';

const props = defineProps<{
  yearlyClassSubjects: any[];
  years: any[];
  classes: any[];
  subjects: any[];
  loading: boolean;
}>();

const emit = defineEmits(['refresh']);

const filterYearId = ref<string | null>(null);
const filterClassId = ref<string | null>(null);

const filteredYcs = computed(() => {
  return props.yearlyClassSubjects.filter(ycs => {
    if (filterYearId.value && ycs.academic_year_id !== filterYearId.value) return false;
    if (filterClassId.value && ycs.class_id !== filterClassId.value) return false;
    return true;
  });
});

const yearOptions = computed(() => props.years.map(y => ({ label: y.name, value: y.id })));
const classOptions = computed(() => props.classes.map(c => ({ label: c.name, value: c.id })));

const ycsCols = computed(() => [
  { field: 'academic_year_id', header: 'Academic Year', type: 'select' as const, options: yearOptions.value },
  { field: 'class_id', header: 'Class', type: 'select' as const, options: classOptions.value },
  { 
    field: 'subject_id', 
    header: 'Subject', 
    type: 'select' as const, 
    options: (form: any) => {
      // If year or class is not selected, return empty or all subjects
      if (!form.academic_year_id || !form.class_id) return [];
      
      // Find subjects that are already assigned to this year and class,
      // excluding the current one being edited
      const assignedSubjectIds = props.yearlyClassSubjects
        .filter(ycs => ycs.academic_year_id === form.academic_year_id && ycs.class_id === form.class_id && ycs.id !== form.id)
        .map(ycs => ycs.subject_id);
        
      return props.subjects
        .filter(s => !assignedSubjectIds.includes(s.id))
        .map(s => ({ label: `${s.name} (${s.code})`, value: s.id }));
    }
  },
  { field: 'is_main_subject', header: 'Is Main Subject?', type: 'boolean' as const },
  { field: 'affects_result_calculation', header: 'Affects Result?', type: 'boolean' as const },
]);
</script>

<template>
  <div>
    <div class="filter-card">
      <div class="filter-group">
        <label>Filter by Academic Year</label>
        <select v-model="filterYearId" class="custom-select">
          <option :value="null">-- All Years --</option>
          <option v-for="y in years" :key="y.id" :value="y.id">{{ y.name }}</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Filter by Class</label>
        <select v-model="filterClassId" class="custom-select">
          <option :value="null">-- All Classes --</option>
          <option v-for="c in classes" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>
    </div>

    <CrudTable 
      title="Yearly Class Subjects" 
      :rows="filteredYcs" 
      :columns="ycsCols" 
      :loading="loading"
      :createFn="AcademicService.createYearlyClassSubject"
      :updateFn="AcademicService.updateYearlyClassSubject"
      :deleteFn="AcademicService.deleteYearlyClassSubject"
      @refresh="emit('refresh')" 
    />
  </div>
</template>

<style scoped>
.filter-card {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  background: white;
  padding: 1.25rem;
  border-radius: 12px;
  border: 1px solid #f0f4f8;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
}
.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
  min-width: 200px;
}
.filter-group label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #475569;
}
.custom-select {
  width: 100%;
  padding: 0.6rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.9rem;
  background: #fff;
  color: #1e293b;
  outline: none;
  transition: border-color 0.2s ease;
}
.custom-select:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}
</style>
