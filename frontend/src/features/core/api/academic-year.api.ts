import { useApi } from '@/composables/useApi';
import type { APIResponse, PaginatedResponse } from '@/types/api.types';
import type { AcademicYear, AcademicYearCreatePayload, AcademicYearUpdatePayload } from '../types/academic-year.types';

export const academicYearApi = {
  getAcademicYears(page = 1, size = 50) {
    return useApi().get<PaginatedResponse<AcademicYear>>(`/core/academic-years?page=${page}&size=${size}`);
  },
  createAcademicYear(payload: AcademicYearCreatePayload) {
    return useApi().post<APIResponse<AcademicYear>>('/core/academic-years', payload);
  },
  updateAcademicYear(id: number, payload: AcademicYearUpdatePayload) {
    return useApi().put<APIResponse<AcademicYear>>(`/core/academic-years/${id}`, payload);
  },
  deleteAcademicYear(id: number) {
    return useApi().delete<APIResponse<null>>(`/core/academic-years/${id}`);
  },
};
