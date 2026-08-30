<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { AcademicService } from '../../services/academic.service';
import { TenantService } from '../../services/tenant.service';
import CrudTable from '../../components/CrudTable.vue';
import Toast from 'primevue/toast';

const toast = useToast();
const activeTab = ref('years');

const years = ref<any[]>([]);
const departments = ref<any[]>([]);
const classes = ref<any[]>([]);
const sections = ref<any[]>([]);
const subjects = ref<any[]>([]);
const shifts = ref<any[]>([]);
const yearlyClassSubjects = ref<any[]>([]);
const branches = ref<any[]>([]);
const loading = ref(true);

const filterYearId = ref<string | null>(null);
const filterClassId = ref<string | null>(null);

const filteredYcs = computed(() => {
  return yearlyClassSubjects.value.filter(ycs => {
    if (filterYearId.value && ycs.academic_year_id !== filterYearId.value) return false;
    if (filterClassId.value && ycs.class_id !== filterClassId.value) return false;
    return true;
  });
});

const load = async () => {
  loading.value = true;
  try {
    [years.value, departments.value, classes.value, sections.value, subjects.value, shifts.value, yearlyClassSubjects.value, branches.value] = await Promise.all([
      AcademicService.getYears(),
      AcademicService.getDepartments(),
      AcademicService.getClasses(),
      AcademicService.getSections(),
      AcademicService.getSubjects(),
      AcademicService.getShifts(),
      AcademicService.getYearlyClassSubjects(),
      TenantService.getBranches(),
    ]);
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Load failed', life: 3000 });
  } finally {
    loading.value = false;
  }
};

onMounted(load);

const tabs = [
  { id: 'years', label: 'Academic Years', icon: 'pi pi-calendar' },
  { id: 'departments', label: 'Departments', icon: 'pi pi-building' },
  { id: 'shifts', label: 'Shifts', icon: 'pi pi-clock' },
  { id: 'classes', label: 'Classes', icon: 'pi pi-th-large' },
  { id: 'sections', label: 'Sections', icon: 'pi pi-list' },
  { id: 'subjects', label: 'Subjects', icon: 'pi pi-book' },
  { id: 'ycs', label: 'Subject Assigns', icon: 'pi pi-sitemap' },
];


const yearCols = [
  { field: 'name', header: 'Year Name' },
  { field: 'start_date', header: 'Start Date', type: 'date' as const },
  { field: 'end_date', header: 'End Date', type: 'date' as const },
];

const deptCols = [
  { field: 'name', header: 'Department Name' },
  { field: 'level', header: 'Academic Level (e.g., SSC, HSC, BSC)' },
];

const departmentOptions = computed(() => {
  return departments.value.map(d => ({ label: `${d.name} (${d.level || 'General'})`, value: d.id }));
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

const sectionCols = computed(() => [
  { field: 'name', header: 'Section Name' },
  { field: 'branch_id', header: 'Branch', type: 'select' as const, options: branchOptions.value },
  { field: 'class_id', header: 'Class', type: 'select' as const, options: classOptions.value },
  { field: 'shift_id', header: 'Shift', type: 'select' as const, options: shiftOptions.value },
]);

const subjectCols = computed(() => [
  { field: 'name', header: 'Subject Name' },
  { field: 'code', header: 'Code' },
]);

const shiftCols = [
  { field: 'name', header: 'Shift Name' },
  { field: 'start_time', header: 'Start Time' },
  { field: 'end_time', header: 'End Time' },
];

const yearOptions = computed(() => years.value.map(y => ({ label: y.name, value: y.id })));
const classOptions = computed(() => classes.value.map(c => ({ label: c.name, value: c.id })));
const shiftOptions = computed(() => shifts.value.map(s => ({ label: s.name, value: s.id })));
const branchOptions = computed(() => branches.value.map(b => ({ label: b.name, value: b.id })));
const subjectOptions = computed(() => subjects.value.map(s => ({ label: s.name, value: s.id })));

const ycsCols = computed(() => [
  { field: 'academic_year_id', header: 'Academic Year', type: 'select' as const, options: yearOptions.value },
  { field: 'class_id', header: 'Class', type: 'select' as const, options: classOptions.value },
  { field: 'subject_id', header: 'Subject', type: 'select' as const, options: subjectOptions.value },
  { field: 'is_main_subject', header: 'Is Main Subject?', type: 'boolean' as const },
  { field: 'affects_result_calculation', header: 'Affects Result?', type: 'boolean' as const },
]);
</script>

<template>
  <div class="page-container">
    <Toast />
    
    <div class="page-header">
      <div>
        <h1>Academic Setup</h1>
        <p>Configure academic years, departments, classes, sections, and subjects.</p>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="tabs-header">
      <button 
        v-for="t in tabs" 
        :key="t.id" 
        class="tab-btn" 
        :class="{ active: activeTab === t.id }" 
        @click="activeTab = t.id"
      >
        <i :class="t.icon"></i>
        <span>{{ t.label }}</span>
      </button>
    </div>

    <!-- Tab Content Panels -->
    <div class="tab-content">
      <div v-if="activeTab === 'years'">
        <CrudTable 
          title="Academic Years" 
          :rows="years" 
          :columns="yearCols" 
          :loading="loading"
          :createFn="AcademicService.createYear"
          :updateFn="AcademicService.updateYear"
          :deleteFn="AcademicService.deleteYear"
          @refresh="load" 
        />
      </div>

      <div v-if="activeTab === 'departments'">
        <CrudTable 
          title="Departments" 
          :rows="departments" 
          :columns="deptCols" 
          :loading="loading"
          :createFn="AcademicService.createDepartment"
          :updateFn="AcademicService.updateDepartment"
          :deleteFn="AcademicService.deleteDepartment"
          @refresh="load" 
        />
      </div>

      <div v-if="activeTab === 'classes'">
        <CrudTable 
          title="Classes" 
          :rows="classes" 
          :columns="classCols" 
          :loading="loading"
          :createFn="AcademicService.createClass"
          :updateFn="AcademicService.updateClass"
          :deleteFn="AcademicService.deleteClass"
          @refresh="load" 
        />
      </div>

      <div v-if="activeTab === 'sections'">
        <CrudTable 
          title="Sections" 
          :rows="sections" 
          :columns="sectionCols" 
          :loading="loading"
          :createFn="AcademicService.createSection"
          :updateFn="AcademicService.updateSection"
          :deleteFn="AcademicService.deleteSection"
          @refresh="load" 
        />
      </div>

      <div v-if="activeTab === 'shifts'">
        <CrudTable 
          title="Shifts" 
          :rows="shifts" 
          :columns="shiftCols" 
          :loading="loading"
          :createFn="AcademicService.createShift"
          :updateFn="AcademicService.updateShift"
          :deleteFn="AcademicService.deleteShift"
          @refresh="load" 
        />
      </div>

      <div v-if="activeTab === 'ycs'">
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
          @refresh="load" 
        />
      </div>

      <div v-if="activeTab === 'subjects'">
        <CrudTable 
          title="Subjects" 
          :rows="subjects" 
          :columns="subjectCols" 
          :loading="loading"
          :createFn="AcademicService.createSubject"
          :updateFn="AcademicService.updateSubject"
          :deleteFn="AcademicService.deleteSubject"
          @refresh="load" 
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-container { 
  display: flex; 
  flex-direction: column; 
  gap: 1.5rem; 
}
.page-header h1 { 
  font-size: 1.75rem; 
  font-weight: 700; 
  color: #102a43; 
  margin: 0 0 .25rem; 
}
.page-header p { 
  color: #627d98; 
  margin: 0; 
}

/* Tabs Styling */
.tabs-header {
  display: flex;
  gap: 0.5rem;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 2px;
}
.tab-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  border: none;
  background: transparent;
  color: #64748b;
  font-weight: 600;
  font-size: 0.95rem;
  border-radius: 8px 8px 0 0;
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 3px solid transparent;
}
.tab-btn:hover {
  color: #1e293b;
  background: #f8fafc;
}
.tab-btn.active {
  color: #2563eb;
  background: #eff6ff;
  border-bottom-color: #2563eb;
}
.tab-content {
  margin-top: 0.5rem;
}

/* Filter Card */
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
