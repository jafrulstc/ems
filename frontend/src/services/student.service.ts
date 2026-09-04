import api from '../utils/api';

export const StudentService = {
  // Guardians
  getGuardians: () => api.get('/student/guardians').then(r => r.data),
  createGuardian: (data: any) => api.post('/student/guardians', data).then(r => r.data),
  updateGuardian: (id: string, data: any) => api.put(`/student/guardians/${id}`, data).then(r => r.data),
  deleteGuardian: (id: string) => api.delete(`/student/guardians/${id}`).then(r => r.data),
  // Students
  getStudents: () => api.get('/student/students').then(r => r.data),
  getNextStudentIdNo: () => api.get('/student/students/next-id').then(r => r.data.next_student_id_no as number),
  createStudent: (data: any) => api.post('/student/students', data).then(r => r.data),
  updateStudent: (id: string, data: any) => api.put(`/student/students/${id}`, data).then(r => r.data),
  deleteStudent: (id: string) => api.delete(`/student/students/${id}`).then(r => r.data),
  // Enrollments
  getEnrollments: () => api.get('/student/enrollments').then(r => r.data),
  createEnrollment: (data: any) => api.post('/student/enrollments', data).then(r => r.data),
  updateEnrollment: (id: string, data: any) => api.put(`/student/enrollments/${id}`, data).then(r => r.data),
  deleteEnrollment: (id: string) => api.delete(`/student/enrollments/${id}`).then(r => r.data),

  // Reports
  getEnrollmentReports: (params?: any) => api.get('/student/reports/enrollments', { params }).then(r => r.data),
};
