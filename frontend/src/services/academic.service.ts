import api from '../utils/api';

export const AcademicService = {
  // Departments
  getDepartments: (params?: any) => api.get('/academic/departments', { params }).then(r => r.data),
  createDepartment: (data: any) => api.post('/academic/departments', data).then(r => r.data),
  updateDepartment: (id: string, data: any) => api.put(`/academic/departments/${id}`, data).then(r => r.data),
  deleteDepartment: (id: string) => api.delete(`/academic/departments/${id}`).then(r => r.data),
  
  // Years
  getYears: (params?: any) => api.get('/academic/years', { params }).then(r => r.data),
  createYear: (data: any) => api.post('/academic/years', data).then(r => r.data),
  updateYear: (id: string, data: any) => api.put(`/academic/years/${id}`, data).then(r => r.data),
  deleteYear: (id: string) => api.delete(`/academic/years/${id}`).then(r => r.data),

  // Classes
  getClasses: (params?: any) => api.get('/academic/classes', { params }).then(r => r.data),
  createClass: (data: any) => api.post('/academic/classes', data).then(r => r.data),
  updateClass: (id: string, data: any) => api.put(`/academic/classes/${id}`, data).then(r => r.data),
  deleteClass: (id: string) => api.delete(`/academic/classes/${id}`).then(r => r.data),

  // Sections
  getSections: (params?: any) => api.get('/academic/sections', { params }).then(r => r.data),
  createSection: (data: any) => api.post('/academic/sections', data).then(r => r.data),
  updateSection: (id: string, data: any) => api.put(`/academic/sections/${id}`, data).then(r => r.data),
  deleteSection: (id: string) => api.delete(`/academic/sections/${id}`).then(r => r.data),

  // Subjects
  getSubjects: (params?: any) => api.get('/academic/subjects', { params }).then(r => r.data),
  createSubject: (data: any) => api.post('/academic/subjects', data).then(r => r.data),
  updateSubject: (id: string, data: any) => api.put(`/academic/subjects/${id}`, data).then(r => r.data),
  deleteSubject: (id: string) => api.delete(`/academic/subjects/${id}`).then(r => r.data),

  // Shifts
  getShifts: (params?: any) => api.get('/academic/shifts', { params }).then(r => r.data),
  createShift: (data: any) => api.post('/academic/shifts', data).then(r => r.data),
  updateShift: (id: string, data: any) => api.put(`/academic/shifts/${id}`, data).then(r => r.data),
  deleteShift: (id: string) => api.delete(`/academic/shifts/${id}`).then(r => r.data),

  // Yearly Class Subjects
  getYearlyClassSubjects: (params?: any) => api.get('/academic/yearly-class-subjects', { params }).then(r => r.data),
  createYearlyClassSubject: (data: any) => api.post('/academic/yearly-class-subjects', data).then(r => r.data),
  updateYearlyClassSubject: (id: string, data: any) => api.put(`/academic/yearly-class-subjects/${id}`, data).then(r => r.data),
  deleteYearlyClassSubject: (id: string) => api.delete(`/academic/yearly-class-subjects/${id}`).then(r => r.data),
};
