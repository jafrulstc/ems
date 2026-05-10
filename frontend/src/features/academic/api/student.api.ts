import { useApi } from '@/composables/useApi';
import type { APIResponse, PaginatedResponse } from '@/types/api.types';
import type { Guardian, GuardianCreatePayload, GuardianUpdatePayload, Student, StudentCreatePayload, StudentUpdatePayload } from '../types/student.types';

export const studentApi = {
  // --- Guardians ---
  getGuardians(page = 1, size = 50, search?: string) {
    const searchFilter = search ? `&search=${encodeURIComponent(search)}` : '';
    return useApi().get<PaginatedResponse<Guardian>>(`/academic/guardians?page=${page}&size=${size}${searchFilter}`);
  },
  createGuardian(payload: GuardianCreatePayload) {
    return useApi().post<APIResponse<Guardian>>('/academic/guardians', payload);
  },
  updateGuardian(id: number, payload: GuardianUpdatePayload) {
    return useApi().put<APIResponse<Guardian>>(`/academic/guardians/${id}`, payload);
  },
  deleteGuardian(id: number) {
    return useApi().delete<APIResponse<null>>(`/academic/guardians/${id}`);
  },

  // --- Students ---
  getStudents(page = 1, size = 50, search?: string) {
    const searchFilter = search ? `&search=${encodeURIComponent(search)}` : '';
    return useApi().get<PaginatedResponse<Student>>(`/academic/students?page=${page}&size=${size}${searchFilter}`);
  },
  createStudent(payload: StudentCreatePayload) {
    return useApi().post<APIResponse<Student>>('/academic/students', payload);
  },
  updateStudent(id: number, payload: StudentUpdatePayload) {
    return useApi().put<APIResponse<Student>>(`/academic/students/${id}`, payload);
  },
  deleteStudent(id: number) {
    return useApi().delete<APIResponse<null>>(`/academic/students/${id}`);
  }
};
