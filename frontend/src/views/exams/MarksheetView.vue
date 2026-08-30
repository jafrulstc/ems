<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue';
import { useToast } from 'primevue/usetoast';
import { ExamService } from '../../services/exam.service';
import { AcademicService } from '../../services/academic.service';
import { TenantService } from '../../services/tenant.service';
import { useAuthStore } from '../../stores/auth';
import Button from 'primevue/button';

const toast = useToast();
const authStore = useAuthStore();

const loading = ref(false);
const isPrinting = ref(false);
const exams = ref<any[]>([]);
const academicYears = ref<any[]>([]);
const classes = ref<any[]>([]);
const gradingScales = ref<any[]>([]);
const instituteName = ref('');

const reportFilters = ref({
  academic_year_id: null,
  class_id: null,
  exam_id: null
});

const meritList = ref<any[]>([]);
const uniqueSubjects = ref<string[]>([]);

onMounted(async () => {
  try {
    const [examsData, yearsData, classesData, scalesData, institutesData] = await Promise.all([
      ExamService.getExams(),
      AcademicService.getYears().catch(() => []),
      AcademicService.getClasses().catch(() => []),
      ExamService.getGradingScales().catch(() => []),
      TenantService.getInstitutes().catch(() => [])
    ]);
    
    exams.value = examsData;
    academicYears.value = yearsData;
    classes.value = classesData;
    gradingScales.value = scalesData;
    
    if (institutesData && institutesData.length > 0) {
      const currentInstitute = institutesData.find((i: any) => i.slug === authStore.tenantSlug);
      if (currentInstitute) {
        instituteName.value = currentInstitute.name;
      } else {
        instituteName.value = institutesData[0].name;
      }
    }
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Initialization failed', life: 3000 });
  }
});

const sortedGradingScales = computed(() => {
  return [...gradingScales.value].sort((a, b) => b.min_marks - a.min_marks);
});

const loadReport = async () => {
  if (!reportFilters.value.exam_id) {
    toast.add({ severity: 'warn', summary: 'Please select an exam', life: 3000 });
    return;
  }
  loading.value = true;
  try {
    const params: any = {};
    if (reportFilters.value.exam_id) params.exam_id = reportFilters.value.exam_id;
    if (reportFilters.value.academic_year_id) params.academic_year_id = reportFilters.value.academic_year_id;
    if (reportFilters.value.class_id) params.class_id = reportFilters.value.class_id;
    
    const data = await ExamService.getMeritList(params);
    meritList.value = data;
    
    const subjects = new Set<string>();
    data.forEach((row: any) => {
      Object.keys(row.subjects).forEach(s => subjects.add(s));
    });
    uniqueSubjects.value = Array.from(subjects);
    
    if (data.length === 0) {
      toast.add({ severity: 'info', summary: 'No results found', life: 3000 });
    }
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Failed to load report', life: 3000 });
  } finally {
    loading.value = false;
  }
};

const selectedExamName = computed(() => {
  const ex = exams.value.find(e => e.id === reportFilters.value.exam_id);
  return ex ? ex.name : '';
});

const selectedDepartmentName = computed(() => {
  const cls = classes.value.find(c => c.id === reportFilters.value.class_id);
  return (cls && cls.department_name) ? cls.department_name : '';
});

const selectedClassName = computed(() => {
  const cls = classes.value.find(c => c.id === reportFilters.value.class_id);
  return cls ? cls.name : '';
});

const selectedYearName = computed(() => {
  const y = academicYears.value.find(y => y.id === reportFilters.value.academic_year_id);
  return y ? y.name : '';
});

const printReport = async () => {
  isPrinting.value = true;
  await nextTick();
  setTimeout(() => {
    window.print();
    isPrinting.value = false;
  }, 100);
};
</script>

<template>
  <div class="page-container">
    <div class="filter-card card">
      <h2 class="page-title">Marksheet Generation</h2>
      <div class="filter-grid">
        <div class="field">
          <label>Academic Year</label>
          <select v-model="reportFilters.academic_year_id" class="custom-select">
            <option :value="null">-- Select Year --</option>
            <option v-for="y in academicYears" :key="y.id" :value="y.id">{{ y.name }}</option>
          </select>
        </div>
        <div class="field">
          <label>Class</label>
          <select v-model="reportFilters.class_id" class="custom-select">
            <option :value="null">-- Select Class --</option>
            <option v-for="c in classes" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>
        <div class="field">
          <label>Exam *</label>
          <select v-model="reportFilters.exam_id" class="custom-select">
            <option :value="null">-- Select Exam --</option>
            <option v-for="e in exams" :key="e.id" :value="e.id">{{ e.name }}</option>
          </select>
        </div>
      </div>
      <div class="filter-actions">
        <Button label="Load Marksheets" icon="pi pi-search" @click="loadReport" :loading="loading" />
      </div>
    </div>

    <div v-if="meritList.length > 0" class="actions-bar no-print">
      <Button label="Print Marksheets" icon="pi pi-print" @click="printReport" class="p-button-secondary" />
    </div>

    <Teleport to="body" :disabled="!isPrinting">
      <div class="marksheet-wrapper" :class="{ 'is-printing-mode': isPrinting }" v-if="meritList.length > 0">
        
        <!-- Loop over each student for their marksheet -->
        <div class="marksheet-page" v-for="(student) in meritList" :key="student.enrollment_id">
          <div class="marksheet-frame">
            <div class="ms-header-container">
              <div class="ms-header-center">
                <h1 class="ms-institute">{{ instituteName }}</h1>
                <h3 class="ms-exam-name">{{ selectedExamName }} - {{ selectedYearName }}</h3>
                <p class="ms-class-info">বিভাগ: {{ selectedDepartmentName }} &nbsp;&nbsp; শ্রেণি: {{ selectedClassName }}</p>
              </div>

              <div class="ms-grading-scale-box" v-if="sortedGradingScales.length > 0">
                <table class="gs-mini-table">
                  <thead>
                    <tr>
                      <th>রেঞ্জ (%)</th>
                      <th>গ্রেড</th>
                      <th>পয়েন্ট</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="scale in sortedGradingScales" :key="scale.id">
                      <td>{{ scale.min_marks }}-{{ scale.max_marks }}%</td>
                      <td>{{ scale.grade_name }}</td>
                      <td>{{ scale.grade_point ? scale.grade_point.toFixed(2) : '0.00' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div class="ms-header-line"></div>

            <div class="ms-student-info">
              <div class="info-row">
                <span class="info-label">শিক্ষার্থীর নাম:</span>
                <span class="info-value font-bold">{{ student.student_name }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">রোল নম্বর:</span>
                <span class="info-value">{{ student.roll_number }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">স্টুডেন্ট আইডি:</span>
                <span class="info-value">{{ student.student_id_no }}</span>
              </div>
            </div>

            <table class="ms-table">
              <thead>
                <tr>
                  <th>বিষয়</th>
                  <th width="15%">পূর্ণমান</th>
                  <th width="15%">প্রাপ্ত নম্বর</th>
                  <th width="15%">লেটার গ্রেড</th>
                  <th width="15%">গ্রেড পয়েন্ট</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="subj in uniqueSubjects" :key="subj">
                  <td class="font-semibold">{{ subj }}</td>
                  <td class="text-center">{{ student.subjects[subj] ? student.subjects[subj].full_marks : '-' }}</td>
                  <td class="text-center">{{ student.subjects[subj] ? student.subjects[subj].obtained_marks : '-' }}</td>
                  <td class="text-center">{{ student.subjects[subj] ? (student.subjects[subj].grade || '-') : '-' }}</td>
                  <td class="text-center">{{ student.subjects[subj] ? (student.subjects[subj].grade_point !== undefined ? student.subjects[subj].grade_point.toFixed(2) : '-') : '-' }}</td>
                </tr>
              </tbody>
            </table>

            <div class="ms-summary">
              <div class="summary-box">
                <div class="summary-item"><span>মোট নম্বর:</span> <strong>{{ student.total_marks }}</strong> / {{ student.total_full_marks }}</div>
                <div class="summary-item"><span>শতাংশ:</span> <strong>{{ student.percentage ? student.percentage.toFixed(2) : '0.00' }}%</strong></div>
              </div>
              <div class="summary-box">
                <div class="summary-item"><span>জিপিএ:</span> <strong>{{ student.has_failed ? '0.00' : (student.gpa !== null && student.gpa !== undefined ? student.gpa.toFixed(2) : '0.00') }}</strong></div>
                <div class="summary-item"><span>লেটার গ্রেড:</span> <strong>{{ student.overall_grade || '-' }}</strong></div>
              </div>
              <div class="summary-box">
                <div class="summary-item"><span>ফলাফল:</span> <strong>{{ student.has_failed ? 'অকৃতকার্য' : 'কৃতকার্য' }}</strong></div>
                <div class="summary-item"><span>মেধাক্রম:</span> <strong>{{ student.has_failed ? 'F' : (student.rank || '-') }}</strong></div>
              </div>
            </div>

            <div class="ms-signatures">
              <div class="sig-line">শ্রেণি শিক্ষকের স্বাক্ষর</div>
              <div class="sig-line">অধ্যক্ষের স্বাক্ষর</div>
            </div>
          </div>
        </div>

      </div>
    </Teleport>
    
    <div v-if="meritList.length === 0 && !loading" class="empty-state no-print">
      <i class="pi pi-file" style="font-size: 2.5rem; color: #cbd5e1; margin-bottom: 1rem;"></i>
      <p>Select criteria and click Load Marksheets to generate.</p>
    </div>
  </div>
</template>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding-bottom: 3rem;
}

.filter-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

.page-title {
  margin: 0 0 1.5rem 0;
  color: #1e293b;
  font-size: 1.25rem;
  font-weight: 600;
}

.filter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.field label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #475569;
}

.filter-actions {
  display: flex;
  justify-content: flex-end;
}

.actions-bar {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.empty-state {
  background: white;
  padding: 4rem 2rem;
  border-radius: 12px;
  text-align: center;
  color: #64748b;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

/* Marksheet Styles */
.marksheet-wrapper {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  align-items: center;
}

.marksheet-page {
  background: white;
  width: 210mm;
  min-height: 297mm;
  padding: 8mm;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border-radius: 0;
  box-sizing: border-box;
  font-family: 'Inter', sans-serif;
  color: #000;
  display: flex;
  flex-direction: column;
}

.marksheet-frame {
  border: 4px solid #000;
  padding: 8mm 10mm;
  height: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.ms-header-container {
  position: relative;
  min-height: 185px;
}

.ms-header-line {
  border-bottom: 2px solid #000;
  margin-bottom: 15px;
  clear: both;
}

.ms-header-center {
  text-align: center;
  padding-right: 140px; /* Space for grading scale box if needed, or keep centered */
}

.ms-grading-scale-box {
  position: absolute;
  right: 0;
  top: 0;
}

.gs-mini-table {
  border-collapse: collapse;
  font-size: 10px;
  line-height: 1.2;
}

.gs-mini-table th, .gs-mini-table td {
  border: 1px solid #000;
  padding: 2px 4px;
  text-align: center;
}

.gs-mini-table th {
  background-color: #f1f5f9;
  font-weight: 700;
}

.ms-institute {
  font-size: 22px;
  font-weight: 800;
  margin: 0 0 4px 0;
}

.ms-exam-name {
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 4px 0;
}

.ms-class-info {
  font-size: 13px;
  margin: 0;
}

.ms-student-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 15px;
  font-size: 14px;
}

.info-row {
  display: flex;
  gap: 8px;
}

.info-label {
  font-weight: 600;
  min-width: 90px;
}

.font-bold {
  font-weight: 700;
}

.font-semibold {
  font-weight: 600;
}

.text-center {
  text-align: center;
}

.ms-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
  font-size: 13px;
}

.ms-table th, .ms-table td {
  border: 1px solid #000;
  padding: 6px 10px;
}

.ms-table th {
  background-color: #f1f5f9;
  font-weight: 700;
}

.ms-summary {
  display: flex;
  justify-content: space-between;
  border: 1px solid #000;
  padding: 10px 15px;
  margin-bottom: 20px;
  background-color: #f8fafc;
}

.summary-box {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.summary-item {
  font-size: 14px;
}

.summary-item span {
  display: inline-block;
  min-width: 75px;
  color: #334e68;
}

.summary-item strong {
  font-size: 15px;
}

.ms-signatures {
  margin-top: auto;
  display: flex;
  justify-content: space-between;
  padding-top: 30px;
}

.sig-line {
  border-top: 1px dashed #000;
  padding-top: 5px;
  width: 180px;
  text-align: center;
  font-weight: 600;
  font-size: 14px;
}

@media print {
  @page {
    size: A4 portrait;
    margin: 0;
  }

  body {
    margin: 0;
    padding: 0;
  }

  .is-printing-mode {
    position: static;
    width: 100%;
    padding: 0;
    box-shadow: none;
    background: white;
    gap: 0;
  }

  .marksheet-page {
    width: 210mm;
    height: 297mm;
    max-height: 297mm;
    padding: 6mm;
    box-shadow: none;
    border: none;
    page-break-after: always;
    break-after: page;
    page-break-inside: avoid;
    break-inside: avoid;
    box-sizing: border-box;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }
  
  /* The last page shouldn't break */
  .marksheet-page:last-child {
    page-break-after: auto;
    break-after: auto;
  }

  .no-print {
    display: none !important;
  }
}
</style>
