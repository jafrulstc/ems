<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue';
import { useToast } from 'primevue/usetoast';
import { ExamService } from '../../services/exam.service';
import { AcademicService } from '../../services/academic.service';
import { TenantService } from '../../services/tenant.service';
import { useAuthStore } from '../../stores/auth';
import Button from 'primevue/button';
import Toast from 'primevue/toast';
import * as XLSX from 'xlsx';

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
  exam_id: null,
});

const meritList = ref<any[]>([]);

onMounted(async () => {
  try {
    const [examsData, yearsData, classesData, scalesData, institutesData] = await Promise.all([
      ExamService.getExams({fetch_all: true}).then(r => r.items),
      AcademicService.getYears({fetch_all: true}).then(r => r.items).catch(() => []),
      AcademicService.getClasses({fetch_all: true}).then(r => r.items).catch(() => []),
      ExamService.getGradingScales({fetch_all: true}).then(r => r.items).catch(() => []),
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

const toBengali = (num: number | string | undefined): string => {
  if (num === undefined || num === null) return '';
  const benDigits = ['০', '১', '২', '৩', '৪', '৫', '৬', '৭', '৮', '৯'];
  return num.toString().replace(/\d/g, (d) => benDigits[parseInt(d, 10)] ?? d);
};

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
    
    meritList.value = await ExamService.getMeritList(params);
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Failed to load report', life: 3000 });
  } finally {
    loading.value = false;
  }
};

const uniqueSubjects = computed(() => {
  const subs = new Set<string>();
  meritList.value.forEach(row => {
    Object.keys(row.subjects || {}).forEach(s => subs.add(s));
  });
  return Array.from(subs);
});

const totalExaminees = computed(() => meritList.value.length);
const totalPassed = computed(() => meritList.value.filter(s => !s.has_failed).length);
const totalAbsent = computed(() => meritList.value.filter(s => s.special_status === 'Absent').length);
const totalFailed = computed(() => totalExaminees.value - totalPassed.value - totalAbsent.value);

const selectedExamName = computed(() => {
  const ex = exams.value.find(e => e.id === reportFilters.value.exam_id);
  return ex ? ex.name : '';
});

const selectedClassName = computed(() => {
  const cls = classes.value.find(c => c.id === reportFilters.value.class_id);
  return cls ? cls.name : '';
});

const selectedDepartmentName = computed(() => {
  const cls = classes.value.find(c => c.id === reportFilters.value.class_id);
  return (cls && cls.department_name) ? cls.department_name : '';
});

const selectedYearName = computed(() => {
  const y = academicYears.value.find(y => y.id === reportFilters.value.academic_year_id);
  return y ? y.name : '';
});

// Backend now calculates GPA accurately based on individual subject grade points
// No local calculateGPA needed here anymore.

const printReport = async () => {
  isPrinting.value = true;
  await nextTick();

  // Inject @page landscape style dynamically — most reliable cross-browser approach
  const style = document.createElement('style');
  style.id = '__landscape_print_style__';
  style.textContent = `@page { size: A4 landscape !important; margin: 1cm !important; }`;
  document.head.appendChild(style);

  setTimeout(() => {
    window.print();
    // Remove the injected style after print dialog closes
    const el = document.getElementById('__landscape_print_style__');
    if (el) el.remove();
    isPrinting.value = false;
  }, 150);
};

const exportToExcel = () => {
  const headers = ['ক্র. নং', 'শিক্ষার্থীদের নাম', ...uniqueSubjects.value, 'মোট', 'প্রাপ্ত', 'গড়', 'জিপিএ', 'গ্রেড', 'মেধাক্রম'];
  
  const data = meritList.value.map((row, index) => {
    const rowData: any = {
      'ক্র. নং': index + 1,
      'শিক্ষার্থীদের নাম': row.student_name,
    };
    
    uniqueSubjects.value.forEach(subj => {
      rowData[subj] = row.subjects[subj] !== undefined ? row.subjects[subj].obtained_marks : '-';
    });
    
    rowData['মোট'] = Number(row.total_full_marks.toFixed(2));
    rowData['প্রাপ্ত'] = Number(row.total_marks.toFixed(2));
    rowData['গড়'] = row.average_marks ? row.average_marks.toFixed(2) : '0.00';
    rowData['জিপিএ'] = row.has_failed ? '0.00' : (row.gpa !== null && row.gpa !== undefined ? row.gpa.toFixed(2) : '0.00');
    rowData['গ্রেড'] = row.overall_grade || '-';
    rowData['মেধাক্রম'] = row.rank || '-';
    
    return rowData;
  });

  const worksheet = XLSX.utils.json_to_sheet(data, { header: headers });
  
  // Custom column widths
  const wscols = [
    { wch: 10 }, // serial
    { wch: 30 }, // name
    ...uniqueSubjects.value.map(() => ({ wch: 15 })), // subjects
    { wch: 10 }, // total
    { wch: 10 }, // obtained
    { wch: 10 }, // avg
    { wch: 10 }, // gpa
    { wch: 10 }, // grade
    { wch: 10 }  // rank
  ];
  worksheet['!cols'] = wscols;

  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, 'Merit List');
  XLSX.writeFile(workbook, `Merit_List_${selectedClassName.value || 'Report'}.xlsx`);
};

// Column Resizing Logic
const resizingCol = ref<HTMLElement | null>(null);
const startX = ref(0);
const startWidth = ref(0);

const startResize = (e: MouseEvent) => {
  const target = e.target as HTMLElement;
  const th = target.closest('th');
  if (!th) return;
  
  resizingCol.value = th;
  startX.value = e.pageX;
  startWidth.value = th.offsetWidth;
  
  document.addEventListener('mousemove', handleMouseMove);
  document.addEventListener('mouseup', stopResize);
};

const handleMouseMove = (e: MouseEvent) => {
  if (!resizingCol.value) return;
  const dx = e.pageX - startX.value;
  requestAnimationFrame(() => {
    if (resizingCol.value) {
      resizingCol.value.style.width = `${startWidth.value + dx}px`;
      resizingCol.value.style.minWidth = `${startWidth.value + dx}px`;
    }
  });
};

const stopResize = () => {
  resizingCol.value = null;
  document.removeEventListener('mousemove', handleMouseMove);
  document.removeEventListener('mouseup', stopResize);
};
</script>

<template>
  <div class="page-container">
    <Toast />
    
    <div class="no-print filter-card">
      <div class="filter-group">
        <label>Academic Year</label>
        <select v-model="reportFilters.academic_year_id" class="custom-select">
          <option :value="null">-- Select Year --</option>
          <option v-for="y in academicYears" :key="y.id" :value="y.id">{{ y.name }}</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Class</label>
        <select v-model="reportFilters.class_id" class="custom-select">
          <option :value="null">-- Select Class --</option>
          <option v-for="c in classes" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Exam</label>
        <select v-model="reportFilters.exam_id" class="custom-select">
          <option :value="null">-- Select Exam --</option>
          <option v-for="e in exams" :key="e.id" :value="e.id">{{ e.name }}</option>
        </select>
      </div>
      <Button label="Load Report" icon="pi pi-search" @click="loadReport" :loading="loading" style="height: 42px;" />
    </div>

    <div class="no-print actions-bar" v-if="meritList.length > 0">
      <Button label="Print" icon="pi pi-print" @click="printReport" class="p-button-secondary" />
      <Button label="Export Excel" icon="pi pi-file-excel" @click="exportToExcel" class="p-button-success" />
    </div>

    <Teleport to="body" :disabled="!isPrinting">
      <div class="report-wrapper" :class="{ 'is-printing-mode': isPrinting }" v-if="meritList.length > 0">
        <div class="report-container">
          <!-- Report Header -->
        <div class="report-header">
          <!-- Left: Stats -->
          <div class="stats-box">
            <div class="stat-row">
              <span class="stat-label">মোট শিক্ষার্থী :</span>
              <span class="stat-val">{{ totalExaminees }} জন</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">পাস :</span>
              <span class="stat-val">{{ totalPassed }} জন</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">অকৃতকার্য :</span>
              <span class="stat-val">{{ totalFailed }} জন</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">অনুপস্থিত :</span>
              <span class="stat-val">{{ totalAbsent }} জন</span>
            </div>
          </div>

          <!-- Center: Titles -->
          <div class="title-box">
            <h1 class="org-name">{{ instituteName }}</h1>
            <h2 class="exam-name">{{ selectedExamName }}</h2>
            <!-- <p class="class-info">বিভাগ: {{ selectedDepartmentName }} &nbsp;&nbsp; শ্রেণি: {{ selectedClassName }} &nbsp;&nbsp; শাখা/গ্রুপ: -</p> -->
            <p class="class-info">বিভাগ: {{ selectedDepartmentName }} &nbsp;&nbsp; শ্রেণি: {{ selectedClassName }}</p>
          </div>

          <!-- Right: Grading Table -->
          <div class="grading-box">
            <table class="grading-table">
              <thead>
                <tr>
                  <th>মার্কের পরিমাণ (শতকরা)</th>
                  <th>গ্রেড</th>
                  <th>পয়েন্ট</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(scale, index) in sortedGradingScales" :key="scale.id">
                  <td>
                    <template v-if="index === 0">
                      {{ toBengali(scale.min_marks) }} বা তার বেশি
                    </template>
                    <template v-else>
                      {{ toBengali(scale.min_marks) }} থেকে {{ toBengali(scale.max_marks) }}
                    </template>
                  </td>
                  <td>{{ scale.grade_name }}</td>
                  <td>{{ scale.grade_point.toFixed(2) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Main Data Table -->
        <table class="merit-table">
          <thead>
            <tr>
              <th width="5%" class="resizable-th">
                ক্র.<br>নং
                <div class="resizer no-print" @mousedown.prevent="startResize"></div>
              </th>
              <th width="20%" class="resizable-th">
                শিক্ষার্থীদের নাম
                <div class="resizer no-print" @mousedown.prevent="startResize"></div>
              </th>
              <th v-for="subj in uniqueSubjects" :key="subj" class="resizable-th">
                {{ subj }}
                <div class="resizer no-print" @mousedown.prevent="startResize"></div>
              </th>
              <th width="6%" class="resizable-th">
                মোট
                <div class="resizer no-print" @mousedown.prevent="startResize"></div>
              </th>
              <th width="6%" class="resizable-th">
                প্রাপ্ত
                <div class="resizer no-print" @mousedown.prevent="startResize"></div>
              </th>
              <th width="6%" class="resizable-th">
                গড়
                <div class="resizer no-print" @mousedown.prevent="startResize"></div>
              </th>
              <th width="6%" class="resizable-th">
                জিপিএ
                <div class="resizer no-print" @mousedown.prevent="startResize"></div>
              </th>
              <th width="6%" class="resizable-th">
                গ্রেড
                <div class="resizer no-print" @mousedown.prevent="startResize"></div>
              </th>
              <th width="8%" class="resizable-th">
                মেধাক্রম
                <div class="resizer no-print" @mousedown.prevent="startResize"></div>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in meritList" :key="row.enrollment_id">
              <td class="text-center">{{ index + 1 }}</td>
              <td>{{ row.student_name }}</td>
              <td class="text-center" v-for="subj in uniqueSubjects" :key="subj">
                {{ row.subjects[subj] !== undefined ? Number(row.subjects[subj].obtained_marks.toFixed(2)) : '-' }}
              </td>
              <td class="text-center">{{ Number(row.total_full_marks.toFixed(2)) }}</td>
              <td class="text-center">{{ Number(row.total_marks.toFixed(2)) }}</td>
              <td class="text-center">{{ row.average_marks ? row.average_marks.toFixed(2) : '0.00' }}</td>
              <td class="text-center">{{ row.has_failed ? '0.00' : (row.gpa !== null && row.gpa !== undefined ? row.gpa.toFixed(2) : '0.00') }}</td>
              <td class="text-center">{{ row.overall_grade || '-' }}</td>
              <td class="text-center">{{ row.has_failed ? 'F' : (row.rank || '-') }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    </Teleport>
    
    <div v-if="meritList.length === 0 && !loading" class="empty-state no-print">
      <i class="pi pi-print" style="font-size: 2.5rem; color: #cbd5e1; margin-bottom: 1rem;"></i>
      <p>Select criteria and click Load Report to generate the merit list.</p>
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

.actions-bar {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  background: white;
  border-radius: 12px;
  color: #64748b;
  border: 1px dashed #cbd5e1;
}

/* --- Report Specific Styles --- */
.report-wrapper {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  overflow-x: auto;
}

.report-container {
  min-width: 900px;
  color: #000;
  font-family: 'Arial', sans-serif;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  border: 2px solid #000;
  padding: 10px;
}

/* Stats Box */
.stats-box {
  border: 1px solid #000;
  padding: 8px 12px;
  font-size: 15px;
  width: 200px;
  font-weight: bold;
}
.stat-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}
.stat-row:last-child {
  margin-bottom: 0;
}

/* Title Box */
.title-box {
  text-align: center;
  flex: 1;
  padding: 0 20px;
}
.org-name {
  margin: 0 0 5px 0;
  font-size: 36px;
  font-weight: 900;
}
.exam-name {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: bold;
}
.class-info {
  margin: 0;
  font-size: 14px;
  font-weight: bold;
}

/* Grading Box */
.grading-box {
  width: 250px;
}
.grading-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
  font-weight: bold;
}
.grading-table th, .grading-table td {
  border: 1px solid #000;
  padding: 3px 6px;
  text-align: center;
}
.grading-table th {
  background-color: #f9f9f9;
}

/* Merit Table */
.merit-table {
  width: 100%;
  border-collapse: collapse;
  border: 2px solid #000;
  font-size: 14px;
  font-weight: 600;
}
.merit-table th, .merit-table td {
  border: 1px solid #000;
  padding: 6px 8px;
}
.merit-table th {
  background-color: #f9f9f9;
  text-align: center;
  vertical-align: middle;
  font-size: 15px;
}
.merit-table td {
  font-size: 14px;
}
.text-center {
  text-align: center;
}

/* Resizable Columns */
.resizable-th {
  position: relative;
}
.resizer {
  position: absolute;
  top: 0;
  right: 0;
  width: 6px;
  cursor: col-resize;
  user-select: none;
  height: 100%;
  background-color: transparent;
  z-index: 10;
}
.resizer:hover,
.resizer:active {
  background-color: #cbd5e1;
}

/* Print Styles */
@media print {
  .is-printing-mode {
    position: static;
    width: 100%;
    padding: 0;
    box-shadow: none;
    background: white;
  }

  .report-wrapper {
    overflow: visible !important;
  }

  .report-container {
    min-width: 100% !important;
    width: 100% !important;
  }

  .no-print {
    display: none !important;
  }
  
  /* Make all non-table borders 1px and uniform in print */
  .report-header, .stats-box {
    border: 1px solid #000 !important;
  }
  
  .grading-table {
    border-collapse: separate !important;
    border-spacing: 0 !important;
    border: none !important;
  }
  .grading-table th, .grading-table td {
    border-bottom: 1px solid #000 !important;
    border-right: 1px solid #000 !important;
    border-top: none !important;
    border-left: none !important;
  }
  .grading-table thead th {
    border-top: 1px solid #000 !important;
  }
  .grading-table th:first-child, .grading-table td:first-child {
    border-left: 1px solid #000 !important;
  }

  /* Merit Table: Perfect 1px borders across page breaks */
  .merit-table {
    border-collapse: separate !important;
    border-spacing: 0 !important;
    border: none !important;
  }
  
  .merit-table thead {
    display: table-header-group;
  }
  
  .merit-table tr {
    page-break-inside: avoid;
  }

  .merit-table th, .merit-table td {
    border-bottom: 1px solid #000 !important;
    border-right: 1px solid #000 !important;
    border-top: none !important;
    border-left: none !important;
    box-shadow: none !important;
    background-color: transparent !important;
    background-clip: padding-box !important;
  }

  /* Force top border only on header cells so it repeats perfectly on page 2 */
  .merit-table thead th {
    border-top: 1px solid #000 !important;
  }
  
  /* Force left border on the first column of every row */
  .merit-table th:first-child, .merit-table td:first-child {
    border-left: 1px solid #000 !important;
  }
}
</style>

<style>
@media print {
  @page {
    margin: 1cm;
  }
}
</style>

