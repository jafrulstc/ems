import api from '../utils/api';

export const ExamService = {
  // Grading Scales
  getGradingScales: () => api.get('/exam/grading-scales').then(r => r.data),
  createGradingScale: (data: any) => api.post('/exam/grading-scales', data).then(r => r.data),
  updateGradingScale: (id: string, data: any) => api.put(`/exam/grading-scales/${id}`, data).then(r => r.data),
  deleteGradingScale: (id: string) => api.delete(`/exam/grading-scales/${id}`).then(r => r.data),
  // Exams
  getExams: () => api.get('/exam/').then(r => r.data),
  getExamSubjects: (exam_id: string) => api.get(`/exam/${exam_id}/subjects`).then(r => r.data),
  createExam: (data: any) => api.post('/exam/', data).then(r => r.data),
  updateExam: (id: string, data: any) => api.put(`/exam/${id}`, data).then(r => r.data),
  deleteExam: (id: string) => api.delete(`/exam/${id}`).then(r => r.data),
  // Schedules
  getSchedules: () => api.get('/exam/schedules').then(r => r.data),
  createSchedule: (data: any) => api.post('/exam/schedules', data).then(r => r.data),
  updateSchedule: (id: string, data: any) => api.put(`/exam/schedules/${id}`, data).then(r => r.data),
  deleteSchedule: (id: string) => api.delete(`/exam/schedules/${id}`).then(r => r.data),
  // Results
  getResults: () => api.get('/exam/results').then(r => r.data),
  createResult: (data: any) => api.post('/exam/results', data).then(r => r.data),
  updateResult: (id: string, data: any) => api.put(`/exam/results/${id}`, data).then(r => r.data),
  deleteResult: (id: string) => api.delete(`/exam/results/${id}`).then(r => r.data),
  
  // Exam Types
  getExamTypes: () => api.get('/exam/types').then(r => r.data),
  createExamType: (data: any) => api.post('/exam/types', data).then(r => r.data),
  updateExamType: (id: string, data: any) => api.put(`/exam/types/${id}`, data).then(r => r.data),
  deleteExamType: (id: string) => api.delete(`/exam/types/${id}`).then(r => r.data),

  // Utilities / Logic
  generateResults: (exam_id: string) => api.post('/exam/results/generate', { exam_id }).then(r => r.data),
  getMeritList: (params: { exam_id?: string, academic_year_id?: string, class_id?: string }) => api.get('/exam/reports/merit-list', { params }).then(r => r.data),
};
