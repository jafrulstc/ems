import api from '../utils/api';

export const TenantService = {
  getInstitutes: () => api.get('/institutes').then(res => res.data),
  createInstitute: (data: any) => api.post('/institutes', data).then(res => res.data),
  updateInstitute: (id: string, data: any) => api.put(`/institutes/${id}`, data).then(r => r.data),
  deleteInstitute: (id: string) => api.delete(`/institutes/${id}`).then(r => r.data),

  getBranches: () => api.get('/branches').then(res => res.data),
  createBranch: (data: any) => api.post('/branches', data).then(res => res.data),
  updateBranch: (id: string, data: any) => api.put(`/branches/${id}`, data).then(r => r.data),
  deleteBranch: (id: string) => api.delete(`/branches/${id}`).then(r => r.data),
};
