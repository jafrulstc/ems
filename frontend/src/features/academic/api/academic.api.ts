import { useApi } from '@/composables/useApi';
import type { APIResponse, PaginatedResponse } from '@/types/api.types';
import type {
  AcademicClass, ClassCreatePayload, ClassUpdatePayload,
  Section, SectionCreatePayload, SectionUpdatePayload,
  Subject, SubjectCreatePayload, SubjectUpdatePayload,
  ClassSubject, ClassSubjectCreatePayload, ClassSubjectUpdatePayload,
} from '../types/academic.types';

export const academicApi = {
  // --- Classes ---
  getClasses(page = 1, size = 50) {
    return useApi().get<PaginatedResponse<AcademicClass>>(`/academic/classes?page=${page}&size=${size}`);
  },
  createClass(payload: ClassCreatePayload) {
    return useApi().post<APIResponse<AcademicClass>>('/academic/classes', payload);
  },
  updateClass(id: number, payload: ClassUpdatePayload) {
    return useApi().put<APIResponse<AcademicClass>>(`/academic/classes/${id}`, payload);
  },
  deleteClass(id: number) {
    return useApi().delete<APIResponse<null>>(`/academic/classes/${id}`);
  },

  // --- Sections ---
  getSections(page = 1, size = 50, classId?: number) {
    const classFilter = classId ? `&class_id=${classId}` : '';
    return useApi().get<PaginatedResponse<Section>>(`/academic/sections?page=${page}&size=${size}${classFilter}`);
  },
  createSection(payload: SectionCreatePayload) {
    return useApi().post<APIResponse<Section>>('/academic/sections', payload);
  },
  updateSection(id: number, payload: SectionUpdatePayload) {
    return useApi().put<APIResponse<Section>>(`/academic/sections/${id}`, payload);
  },
  deleteSection(id: number) {
    return useApi().delete<APIResponse<null>>(`/academic/sections/${id}`);
  },

  // --- Subjects ---
  getSubjects(page = 1, size = 50) {
    return useApi().get<PaginatedResponse<Subject>>(`/academic/subjects?page=${page}&size=${size}`);
  },
  createSubject(payload: SubjectCreatePayload) {
    return useApi().post<APIResponse<Subject>>('/academic/subjects', payload);
  },
  updateSubject(id: number, payload: SubjectUpdatePayload) {
    return useApi().put<APIResponse<Subject>>(`/academic/subjects/${id}`, payload);
  },
  deleteSubject(id: number) {
    return useApi().delete<APIResponse<null>>(`/academic/subjects/${id}`);
  },

  // --- Class Subjects ---
  getClassSubjects(page = 1, size = 50) {
    return useApi().get<PaginatedResponse<ClassSubject>>(`/academic/class-subjects?page=${page}&size=${size}`);
  },
  getClassSubjectsByClass(classId: number) {
    return useApi().get<APIResponse<ClassSubject[]>>(`/academic/class-subjects?class_id=${classId}`);
  },
  createClassSubject(payload: ClassSubjectCreatePayload) {
    return useApi().post<APIResponse<ClassSubject>>('/academic/class-subjects', payload);
  },
  updateClassSubject(id: number, payload: ClassSubjectUpdatePayload) {
    return useApi().put<APIResponse<ClassSubject>>(`/academic/class-subjects/${id}`, payload);
  },
  deleteClassSubject(id: number) {
    return useApi().delete<APIResponse<null>>(`/academic/class-subjects/${id}`);
  },
};
