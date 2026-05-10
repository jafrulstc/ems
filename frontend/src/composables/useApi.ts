import axios from 'axios';

// Default config
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptors can be added here later (e.g., for JWT injection)

export function useApi() {
  return apiClient;
}
