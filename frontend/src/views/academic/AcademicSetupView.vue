<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { AcademicService } from '../../services/academic.service';
import { TenantService } from '../../services/tenant.service';
import Toast from 'primevue/toast';

import AcademicYearsTab from './tabs/AcademicYearsTab.vue';
import DepartmentsTab from './tabs/DepartmentsTab.vue';
import ClassesTab from './tabs/ClassesTab.vue';
import SectionsTab from './tabs/SectionsTab.vue';
import ShiftsTab from './tabs/ShiftsTab.vue';
import SubjectsTab from './tabs/SubjectsTab.vue';
import SubjectAssignsTab from './tabs/SubjectAssignsTab.vue';

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
      <AcademicYearsTab v-if="activeTab === 'years'" :years="years" :loading="loading" @refresh="load" />
      <DepartmentsTab v-if="activeTab === 'departments'" :departments="departments" :loading="loading" @refresh="load" />
      <ClassesTab v-if="activeTab === 'classes'" :classes="classes" :departments="departments" :loading="loading" @refresh="load" />
      <SectionsTab v-if="activeTab === 'sections'" :sections="sections" :branches="branches" :classes="classes" :shifts="shifts" :loading="loading" @refresh="load" />
      <ShiftsTab v-if="activeTab === 'shifts'" :shifts="shifts" :loading="loading" @refresh="load" />
      <SubjectAssignsTab v-if="activeTab === 'ycs'" :yearlyClassSubjects="yearlyClassSubjects" :years="years" :classes="classes" :subjects="subjects" :loading="loading" @refresh="load" />
      <SubjectsTab v-if="activeTab === 'subjects'" :subjects="subjects" :loading="loading" @refresh="load" />
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
</style>
