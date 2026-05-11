<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Tag from 'primevue/tag';
import PageHeader from '@/components/shared/PageHeader.vue';
import EmptyState from '@/components/shared/EmptyState.vue';
import { enrollmentApi } from '../api/enrollment.api';
import { studentApi } from '../api/student.api';
import { academicApi } from '../api/academic.api';
import { academicYearApi } from '@/features/core/api/academic-year.api';
import type { Enrollment } from '../types/enrollment.types';
import type { Student } from '../types/student.types';
import type { Section, AcademicClass } from '../types/academic.types';
import type { AcademicYear } from '@/features/core/types/academic-year.types';
import EnrollmentFormDialog from '../components/EnrollmentFormDialog.vue';
import { usePermission } from '@/features/auth/composables/usePermission';

const { hasPermission } = usePermission();
const canEdit = hasPermission('academic.enrollments.edit');
const canCreate = hasPermission('academic.enrollments.create');
const canDelete = hasPermission('academic.enrollments.delete');

const enrollments = ref<Enrollment[]>([]);
const students = ref<Student[]>([]);
const sections = ref<Section[]>([]);
const classes = ref<AcademicClass[]>([]);
const academicYears = ref<AcademicYear[]>([]);
const loading = ref(false);
const dialogVisible = ref(false);
const editingItem = ref<Enrollment | null>(null);

const studentMap = computed(() => new Map(students.value.map(s => [s.id, s.full_name])));
const sectionMap = computed(() => new Map(sections.value.map(s => [s.id, s.name])));
const yearMap = computed(() => new Map(academicYears.value.map(y => [y.id, y.name])));

const fetchEnrollments = async () => {
  loading.value = true;
  try {
    const res = await enrollmentApi.getEnrollments(1, 100);
    enrollments.value = res.data.data?.items ?? [];
  } catch (e) { console.error(e); } finally { loading.value = false; }
};

const fetchLookups = async () => {
  try {
    const [stuRes, secRes, clRes, ayRes] = await Promise.all([
      studentApi.getStudents(1, 100),
      academicApi.getSections(1, 100),
      academicApi.getClasses(1, 100),
      academicYearApi.getAcademicYears(1, 100),
    ]);
    students.value = stuRes.data.data?.items ?? [];
    sections.value = secRes.data.data?.items ?? [];
    classes.value = clRes.data.data?.items ?? [];
    academicYears.value = ayRes.data.data?.items ?? [];
  } catch (e) { console.error(e); }
};

onMounted(() => { fetchEnrollments(); fetchLookups(); });

const openNew = () => { editingItem.value = null; dialogVisible.value = true; };
const edit = (data: Enrollment) => { editingItem.value = data; dialogVisible.value = true; };

const remove = async (id: number) => {
  if (!confirm('Delete this enrollment?')) return;
  try { await enrollmentApi.deleteEnrollment(id); fetchEnrollments(); } catch (e) { console.error(e); }
};
</script>

<template>
  <div>
    <PageHeader title="Enrollments" subtitle="Manage student enrollments" icon="pi pi-user-plus">
      <template #actions>
        <Button v-if="canCreate" label="Enroll Student" icon="pi pi-plus" @click="openNew" />
      </template>
    </PageHeader>

    <div class="ems-card">
      <DataTable v-if="enrollments.length" :value="enrollments" :loading="loading" stripedRows responsiveLayout="scroll">
        <Column header="Student" sortable>
          <template #body="{ data }">{{ studentMap.get(data.student_id) ?? data.student_id }}</template>
        </Column>
        <Column header="Section" sortable>
          <template #body="{ data }">{{ sectionMap.get(data.section_id) ?? data.section_id }}</template>
        </Column>
        <Column header="Academic Year" sortable>
          <template #body="{ data }">{{ yearMap.get(data.academic_year_id) ?? data.academic_year_id }}</template>
        </Column>
        <Column field="roll_no" header="Roll No" sortable>
          <template #body="{ data }">{{ data.roll_no || '—' }}</template>
        </Column>
        <Column header="Status" style="width: 8rem">
          <template #body="{ data }">
            <Tag :severity="data.is_active ? 'success' : 'danger'" :value="data.is_active ? 'Active' : 'Inactive'" />
          </template>
        </Column>
        <Column v-if="canEdit || canDelete" :exportable="false" style="min-width:10rem">
          <template #body="{ data }">
            <Button v-if="canEdit" icon="pi pi-pencil" text rounded severity="success" class="mr-1" @click="edit(data)" />
            <Button v-if="canDelete" icon="pi pi-trash" text rounded severity="danger" @click="remove(data.id)" />
          </template>
        </Column>
      </DataTable>
      <EmptyState v-else icon="pi pi-user-plus" title="No enrollments" description="Enroll students to academic years and sections" />
    </div>

    <EnrollmentFormDialog v-model:visible="dialogVisible" :edit-data="editingItem" @saved="fetchEnrollments" />
  </div>
</template>
