import { useApi } from '@/composables/useApi';
import type { APIResponse, PaginatedResponse } from '@/types/api.types';
import type { AcademicClass, ClassCreatePayload, ClassUpdatePayload } from '../types/academic.types';

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
  }
};
