<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import { ExamService } from '../../services/exam.service';
import { AcademicService } from '../../services/academic.service';
import { StudentService } from '../../services/student.service';
import CrudTable from '../../components/CrudTable.vue';
import Toast from 'primevue/toast';
import Button from 'primevue/button';
import InputNumber from 'primevue/inputnumber';
import TabView from 'primevue/tabview';
import TabPanel from 'primevue/tabpanel';
import ExamReportView from './ExamReportView.vue';
import MarksheetView from './MarksheetView.vue';

const toast = useToast();
const activeTab = ref('types');

const exams = ref<any[]>([]);
const schedules = ref<any[]>([]);

const gradingScales = ref<any[]>([]);
const examTypes = ref<any[]>([]);
const subjects = ref<any[]>([]);
const students = ref<any[]>([]);
const enrollments = ref<any[]>([]);
const academicYears = ref<any[]>([]);
const yearlyClassSubjects = ref<any[]>([]);
const classes = ref<any[]>([]);

const loading = ref(true);
const markEntryLoading = ref(false);

const selectedYearId = ref<string | null>(null);
const selectedExamId = ref<string | null>(null);
const selectedClassId = ref<string | null>(null);
const selectedScheduleId = ref<string | null>(null);
const filteredResults = ref<any[]>([]);

const examFilterYearId = ref<string | null>(null);
const filteredExams = computed(() => {
  if (!examFilterYearId.value) return exams.value;
  return exams.value.filter(e => e.academic_year_id === examFilterYearId.value);
});

const scheduleFilterYearId = ref<string | null>(null);
const scheduleFilterClassId = ref<string | null>(null);
const filteredSchedules = computed(() => {
  return schedules.value.filter(s => {
    if (scheduleFilterClassId.value && s.class_id !== scheduleFilterClassId.value) {
      return false;
    }
    if (scheduleFilterYearId.value) {
      const exam = exams.value.find(e => e.id === s.exam_id);
      if (!exam || exam.academic_year_id !== scheduleFilterYearId.value) {
        return false;
      }
    }
    return true;
  });
});

const load = async () => {
  loading.value = true;
  try {
    const [examsData, schedulesData, scalesData, typesData, subjectsData, studentsData, enrollmentsData, yearsData, ycsData, classesData] = await Promise.all([
      ExamService.getExams({fetch_all: true}).then(r => r.items),
      ExamService.getSchedules({fetch_all: true}).then(r => r.items),
      ExamService.getGradingScales({fetch_all: true}).then(r => r.items),
      ExamService.getExamTypes({fetch_all: true}).then(r => r.items),
      AcademicService.getSubjects({fetch_all: true}).then(r => r.items).catch(() => []),
      StudentService.getStudents({fetch_all: true}).then(r => r.items).catch(() => []),
      StudentService.getEnrollments({fetch_all: true}).then(r => r.items).catch(() => []),
      AcademicService.getYears({fetch_all: true}).then(r => r.items).catch(() => []),
      AcademicService.getYearlyClassSubjects({fetch_all: true}).then(r => r.items).catch(() => []),
      AcademicService.getClasses({fetch_all: true}).then(r => r.items).catch(() => []),
    ]);

    exams.value = examsData;
    schedules.value = schedulesData;
    gradingScales.value = scalesData;
    examTypes.value = typesData;
    subjects.value = subjectsData;
    students.value = studentsData;
    enrollments.value = enrollmentsData;
    academicYears.value = yearsData;
    yearlyClassSubjects.value = ycsData;
    classes.value = classesData;

    if (selectedScheduleId.value) {
      await loadMarks();
    }
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Load failed', life: 3000 });
  } finally {
    loading.value = false;
  }
};

onMounted(load);

const tabs = [
  { id: 'types', label: 'Exam Types', icon: 'pi pi-tags' },
  { id: 'exams', label: 'Exams', icon: 'pi pi-file-edit' },
  { id: 'grading', label: 'Grading Scales', icon: 'pi pi-chart-bar' },
  { id: 'schedules', label: 'Exam Schedules', icon: 'pi pi-calendar-plus' },
  { id: 'mark-entry', label: 'Mark Entry', icon: 'pi pi-check-square' },
  { id: 'reports', label: 'Reports', icon: 'pi pi-chart-line' },
];

const examTypeOptions = computed(() => examTypes.value.map(t => ({ label: t.name, value: t.id })));
const examOptions = computed(() => exams.value.map(e => ({ label: e.name, value: e.id })));
const subjectOptions = computed(() => subjects.value.map(s => ({ label: `${s.name} ${s.code ? `(${s.code})` : ''}`, value: s.id })));
const academicYearOptions = computed(() => academicYears.value.map(y => ({ label: y.name, value: y.id })));
const classOptions = computed(() => classes.value.map(c => ({ label: c.name, value: c.id })));

const dynamicSubjectOptions = (form: any) => {
  if (!form.exam_id || !form.class_id) return subjectOptions.value;
  
  const exam = exams.value.find(e => e.id === form.exam_id);
  if (!exam) return subjectOptions.value;

  const validYcs = yearlyClassSubjects.value.filter(ycs => 
    ycs.academic_year_id === exam.academic_year_id && ycs.class_id === form.class_id
  );
  
  const validSubjectIds = new Set(validYcs.map(ycs => ycs.subject_id));
  return subjectOptions.value.filter(opt => validSubjectIds.has(opt.value));
};

const examCols = computed(() => [
  { field: 'name', header: 'Exam Name', required: true },
  { field: 'academic_year_id', header: 'Academic Year', type: 'select' as const, options: academicYearOptions.value, required: true },
  { field: 'exam_type_id', header: 'Exam Type', type: 'select' as const, options: examTypeOptions.value, required: true },
  { field: 'start_date', header: 'Start Date', type: 'date' as const, required: true },
  { field: 'end_date', header: 'End Date', type: 'date' as const, required: true },
]);

const typeCols = [
  { field: 'name', header: 'Type Name' },
];

const scheduleCols = computed(() => [
  { field: 'exam_id', header: 'Exam', type: 'select' as const, options: examOptions.value, required: true },
  { field: 'class_id', header: 'Class', type: 'select' as const, options: classOptions.value, required: true },
  { field: 'subject_id', header: 'Subject', type: 'select' as const, options: dynamicSubjectOptions, required: true },
  { field: 'exam_date', header: 'Exam Date', type: 'date' as const, required: true },
  { field: 'start_time', header: 'Start Time', type: 'time' as const },
  { field: 'end_time', header: 'End Time', type: 'time' as const },
  { field: 'full_marks', header: 'Full Marks', type: 'number' as const, defaultValue: 100 },
  { field: 'pass_marks', header: 'Pass Marks', type: 'number' as const, defaultValue: 33 },
]);

const gradingCols = [
  { field: 'grade_name', header: 'Grade Name' },
  { field: 'min_marks', header: 'Min Marks (%)', type: 'number' as const },
  { field: 'max_marks', header: 'Max Marks (%)', type: 'number' as const },
  { field: 'grade_point', header: 'Grade Point', type: 'number' as const },
  { field: 'is_pass', header: 'Is Pass?', type: 'boolean' as const },
];

// Helper to get subject display name for schedule select dropdown
const getSubjectName = (subjectId: string) => {
  const subj = subjects.value.find(s => s.id === subjectId);
  return subj ? `${subj.name} ${subj.code ? `(${subj.code})` : ''}` : `Subject ID: ${subjectId}`;
};

// Helper to get student info
const getStudentInfo = (enrollmentId: string) => {
  const enrollment = enrollments.value.find(e => e.id === enrollmentId);
  if (enrollment) {
    const student = students.value.find(s => s.id === enrollment.student_id);
    const studentName = student ? student.full_name : 'Student';
    const studentId = student && student.student_id_no ? student.student_id_no : 'N/A';
    const rollNo = enrollment.roll_number != null ? enrollment.roll_number : 'N/A';
    return `${studentName} (ID: ${studentId}, Roll: ${rollNo})`;
  }
  return `Enrollment #${enrollmentId.substring(0, 8)}`;
};

const focusNext = (event: Event) => {
  const inputs = Array.from(document.querySelectorAll('.marks-table .p-inputnumber-input')) as HTMLInputElement[];
  const target = event.target as HTMLInputElement;
  const currentIndex = inputs.indexOf(target);
  if (currentIndex > -1 && currentIndex < inputs.length - 1) {
    inputs[currentIndex + 1]?.focus();
    inputs[currentIndex + 1]?.select();
  }
};

const getDynamicGrade = (result: any) => {
  if (result.status !== 'PRESENT') return result.status;
  
  const schedule = schedules.value.find(s => s.id === result.exam_schedule_id);
  if (!schedule || !schedule.full_marks) return result.grade || 'N/A';

  const marks = result.obtained_marks || 0;
  const percentage = (marks / schedule.full_marks) * 100;
  
  const scales = [...gradingScales.value].sort((a, b) => b.min_marks - a.min_marks);
  for (const scale of scales) {
    if (percentage >= scale.min_marks && percentage <= scale.max_marks) {
      return scale.grade_name;
    }
  }
  return 'N/A';
};

// ── Pagination state ─────────────────────────────────────
const resultsPage = ref(1);
const resultsLimit = ref(50); // 0 = সকল (All)

const paginatedResults = computed(() => {
  if (resultsLimit.value === 0) return filteredResults.value;
  const start = (resultsPage.value - 1) * resultsLimit.value;
  return filteredResults.value.slice(start, start + resultsLimit.value);
});

const totalResultPages = computed(() => {
  if (resultsLimit.value === 0 || filteredResults.value.length === 0) return 1;
  return Math.ceil(filteredResults.value.length / resultsLimit.value);
});

const loadMarks = async () => {
  if (!selectedScheduleId.value || !selectedExamId.value) {
    filteredResults.value = [];
    return;
  }
  markEntryLoading.value = true;
  resultsPage.value = 1;

  try {
    const schedule = schedules.value.find(s => s.id === selectedScheduleId.value);
    const exam = exams.value.find(e => e.id === selectedExamId.value);

    if (!schedule || !exam) {
      filteredResults.value = [];
      return;
    }

    // Backend থেকে শুধু এই schedule-র সব result আনো (server-side filter)
    const response = await ExamService.getResults({
      exam_schedule_id: selectedScheduleId.value,
      fetch_all: true,
    });
    const scheduleResults: any[] = response.items;

    const validEnrollments = enrollments.value.filter(e =>
      e.academic_year_id === exam.academic_year_id && e.class_id === schedule.class_id
    );

    const mapped = validEnrollments.map(enr => {
      const existing = scheduleResults.find((r: any) => r.enrollment_id === enr.id);
      if (existing) return { ...existing, isNew: false };
      return {
        enrollment_id: enr.id,
        exam_schedule_id: schedule.id,
        obtained_marks: 0,
        grade: null,
        status: 'PRESENT',
        isNew: true
      };
    });

    mapped.sort((a, b) => {
      const enrA = validEnrollments.find(e => e.id === a.enrollment_id);
      const enrB = validEnrollments.find(e => e.id === b.enrollment_id);
      const studentA = students.value.find(s => s.id === enrA?.student_id);
      const studentB = students.value.find(s => s.id === enrB?.student_id);
      const idA = studentA?.student_id_no || Number.MAX_SAFE_INTEGER;
      const idB = studentB?.student_id_no || Number.MAX_SAFE_INTEGER;
      if (idA !== idB) return idA - idB;
      const rollA = enrA?.roll_number ? String(enrA.roll_number) : 'ZZZ';
      const rollB = enrB?.roll_number ? String(enrB.roll_number) : 'ZZZ';
      return rollA.localeCompare(rollB, undefined, { numeric: true });
    });

    filteredResults.value = mapped;
  } catch (e) {
    toast.add({ severity: 'error', summary: 'মার্কস লোড ব্যর্থ হয়েছে', life: 3000 });
  } finally {
    markEntryLoading.value = false;
  }
};

const availableExamsForYear = computed(() => {
  if (!selectedYearId.value) return exams.value;
  return exams.value.filter(e => e.academic_year_id === selectedYearId.value);
});

const availableClassesForExam = computed(() => {
  if (!selectedExamId.value) return [];
  const scheduleClassIds = new Set(schedules.value.filter(s => s.exam_id === selectedExamId.value).map(s => s.class_id));
  return classes.value.filter(c => scheduleClassIds.has(c.id));
});

const onYearChange = () => {
  selectedExamId.value = null;
  selectedClassId.value = null;
  selectedScheduleId.value = null;
  filteredResults.value = [];
};

const onExamChange = () => {
  selectedClassId.value = null;
  selectedScheduleId.value = null;
  filteredResults.value = [];
};

const onClassChange = () => {
  selectedScheduleId.value = null;
  filteredResults.value = [];
  resultsPage.value = 1;
};

const saveMarks = async () => {
  if (filteredResults.value.length === 0) return;
  markEntryLoading.value = true;
  try {
    await Promise.all(
      filteredResults.value.map(res => {
        const payload = {
          enrollment_id: res.enrollment_id,
          exam_schedule_id: res.exam_schedule_id,
          obtained_marks: res.obtained_marks || 0,
          status: res.status
        };
        return res.isNew ? ExamService.createResult(payload) : ExamService.updateResult(res.id, payload);
      })
    );
    toast.add({ severity: 'success', summary: 'Marks Saved', detail: 'Student marks updated successfully.', life: 3000 });
    await load();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Save Failed', detail: 'Failed to update marks', life: 3000 });
  } finally {
    markEntryLoading.value = false;
  }
};

const generateResult = async () => {
  if (!selectedExamId.value) {
    toast.add({ severity: 'warn', summary: 'Select Exam', detail: 'Please select an exam first.', life: 3000 });
    return;
  }
  markEntryLoading.value = true;
  try {
    const res = await ExamService.generateResults(selectedExamId.value);
    toast.add({ severity: 'success', summary: 'Results Generated', detail: res.message || 'Final exam results calculated!', life: 3000 });
    await load();
  } catch (e: any) {
    toast.add({ severity: 'error', summary: 'Generation Failed', detail: e?.response?.data?.detail || 'Failed to generate results', life: 3000 });
  } finally {
    markEntryLoading.value = false;
  }
};
</script>

<template>
  <div class="page-container">
    <Toast />
    
    <div class="page-header">
      <div>
        <h1>Examination Management</h1>
        <p>Manage exams, schedules, grading policies, and mark entry.</p>
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
      <div v-if="activeTab === 'exams'">
        <div class="filter-card" style="margin-bottom: 1.5rem; padding: 1rem;">
          <div class="filter-group" style="max-width: 300px;">
            <label>Filter by Academic Year</label>
            <select v-model="examFilterYearId" class="custom-select">
              <option :value="null">-- All Academic Years --</option>
              <option v-for="y in academicYears" :key="y.id" :value="y.id">{{ y.name }}</option>
            </select>
          </div>
        </div>
        <CrudTable 
          title="Exams" 
          :rows="filteredExams" 
          :columns="examCols" 
          :loading="loading"
          :createFn="ExamService.createExam"
          :updateFn="ExamService.updateExam"
          :deleteFn="ExamService.deleteExam"
          @refresh="load" 
        />
      </div>

      <div v-if="activeTab === 'types'">
        <CrudTable 
          title="Exam Types" 
          :rows="examTypes" 
          :columns="typeCols" 
          :loading="loading"
          :createFn="ExamService.createExamType"
          :updateFn="ExamService.updateExamType"
          :deleteFn="ExamService.deleteExamType"
          @refresh="load" 
        />
      </div>

      <div v-if="activeTab === 'grading'">
        <CrudTable 
          title="Grading Scales" 
          :rows="gradingScales" 
          :columns="gradingCols" 
          :loading="loading"
          :createFn="ExamService.createGradingScale"
          :updateFn="ExamService.updateGradingScale"
          :deleteFn="ExamService.deleteGradingScale"
          @refresh="load" 
        />
      </div>

      <div v-if="activeTab === 'schedules'">
        <div class="filter-card" style="margin-bottom: 1.5rem; padding: 1rem; display: flex; gap: 1.5rem; flex-wrap: wrap;">
          <div class="filter-group" style="max-width: 300px;">
            <label>Filter by Academic Year</label>
            <select v-model="scheduleFilterYearId" class="custom-select">
              <option :value="null">-- All Academic Years --</option>
              <option v-for="y in academicYears" :key="y.id" :value="y.id">{{ y.name }}</option>
            </select>
          </div>
          <div class="filter-group" style="max-width: 300px;">
            <label>Filter by Class</label>
            <select v-model="scheduleFilterClassId" class="custom-select">
              <option :value="null">-- All Classes --</option>
              <option v-for="c in classes" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>
        </div>
        <CrudTable 
          title="Exam Schedules" 
          :rows="filteredSchedules" 
          :columns="scheduleCols" 
          :loading="loading"
          :createFn="ExamService.createSchedule"
          :updateFn="ExamService.updateSchedule"
          :deleteFn="ExamService.deleteSchedule"
          @refresh="load" 
        />
      </div>

      <div v-if="activeTab === 'mark-entry'" class="mark-entry-panel">
        <div class="filter-card" style="flex-wrap: wrap;">
          <div class="filter-group">
            <label>Select Academic Year</label>
            <select v-model="selectedYearId" class="custom-select" @change="onYearChange">
              <option :value="null">-- Choose Academic Year --</option>
              <option v-for="y in academicYears" :key="y.id" :value="y.id">{{ y.name }}</option>
            </select>
          </div>

          <div class="filter-group">
            <label>Select Exam</label>
            <div style="display: flex; gap: 1rem;">
              <select v-model="selectedExamId" class="custom-select" :disabled="!selectedYearId" @change="onExamChange" style="flex: 1;">
                <option :value="null">-- Choose Exam --</option>
                <option v-for="e in availableExamsForYear" :key="e.id" :value="e.id">{{ e.name }}</option>
              </select>
              <Button label="Generate" icon="pi pi-cog" severity="success" @click="generateResult" :disabled="!selectedExamId" :loading="markEntryLoading"/>
            </div>
          </div>
          
          <div class="filter-group">
            <label>Select Class</label>
            <select v-model="selectedClassId" class="custom-select" :disabled="!selectedExamId" @change="onClassChange">
              <option :value="null">-- Choose Class --</option>
              <option v-for="c in availableClassesForExam" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>

          <div class="filter-group">
            <label>Select Subject / Schedule</label>
            <select v-model="selectedScheduleId" class="custom-select" :disabled="!selectedClassId" @change="loadMarks">
              <option :value="null">-- Choose Schedule --</option>
              <option v-for="s in schedules.filter(sch => sch.exam_id === selectedExamId && sch.class_id === selectedClassId)" :key="s.id" :value="s.id">
                {{ getSubjectName(s.subject_id) }} | Date: {{ s.exam_date }}
              </option>
            </select>
          </div>

        </div>

        <div class="marks-table-card" v-if="filteredResults.length > 0">
          <div class="card-header">
            <h3>Student Marks Entry</h3>
            <Button label="Save All Marks" icon="pi pi-save" @click="saveMarks" :loading="markEntryLoading" />
          </div>
          <div style="overflow-x: auto;">
            <table class="marks-table">
              <thead>
                <tr>
                  <th style="white-space: nowrap;">Student / Enrollment</th>
                  <th style="white-space: nowrap; text-align: center;">Obtained Marks</th>
                  <th style="white-space: nowrap; text-align: center;">Status</th>
                  <th style="white-space: nowrap; text-align: center;">Calculated Grade</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="result in paginatedResults" :key="result.id || result.enrollment_id">
                  <td style="white-space: nowrap;">{{ getStudentInfo(result.enrollment_id) }}</td>
                  <td style="text-align: center;">
                    <InputNumber 
                      v-model="result.obtained_marks" 
                      :minFractionDigits="0" 
                      :maxFractionDigits="2" 
                      :min="0" 
                      :inputStyle="{ width: '90px', textAlign: 'center' }"
                      :disabled="result.status !== 'PRESENT'" 
                      @keydown.enter.prevent="focusNext"
                    />
                  </td>
                  <td style="text-align: center;">
                    <select v-model="result.status" class="custom-select" style="width: 110px;">
                      <option value="PRESENT">Present</option>
                      <option value="ABSENT">Absent</option>
                      <option value="WITHHELD">Withheld</option>
                      <option value="EXPELLED">Expelled</option>
                    </select>
                  </td>
                  <td style="text-align: center;"><strong>{{ getDynamicGrade(result) }}</strong></td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Pagination Controls -->
          <div class="pagination-bar" v-if="filteredResults.length > 0">
            <span class="pagination-info">মোট <strong>{{ filteredResults.length }}</strong> জন শিক্ষার্থী</span>
            <div class="pagination-nav" v-if="resultsLimit !== 0 && totalResultPages > 1">
              <button class="page-btn" @click="resultsPage--" :disabled="resultsPage === 1">&#9664;</button>
              <span class="page-indicator">{{ resultsPage }} / {{ totalResultPages }}</span>
              <button class="page-btn" @click="resultsPage++" :disabled="resultsPage === totalResultPages">&#9654;</button>
            </div>
            <div class="per-page-wrap">
              <label>প্রতি পেজে:</label>
              <select v-model="resultsLimit" class="per-page-select" @change="resultsPage = 1">
                <option :value="25">25</option>
                <option :value="50">50</option>
                <option :value="100">100</option>
                <option :value="0">সকল</option>
              </select>
            </div>
          </div>
        </div>

        <div v-else-if="selectedScheduleId && !markEntryLoading" class="empty-state">
          <i class="pi pi-inbox" style="font-size: 2rem; color: #94a3b8; margin-bottom: 0.5rem;"></i>
          <p>No marks/results records created for this schedule yet.</p>
        </div>
      </div>

      <div v-if="activeTab === 'reports'" class="reports-panel">
        <TabView>
          <TabPanel header="Merit List" value="0">
            <ExamReportView />
          </TabPanel>
          <TabPanel header="Single Marksheets" value="1">
            <MarksheetView />
          </TabPanel>
        </TabView>
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

/* Mark Entry Styling */
.mark-entry-panel {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.filter-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid #f0f4f8;
  display: flex;
  gap: 1.5rem;
  align-items: flex-end;
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
  flex-wrap: wrap;
}
.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
  min-width: 200px;
}
.filter-group label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #486581;
}
.custom-select {
  padding: 0.65rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.9rem;
  background: #fff;
  color: #1e293b;
  outline: none;
  width: 100%;
}
.marks-table-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid #f0f4f8;
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.card-header h3 {
  margin: 0;
  color: #334e68;
}
.marks-table {
  width: 100%;
  border-collapse: collapse;
}
.marks-table th, .marks-table td {
  padding: 1rem;
  border-bottom: 1px solid #f0f4f8;
  text-align: left;
}
.marks-table th {
  background-color: #f8fafc;
  color: #475569;
  font-weight: 600;
}
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  background: white;
  border-radius: 12px;
  color: #64748b;
  border: 1px dashed #cbd5e1;
}
.empty-state p {
  margin: 0;
}

/* Pagination */
.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
  padding: 0.75rem 0 0;
  border-top: 1px solid #f0f4f8;
  margin-top: 0.75rem;
}
.pagination-info {
  font-size: 0.875rem;
  color: #64748b;
}
.pagination-nav {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.page-btn {
  width: 32px;
  height: 32px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  background: #fff;
  color: #334e68;
  cursor: pointer;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}
.page-btn:hover:not(:disabled) {
  background: #eff6ff;
  border-color: #2563eb;
  color: #2563eb;
}
.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.page-indicator {
  font-size: 0.875rem;
  font-weight: 600;
  color: #334e68;
  min-width: 50px;
  text-align: center;
}
.per-page-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #64748b;
}
.per-page-select {
  padding: 0.3rem 0.5rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.875rem;
  background: #fff;
  color: #1e293b;
  cursor: pointer;
}
</style>
