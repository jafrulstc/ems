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
const activeTab = ref('exams');

const exams = ref<any[]>([]);
const schedules = ref<any[]>([]);
const results = ref<any[]>([]);
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

const selectedExamId = ref<string | null>(null);
const selectedScheduleId = ref<string | null>(null);
const filteredResults = ref<any[]>([]);

const load = async () => {
  loading.value = true;
  try {
    const [examsData, schedulesData, resultsData, scalesData, typesData, subjectsData, studentsData, enrollmentsData, yearsData, ycsData, classesData] = await Promise.all([
      ExamService.getExams(),
      ExamService.getSchedules(),
      ExamService.getResults(),
      ExamService.getGradingScales(),
      ExamService.getExamTypes(),
      AcademicService.getSubjects().catch(() => []),
      StudentService.getStudents().catch(() => []),
      StudentService.getEnrollments().catch(() => []),
      AcademicService.getYears().catch(() => []),
      AcademicService.getYearlyClassSubjects().catch(() => []),
      AcademicService.getClasses().catch(() => []),
    ]);

    exams.value = examsData;
    schedules.value = schedulesData;
    results.value = resultsData;
    gradingScales.value = scalesData;
    examTypes.value = typesData;
    subjects.value = subjectsData;
    students.value = studentsData;
    enrollments.value = enrollmentsData;
    academicYears.value = yearsData;
    yearlyClassSubjects.value = ycsData;
    classes.value = classesData;

    if (selectedScheduleId.value) {
      loadMarks();
    }
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Load failed', life: 3000 });
  } finally {
    loading.value = false;
  }
};

onMounted(load);

const tabs = [
  { id: 'exams', label: 'Exams', icon: 'pi pi-file-edit' },
  { id: 'types', label: 'Exam Types', icon: 'pi pi-tags' },
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

const examSubjectsCache = ref<Record<string, string[]>>({});

const fetchExamSubjects = async (exam_id: string) => {
  if (examSubjectsCache.value[exam_id]) return;
  try {
    const ids = await ExamService.getExamSubjects(exam_id);
    examSubjectsCache.value = { ...examSubjectsCache.value, [exam_id]: ids };
  } catch (e) {
    examSubjectsCache.value = { ...examSubjectsCache.value, [exam_id]: [] };
  }
};

const dynamicSubjectOptions = (form: any) => {
  if (!form.exam_id) return subjectOptions.value;
  
  if (!examSubjectsCache.value[form.exam_id]) {
    fetchExamSubjects(form.exam_id);
    return subjectOptions.value; 
  }
  
  const validIds = new Set(examSubjectsCache.value[form.exam_id]);
  return subjectOptions.value.filter(opt => validIds.has(opt.value));
};

const examCols = computed(() => [
  { field: 'name', header: 'Exam Name', required: true },
  { field: 'academic_year_id', header: 'Academic Year', type: 'select' as const, options: academicYearOptions.value, required: true },
  { field: 'start_date', header: 'Start Date', type: 'date' as const, required: true },
  { field: 'end_date', header: 'End Date', type: 'date' as const, required: true },
  { field: 'exam_type_id', header: 'Exam Type', type: 'select' as const, options: examTypeOptions.value, required: true },
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
    const studentName = student ? `${student.first_name} ${student.last_name}` : 'Student';
    const rollNo = enrollment.roll_number || enrollment.enrollment_number;
    return `${studentName} (Roll: ${rollNo})`;
  }
  return `Enrollment #${enrollmentId.substring(0, 8)}`;
};

const loadMarks = () => {
  if (!selectedScheduleId.value || !selectedExamId.value) {
    filteredResults.value = [];
    return;
  }
  markEntryLoading.value = true;
  
  const schedule = schedules.value.find(s => s.id === selectedScheduleId.value);
  const exam = exams.value.find(e => e.id === selectedExamId.value);
  
  if (!schedule || !exam) {
    filteredResults.value = [];
    markEntryLoading.value = false;
    return;
  }

  const validYcs = yearlyClassSubjects.value.filter(ycs => 
    ycs.academic_year_id === exam.academic_year_id && ycs.subject_id === schedule.subject_id
  );
  const validClassIds = validYcs.map(ycs => ycs.class_id);

  const validEnrollments = enrollments.value.filter(e => 
    e.academic_year_id === exam.academic_year_id && validClassIds.includes(e.class_id)
  );

  const mapped = validEnrollments.map(enr => {
    const existing = results.value.find(r => r.exam_schedule_id === schedule.id && r.enrollment_id === enr.id);
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

  filteredResults.value = mapped;
  markEntryLoading.value = false;
};

const onExamChange = () => {
  selectedScheduleId.value = null;
  filteredResults.value = [];
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
        <CrudTable 
          title="Exams" 
          :rows="exams" 
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
        <CrudTable 
          title="Exam Schedules" 
          :rows="schedules" 
          :columns="scheduleCols" 
          :loading="loading"
          :createFn="ExamService.createSchedule"
          :updateFn="ExamService.updateSchedule"
          :deleteFn="ExamService.deleteSchedule"
          @refresh="load" 
        />
      </div>

      <div v-if="activeTab === 'mark-entry'" class="mark-entry-panel">
        <div class="filter-card">
          <div class="filter-group">
            <label>Select Exam</label>
            <div style="display: flex; gap: 1rem;">
              <select v-model="selectedExamId" class="custom-select" @change="onExamChange" style="flex: 1;">
                <option :value="null">-- Choose Exam --</option>
                <option v-for="e in exams" :key="e.id" :value="e.id">{{ e.name }}</option>
              </select>
              <Button label="Generate Final Result" icon="pi pi-cog" severity="success" @click="generateResult" :disabled="!selectedExamId" :loading="markEntryLoading"/>
            </div>
          </div>
          
          <div class="filter-group">
            <label>Select Subject / Schedule</label>
            <select v-model="selectedScheduleId" class="custom-select" :disabled="!selectedExamId" @change="loadMarks">
              <option :value="null">-- Choose Schedule --</option>
              <option v-for="s in schedules.filter(sch => sch.exam_id === selectedExamId)" :key="s.id" :value="s.id">
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
          <table class="marks-table">
            <thead>
              <tr>
                <th>Student / Enrollment</th>
                <th>Obtained Marks</th>
                <th>Status</th>
                <th>Calculated Grade</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="result in filteredResults" :key="result.id">
                <td>{{ getStudentInfo(result.enrollment_id) }}</td>
                <td>
                  <InputNumber v-model="result.obtained_marks" :minFractionDigits="0" :maxFractionDigits="2" :min="0" style="width: 120px;" :disabled="result.status !== 'PRESENT'" />
                </td>
                <td>
                  <select v-model="result.status" class="custom-select" style="width: 120px;">
                    <option value="PRESENT">Present</option>
                    <option value="ABSENT">Absent</option>
                    <option value="WITHHELD">Withheld</option>
                    <option value="EXPELLED">Expelled</option>
                  </select>
                </td>
                <td><strong>{{ result.grade || 'N/A' }}</strong></td>
              </tr>
            </tbody>
          </table>
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
}
.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
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
</style>
