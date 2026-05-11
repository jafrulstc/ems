import { useApi } from '@/composables/useApi';
import type { APIResponse, PaginatedResponse } from '@/types/api.types';
import type { Enrollment, EnrollmentCreatePayload, EnrollmentUpdatePayload } from '../types/enrollment.types';

export const enrollmentApi = {
  getEnrollments(page = 1, size = 50) {
    return useApi().get<PaginatedResponse<Enrollment>>(`/academic/enrollments?page=${page}&size=${size}`);
  },
  createEnrollment(payload: EnrollmentCreatePayload) {
    return useApi().post<APIResponse<Enrollment>>('/academic/enrollments', payload);
  },
  updateEnrollment(id: number, payload: EnrollmentUpdatePayload) {
    return useApi().put<APIResponse<Enrollment>>(`/academic/enrollments/${id}`, payload);
  },
  deleteEnrollment(id: number) {
    return useApi().delete<APIResponse<null>>(`/academic/enrollments/${id}`);
  },
};
