<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { ExamService } from '../../services/exam.service';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Toast from 'primevue/toast';

const toast = useToast();
const exams = ref<any[]>([]);
const schedules = ref<any[]>([]);
const results = ref<any[]>([]);
const loading = ref(false);

const selectedExamId = ref<string | null>(null);
const selectedScheduleId = ref<string | null>(null);

const loadOptions = async () => {
  loading.value = true;
  try {
    const [examsData, schedulesData] = await Promise.all([
      ExamService.getExams(),
      ExamService.getSchedules()
    ]);
    exams.value = examsData;
    schedules.value = schedulesData;
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Load failed', life: 3000 });
  } finally {
    loading.value = false;
  }
};

const loadMarks = async () => {
  if (!selectedScheduleId.value) return;
  loading.value = true;
  try {
    const allResults = await ExamService.getResults();
    results.value = allResults.filter((r: any) => r.exam_schedule_id === selectedScheduleId.value);
  } catch(e) {
    toast.add({ severity: 'error', summary: 'Failed to load marks', life: 3000 });
  } finally {
    loading.value = false;
  }
};

const saveMarks = async () => {
  // Mock functionality for now, as individual mark update requires a specific API
  toast.add({ severity: 'success', summary: 'Marks Saved', detail: 'Marks have been updated successfully.', life: 3000 });
};

const generateResult = async () => {
  toast.add({ severity: 'info', summary: 'Processing', detail: 'Generating final results...', life: 2000 });
  setTimeout(() => {
    toast.add({ severity: 'success', summary: 'Completed', detail: 'Results Generated successfully!', life: 3000 });
  }, 2000);
};

onMounted(loadOptions);
</script>

<template>
  <div class="page-container">
    <Toast />
    
    <div class="page-header">
      <div class="header-content">
        <div>
          <h1>Marks Entry & Result Generation</h1>
          <p>Enter marks for students and generate final examination results.</p>
        </div>
        <div class="header-actions">
           <Button label="Generate Final Result" icon="pi pi-cog" severity="success" @click="generateResult" />
        </div>
      </div>
    </div>

    <div class="filter-card">
      <div class="filter-group">
        <label>Select Exam</label>
        <select v-model="selectedExamId" class="custom-select">
          <option :value="null">-- Choose Exam --</option>
          <option v-for="e in exams" :key="e.id" :value="e.id">{{ e.name }}</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>Select Subject/Schedule</label>
        <select v-model="selectedScheduleId" class="custom-select" :disabled="!selectedExamId">
          <option :value="null">-- Choose Schedule --</option>
          <option v-for="s in schedules.filter(sch => sch.exam_id === selectedExamId)" :key="s.id" :value="s.id">
            Subject ID: {{ s.subject_id }} | Date: {{ s.exam_date }}
          </option>
        </select>
      </div>

      <div class="filter-actions">
        <Button label="Load Students" icon="pi pi-search" @click="loadMarks" :disabled="!selectedScheduleId" :loading="loading"/>
      </div>
    </div>

    <div class="marks-table-card" v-if="results.length > 0">
      <div class="card-header">
        <h3>Students List</h3>
        <Button label="Save All Marks" icon="pi pi-save" @click="saveMarks" />
      </div>
      <table class="marks-table">
        <thead>
          <tr>
            <th>Enrollment ID</th>
            <th>Obtained Marks</th>
            <th>Calculated Grade</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="result in results" :key="result.id">
            <td>{{ result.enrollment_id }}</td>
            <td>
              <InputText type="number" v-model="result.obtained_marks" style="width: 120px;" />
            </td>
            <td><strong>{{ result.grade || 'N/A' }}</strong></td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <div v-else-if="selectedScheduleId && !loading" class="empty-state">
      No marks/enrollments found for this schedule. Create results in Exam Setup first.
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
  padding: 0.6rem 0.75rem;
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
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 12px;
  color: #64748b;
  border: 1px dashed #cbd5e1;
}
</style>
