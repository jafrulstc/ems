import axios from 'axios';
import type { AcademicSummary, ExamSummary } from '../types/reports.types';
import type { APIResponse } from '@/types/api.types';

const API_URL = import.meta.env.VITE_API_URL || '/api/v1';

export const reportsApi = {
  getAcademicSummary() {
    return axios.get<APIResponse<AcademicSummary>>(`${API_URL}/reports/academic-summary`);
  },
  getExamSummary() {
    return axios.get<APIResponse<ExamSummary>>(`${API_URL}/reports/exam-summary`);
  },
};
