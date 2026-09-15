<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import { ExamService } from '../../services/exam.service';
import { AcademicService } from '../../services/academic.service';
import Button from 'primevue/button';
import InputNumber from 'primevue/inputnumber';
import Select from 'primevue/select';
import Toast from 'primevue/toast';
import ConfirmDialog from 'primevue/confirmdialog';

const toast   = useToast();
const confirm = useConfirm();

// ── State ──────────────────────────────────────────────────────────────────────
const academicYears   = ref<any[]>([]);
const exams           = ref<any[]>([]);
const classes         = ref<any[]>([]);
const schedules       = ref<any[]>([]);
const results         = ref<any[]>([]);

const loading    = ref(false);
const saving     = ref(false);
const generating = ref(false);

const selectedYearId     = ref<string | null>(null);
const selectedExamId     = ref<string | null>(null);
const selectedClassId    = ref<string | null>(null);
const selectedScheduleId = ref<string | null>(null);

// ── Computed filter lists ──────────────────────────────────────────────────────
const filteredExams = computed(() =>
  selectedYearId.value
    ? exams.value.filter(e => e.academic_year_id === selectedYearId.value)
    : exams.value
);

const filteredSchedules = computed(() => {
  if (!selectedExamId.value) return [];
  return schedules.value.filter(s =>
    s.exam_id === selectedExamId.value &&
    (!selectedClassId.value || s.class_id === selectedClassId.value)
  );
});

const selectedSchedule = computed(() =>
  schedules.value.find(s => s.id === selectedScheduleId.value) ?? null
);

// ── Load dropdown data ─────────────────────────────────────────────────────────
const loadOptions = async () => {
  loading.value = true;
  try {
    const [yearsData, examsData, classesData, schedulesData] = await Promise.all([
      AcademicService.getYears({ fetch_all: true }).then(r => r.items).catch(() => []),
      ExamService.getExams({ fetch_all: true }).then(r => r.items),
      AcademicService.getClasses({ fetch_all: true }).then(r => r.items).catch(() => []),
      ExamService.getSchedules({ fetch_all: true }).then(r => r.items),
    ]);
    academicYears.value = yearsData;
    exams.value         = examsData;
    classes.value       = classesData;
    schedules.value     = schedulesData;
  } catch {
    toast.add({ severity: 'error', summary: 'লোড ব্যর্থ হয়েছে', life: 3000 });
  } finally {
    loading.value = false;
  }
};

// ── Load student result rows for selected schedule ─────────────────────────────
const loadMarks = async () => {
  if (!selectedScheduleId.value) return;
  loading.value = true;
  results.value = [];
  try {
    const data = await ExamService.getResults({
      exam_schedule_id: selectedScheduleId.value,
      fetch_all: true,
    });
    const items = data.items ?? data;
    // Store originals to detect unsaved changes
    results.value = items.map((r: any) => ({
      ...r,
      obtained_marks:   Number(r.obtained_marks),
      _original_marks:  Number(r.obtained_marks),
      _original_status: r.status,
    }));
  } catch {
    toast.add({ severity: 'error', summary: 'মার্কস লোড ব্যর্থ', life: 3000 });
  } finally {
    loading.value = false;
  }
};

// ── Save — only pushes changed rows to backend ─────────────────────────────────
const saveMarks = async () => {
  const changed = results.value.filter(
    r => Number(r.obtained_marks) !== r._original_marks || r.status !== r._original_status
  );

  if (!changed.length) {
    toast.add({ severity: 'info', summary: 'কোনো পরিবর্তন নেই', life: 2000 });
    return;
  }

  saving.value = true;
  try {
    await Promise.all(
      changed.map(r =>
        ExamService.updateResult(r.id, {
          enrollment_id:    r.enrollment_id,
          exam_schedule_id: r.exam_schedule_id,
          obtained_marks:   Number(r.obtained_marks),
          status:           r.status,
          grade:            r.grade,
        })
      )
    );
    // Commit originals after success
    results.value.forEach(r => {
      r._original_marks  = Number(r.obtained_marks);
      r._original_status = r.status;
    });
    toast.add({
      severity: 'success',
      summary:  'সংরক্ষিত হয়েছে',
      detail:   `${changed.length} জন শিক্ষার্থীর মার্কস আপডেট হয়েছে।`,
      life: 3000,
    });
  } catch {
    toast.add({ severity: 'error', summary: 'সংরক্ষণ ব্যর্থ হয়েছে', life: 3000 });
  } finally {
    saving.value = false;
  }
};

// ── Generate / Re-generate with confirmation ───────────────────────────────────
const generateResult = () => {
  if (!selectedExamId.value) {
    toast.add({ severity: 'warn', summary: 'প্রথমে একটি পরীক্ষা বেছে নিন', life: 3000 });
    return;
  }

  confirm.require({
    header:       'রিজাল্ট জেনারেট করুন',
    message:
      'এই পরীক্ষার সকল শিক্ষার্থীর গ্রেড পুনরায় হিসাব করা হবে। ' +
      'আগের জেনারেটেড গ্রেড প্রতিস্থাপিত হবে। চালিয়ে যেতে চান?',
    icon:          'pi pi-exclamation-triangle',
    acceptLabel:   'হ্যাঁ, জেনারেট করুন',
    rejectLabel:   'বাতিল',
    acceptClass:   'p-button-danger',
    accept: async () => {
      generating.value = true;
      try {
        const res = await ExamService.generateResults(selectedExamId.value!);
        toast.add({
          severity: 'success',
          summary:  'জেনারেট সম্পন্ন',
          detail:   res.message ?? 'রিজাল্ট সফলভাবে জেনারেট হয়েছে।',
          life: 4000,
        });
        // Reload current schedule to show updated grades
        if (selectedScheduleId.value) await loadMarks();
      } catch (e: any) {
        toast.add({
          severity: 'error',
          summary:  'জেনারেট ব্যর্থ হয়েছে',
          detail:   e?.response?.data?.detail ?? 'অজানা ত্রুটি',
          life: 4000,
        });
      } finally {
        generating.value = false;
      }
    },
  });
};

// ── Helpers ────────────────────────────────────────────────────────────────────
const hasUnsavedChanges = computed(() =>
  results.value.some(
    r => Number(r.obtained_marks) !== r._original_marks || r.status !== r._original_status
  )
);

const statusOptions = [
  { label: 'উপস্থিত (Present)',   value: 'PRESENT' },
  { label: 'অনুপস্থিত (Absent)', value: 'ABSENT' },
  { label: 'বাতিল (Withheld)',    value: 'WITHHELD' },
  { label: 'বহিষ্কৃত (Expelled)', value: 'EXPELLED' },
];

const onStatusChange = (result: any) => {
  if (result.status !== 'PRESENT') result.obtained_marks = 0;
};

onMounted(loadOptions);
</script>

<template>
  <div class="page-container">
    <Toast />
    <ConfirmDialog />

    <!-- ── Header ─────────────────────────────────────────── -->
    <div class="page-header">
      <div class="header-content">
        <div>
          <h1>Marks Entry &amp; Result Generation</h1>
          <p>Enter marks for students and generate final examination results.</p>
        </div>
        <Button
          label="Generate Final Result"
          icon="pi pi-cog"
          severity="success"
          :loading="generating"
          :disabled="!selectedExamId"
          @click="generateResult"
        />
      </div>
    </div>

    <!-- ── Filters ────────────────────────────────────────── -->
    <div class="filter-card">
      <div class="filter-group">
        <label>Academic Year</label>
        <Select
          v-model="selectedYearId"
          :options="academicYears"
          option-label="name"
          option-value="id"
          placeholder="-- Year --"
          class="w-full"
        />
      </div>

      <div class="filter-group">
        <label>Exam</label>
        <Select
          v-model="selectedExamId"
          :options="filteredExams"
          option-label="name"
          option-value="id"
          placeholder="-- Exam --"
          class="w-full"
          :disabled="!filteredExams.length"
          @change="selectedScheduleId = null; results = []"
        />
      </div>

      <div class="filter-group">
        <label>Class</label>
        <Select
          v-model="selectedClassId"
          :options="classes"
          option-label="name"
          option-value="id"
          placeholder="-- Class --"
          class="w-full"
          :disabled="!selectedExamId"
          @change="selectedScheduleId = null; results = []"
        />
      </div>

      <div class="filter-group">
        <label>Subject / Schedule</label>
        <Select
          v-model="selectedScheduleId"
          :options="filteredSchedules"
          option-value="id"
          :option-label="(s: any) => `${s.subject_name ?? s.subject_id} | ${s.exam_date}`"
          placeholder="-- Schedule --"
          class="w-full"
          :disabled="!selectedExamId"
          @change="results = []"
        />
      </div>

      <div class="filter-actions">
        <Button
          label="Load Students"
          icon="pi pi-search"
          :disabled="!selectedScheduleId"
          :loading="loading"
          @click="loadMarks"
        />
      </div>
    </div>

    <!-- ── Schedule info bar ──────────────────────────────── -->
    <div class="info-bar" v-if="selectedSchedule">
      <span>পূর্ণ মার্কস: <strong>{{ selectedSchedule.full_marks }}</strong></span>
      <span>পাস মার্কস: <strong>{{ selectedSchedule.pass_marks }}</strong></span>
      <span>তারিখ: <strong>{{ selectedSchedule.exam_date }}</strong></span>
    </div>

    <!-- ── Marks Table ─────────────────────────────────────── -->
    <div class="marks-table-card" v-if="results.length > 0">
      <div class="card-header">
        <h3>
          Student Marks Entry
          <span v-if="hasUnsavedChanges" class="unsaved-badge">
            ● Unsaved changes
          </span>
        </h3>
        <Button
          label="Save All Marks"
          icon="pi pi-save"
          :loading="saving"
          @click="saveMarks"
        />
      </div>

      <table class="marks-table">
        <thead>
          <tr>
            <th style="width:50px">#</th>
            <th>Student / Enrollment</th>
            <th style="width:160px">Obtained Marks</th>
            <th style="width:190px">Status</th>
            <th style="width:120px">Grade</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(result, index) in results"
            :key="result.id"
            :class="{
              'row-changed': Number(result.obtained_marks) !== result._original_marks
                          || result.status !== result._original_status
            }"
          >
            <td class="text-center">{{ index + 1 }}</td>
            <td>{{ result.student_name ?? result.enrollment_id }}</td>
            <td>
              <InputNumber
                v-model="result.obtained_marks"
                :min="0"
                :max="selectedSchedule?.full_marks ?? 100"
                :minFractionDigits="0"
                :maxFractionDigits="2"
                :disabled="result.status !== 'PRESENT'"
                :inputStyle="{ width: '120px' }"
              />
            </td>
            <td>
              <Select
                v-model="result.status"
                :options="statusOptions"
                option-label="label"
                option-value="value"
                style="min-width: 170px;"
                @change="onStatusChange(result)"
              />
            </td>
            <td class="text-center">
              <strong :class="result.grade === 'F' ? 'fail-grade' : 'pass-grade'">
                {{ result.grade || '—' }}
              </strong>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ── Empty state ────────────────────────────────────── -->
    <div v-else-if="selectedScheduleId && !loading" class="empty-state">
      <i class="pi pi-users" style="font-size:2rem;color:#cbd5e1;margin-bottom:1rem;"></i>
      <p>
        কোনো রেকর্ড পাওয়া যায়নি।<br>
        প্রথমে <strong>Generate Final Result</strong> বাটনে ক্লিক করুন।
      </p>
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
.page-header p { color: #627d98; margin: 0; }
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.filter-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid #f0f4f8;
  display: flex;
  gap: 1.5rem;
  align-items: flex-end;
  flex-wrap: wrap;
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
}
.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
  min-width: 150px;
}
.filter-group label {
  font-size: .9rem;
  font-weight: 600;
  color: #486581;
}
.filter-actions { display: flex; align-items: flex-end; }
.info-bar {
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 8px;
  padding: .75rem 1.25rem;
  display: flex;
  gap: 2rem;
  font-size: .9rem;
  color: #0369a1;
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
  display: flex;
  align-items: center;
  gap: .75rem;
}
.unsaved-badge {
  font-size: .8rem;
  font-weight: 500;
  color: #d97706;
  background: #fef3c7;
  padding: 2px 10px;
  border-radius: 9999px;
}
.marks-table { width: 100%; border-collapse: collapse; }
.marks-table th,
.marks-table td {
  padding: .85rem 1rem;
  border-bottom: 1px solid #f0f4f8;
  text-align: left;
}
.marks-table th {
  background: #f8fafc;
  color: #475569;
  font-weight: 600;
}
.text-center { text-align: center; }
.row-changed { background: #fffbeb; }
.pass-grade { color: #15803d; }
.fail-grade { color: #dc2626; }
.empty-state {
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 12px;
  color: #64748b;
  border: 1px dashed #cbd5e1;
  display: flex;
  flex-direction: column;
  align-items: center;
}
</style>
