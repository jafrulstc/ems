import { useApi } from '@/composables/useApi';
import type { APIResponse, PaginatedResponse } from '@/types/api.types';
import type {
  ExamType, ExamTypeCreatePayload, ExamTypeUpdatePayload,
  ExamBoard, ExamBoardCreatePayload, ExamBoardUpdatePayload,
  Routine, RoutineCreatePayload, RoutineUpdatePayload,
  GradingSystem, GradingSystemCreatePayload, GradingSystemUpdatePayload,
  GradingRuleCreatePayload, GradingRule,
  Mark, MarkBulkCreatePayload,
  AttendanceRecord, AttendanceBulkCreatePayload,
  Result, ResultGeneratePayload,
  ExamRegistration, ExamRegistrationCreatePayload, ExamRegistrationUpdatePayload,
} from '../types/exam.types';

export const examApi = {
  // ── Exam Types ──────────────────────────────────────────────────────────────
  getExamTypes(page = 1, size = 50) {
    return useApi().get<PaginatedResponse<ExamType>>(`/exam/exam-types?page=${page}&size=${size}`);
  },
  createExamType(payload: ExamTypeCreatePayload) {
    return useApi().post<APIResponse<ExamType>>('/exam/exam-types', payload);
  },
  updateExamType(id: number, payload: ExamTypeUpdatePayload) {
    return useApi().put<APIResponse<ExamType>>(`/exam/exam-types/${id}`, payload);
  },
  deleteExamType(id: number) {
    return useApi().delete<APIResponse<null>>(`/exam/exam-types/${id}`);
  },

  // ── Exam Boards ─────────────────────────────────────────────────────────────
  getExamBoards(page = 1, size = 50) {
    return useApi().get<PaginatedResponse<ExamBoard>>(`/exam/exam-boards?page=${page}&size=${size}`);
  },
  createExamBoard(payload: ExamBoardCreatePayload) {
    return useApi().post<APIResponse<ExamBoard>>('/exam/exam-boards', payload);
  },
  updateExamBoard(id: number, payload: ExamBoardUpdatePayload) {
    return useApi().put<APIResponse<ExamBoard>>(`/exam/exam-boards/${id}`, payload);
  },
  deleteExamBoard(id: number) {
    return useApi().delete<APIResponse<null>>(`/exam/exam-boards/${id}`);
  },

  // ── Routines ────────────────────────────────────────────────────────────────
  getRoutines(page = 1, size = 50) {
    return useApi().get<PaginatedResponse<Routine>>(`/exam/routines?page=${page}&size=${size}`);
  },
  getRoutinesByExam(examTypeId: number) {
    return useApi().get<APIResponse<Routine[]>>(`/exam/routines/by-exam/${examTypeId}`);
  },
  createRoutine(payload: RoutineCreatePayload) {
    return useApi().post<APIResponse<Routine>>('/exam/routines', payload);
  },
  updateRoutine(id: number, payload: RoutineUpdatePayload) {
    return useApi().put<APIResponse<Routine>>(`/exam/routines/${id}`, payload);
  },
  deleteRoutine(id: number) {
    return useApi().delete<APIResponse<null>>(`/exam/routines/${id}`);
  },

  // ── Grading Systems ─────────────────────────────────────────────────────────
  getGradingSystems(page = 1, size = 50) {
    return useApi().get<PaginatedResponse<GradingSystem>>(`/exam/grading-systems?page=${page}&size=${size}`);
  },
  createGradingSystem(payload: GradingSystemCreatePayload) {
    return useApi().post<APIResponse<GradingSystem>>('/exam/grading-systems', payload);
  },
  updateGradingSystem(id: number, payload: GradingSystemUpdatePayload) {
    return useApi().put<APIResponse<GradingSystem>>(`/exam/grading-systems/${id}`, payload);
  },
  deleteGradingSystem(id: number) {
    return useApi().delete<APIResponse<null>>(`/exam/grading-systems/${id}`);
  },
  addGradingRule(systemId: number, payload: GradingRuleCreatePayload) {
    return useApi().post<APIResponse<GradingRule>>(`/exam/grading-systems/${systemId}/rules`, payload);
  },

  // ── Marks ───────────────────────────────────────────────────────────────────
  getMarks(page = 1, size = 50) {
    return useApi().get<PaginatedResponse<Mark>>(`/exam/marks?page=${page}&size=${size}`);
  },
  getMarksBySubject(examTypeId: number, classSubjectId: number) {
    return useApi().get<APIResponse<Mark[]>>(`/exam/marks/by-subject?exam_type_id=${examTypeId}&class_subject_id=${classSubjectId}`);
  },
  bulkCreateMarks(payload: MarkBulkCreatePayload) {
    return useApi().post<APIResponse<Mark[]>>('/exam/marks/bulk', payload);
  },
  deleteMark(id: number) {
    return useApi().delete<APIResponse<null>>(`/exam/marks/${id}`);
  },

  // ── Attendance ──────────────────────────────────────────────────────────────
  bulkCreateAttendance(payload: AttendanceBulkCreatePayload) {
    return useApi().post<APIResponse<AttendanceRecord[]>>('/exam/attendance/bulk', payload);
  },
  getAttendance(enrollmentId: number, fromDate: string, toDate: string) {
    return useApi().get<APIResponse<AttendanceRecord[]>>(`/exam/attendance?enrollment_id=${enrollmentId}&from_date=${fromDate}&to_date=${toDate}`);
  },

  // ── Results ─────────────────────────────────────────────────────────────────
  generateResults(payload: ResultGeneratePayload) {
    return useApi().post<APIResponse<Result[]>>('/exam/results/generate', payload);
  },
  getResults(examTypeId: number) {
    return useApi().get<APIResponse<Result[]>>(`/exam/results?exam_type_id=${examTypeId}`);
  },

  // ── Exam Registrations ──────────────────────────────────────────────────────
  getExamRegistrations(page = 1, size = 50) {
    return useApi().get<PaginatedResponse<ExamRegistration>>(`/exam/exam-registrations?page=${page}&size=${size}`);
  },
  getRegistrationsByExam(examTypeId: number) {
    return useApi().get<APIResponse<ExamRegistration[]>>(`/exam/exam-registrations/by-exam/${examTypeId}`);
  },
  createExamRegistration(payload: ExamRegistrationCreatePayload) {
    return useApi().post<APIResponse<ExamRegistration>>('/exam/exam-registrations', payload);
  },
  updateExamRegistration(id: number, payload: ExamRegistrationUpdatePayload) {
    return useApi().put<APIResponse<ExamRegistration>>(`/exam/exam-registrations/${id}`, payload);
  },
  deleteExamRegistration(id: number) {
    return useApi().delete<APIResponse<null>>(`/exam/exam-registrations/${id}`);
  },
};
