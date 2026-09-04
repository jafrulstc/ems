<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import { StudentService } from '../../services/student.service';
import { AcademicService } from '../../services/academic.service';
import { TenantService } from '../../services/tenant.service';
import CrudTable from '../../components/CrudTable.vue';
import Toast from 'primevue/toast';

const toast = useToast();
const activeTab = ref('students');

const students = ref<any[]>([]);
const guardians = ref<any[]>([]);
const enrollments = ref<any[]>([]);
const academicYears = ref<any[]>([]);
const classes = ref<any[]>([]);
const sections = ref<any[]>([]);
const branches = ref<any[]>([]);
const loading = ref(true);

const filterYearId = ref<string | null>(null);
const filterClassId = ref<string | null>(null);

const filteredEnrollments = computed(() => {
  return enrollments.value.filter(e => {
    if (filterYearId.value && e.academic_year_id !== filterYearId.value) return false;
    if (filterClassId.value && e.class_id !== filterClassId.value) return false;
    return true;
  });
});

const load = async () => {
  loading.value = true;
  try {
    const [st, gu, en, yr, cl, se, br] = await Promise.all([
      StudentService.getStudents(),
      StudentService.getGuardians(),
      StudentService.getEnrollments(),
      AcademicService.getYears().catch(() => []),
      AcademicService.getClasses().catch(() => []),
      AcademicService.getSections().catch(() => []),
      TenantService.getBranches().catch(() => []),
    ]);
    students.value = st;
    guardians.value = gu;
    enrollments.value = en;
    academicYears.value = yr;
    classes.value = cl;
    sections.value = se;
    branches.value = br;
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Load failed', life: 3000 });
  } finally {
    loading.value = false;
  }
};

onMounted(load);

const tabs = [
  { id: 'students', label: 'Students', icon: 'pi pi-users' },
  { id: 'guardians', label: 'Guardians', icon: 'pi pi-user' },
  { id: 'enrollments', label: 'Enrollments', icon: 'pi pi-id-card' },
];

const yearOptions = computed(() => academicYears.value.map(y => ({ label: y.name, value: y.id })));
const classOptions = computed(() => classes.value.map(c => ({ label: c.name, value: c.id })));
const sectionOptions = computed(() => sections.value.map(s => ({ label: s.name, value: s.id })));
const branchOptions = computed(() => branches.value.map(b => ({ label: b.name, value: b.id })));
const guardianOptions = computed(() => guardians.value.map(g => ({ label: `${g.name} (${g.phone})`, value: g.id })));
const studentOptions = computed(() => students.value.map(s => ({ label: `${s.student_id_no ? s.student_id_no + ' - ' : ''}${s.first_name} ${s.last_name}`, value: s.id })));

const statusOptions = [
  { label: 'Active', value: 'active' },
  { label: 'Inactive', value: 'inactive' },
  { label: 'Graduated', value: 'graduated' },
  { label: 'Transferred', value: 'transferred' },
  { label: 'Dropped Out', value: 'dropped_out' },
];

const studentCols = computed(() => [
  { field: 'student_id_no', header: 'Student ID No.', type: 'number' as const, required: true },
  { field: 'first_name', header: 'First Name', required: true },
  { field: 'last_name', header: 'Last Name', required: true },
  { field: 'branch_id', header: 'Branch', type: 'select' as const, options: branchOptions.value, required: true },
  { field: 'guardian_id', header: 'Guardian', type: 'select' as const, options: guardianOptions.value },
  { field: 'gender', header: 'Gender', type: 'select' as const, options: [{label: 'Male', value: 'Male'}, {label: 'Female', value: 'Female'}, {label: 'Other', value: 'Other'}], required: true },
  { field: 'date_of_birth', header: 'Date of Birth', type: 'date' as const, required: true },
  { field: 'blood_group', header: 'Blood Group' },
]);

const guardianCols = computed(() => [
  { field: 'name', header: 'Guardian Name', required: true },
  { field: 'phone', header: 'Phone', required: true },
  { field: 'email', header: 'Email' },
]);

const enrollmentCols = computed(() => [
  { field: 'academic_year_id', header: 'Academic Year', type: 'select' as const, options: yearOptions.value, required: true },
  { 
    field: 'student_id', 
    header: 'Student', 
    type: 'select' as const, 
    options: (form: any) => {
      if (!form.academic_year_id) return []; // Empty until academic year is selected
      // Find students already enrolled in the selected academic year, excluding the current enrollment being edited
      const enrolledStudentIds = enrollments.value
        .filter(e => e.academic_year_id === form.academic_year_id && e.id !== form.id)
        .map(e => e.student_id);
      return studentOptions.value.filter(opt => !enrolledStudentIds.includes(opt.value));
    }, 
    required: true 
  },
  { field: 'branch_id', header: 'Branch', type: 'select' as const, options: branchOptions.value, required: true },
  { field: 'class_id', header: 'Class', type: 'select' as const, options: classOptions.value, required: true },
  { field: 'section_id', header: 'Section', type: 'select' as const, options: sectionOptions.value },
  { field: 'roll_number', header: 'Roll No.' },
  { field: 'enrollment_date', header: 'Enrollment Date', type: 'date' as const, required: true },
  { field: 'status', header: 'Status', type: 'select' as const, options: statusOptions, required: true },
]);
</script>

<template>
  <div class="page-container">
    <Toast />
    
    <div class="page-header">
      <div>
        <h1>Student Management</h1>
        <p>Manage students, guardians, and enrollments.</p>
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
      <div v-if="activeTab === 'students'">
        <CrudTable 
          title="Students" 
          :rows="students" 
          :columns="studentCols" 
          :loading="loading"
          :createFn="StudentService.createStudent"
          :updateFn="StudentService.updateStudent"
          :deleteFn="StudentService.deleteStudent"
          @refresh="load" 
        />
      </div>

      <div v-if="activeTab === 'guardians'">
        <CrudTable 
          title="Guardians" 
          :rows="guardians" 
          :columns="guardianCols" 
          :loading="loading"
          :createFn="StudentService.createGuardian"
          :updateFn="StudentService.updateGuardian"
          :deleteFn="StudentService.deleteGuardian"
          @refresh="load" 
        />
      </div>

      <div v-if="activeTab === 'enrollments'">
        <div class="filter-card">
          <div class="filter-group">
            <label>Filter by Academic Year</label>
            <select v-model="filterYearId" class="custom-select">
              <option :value="null">-- All Years --</option>
              <option v-for="y in academicYears" :key="y.id" :value="y.id">{{ y.name }}</option>
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
          title="Enrollments" 
          :rows="filteredEnrollments" 
          :columns="enrollmentCols" 
          :loading="loading"
          :createFn="StudentService.createEnrollment"
          :updateFn="StudentService.updateEnrollment"
          :deleteFn="StudentService.deleteEnrollment"
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
</style>
