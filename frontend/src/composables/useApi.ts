import axios from 'axios';
import type { Router } from 'vue-router';

// Default config
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // For HTTP-only refresh cookies
});

// Lazy router reference to avoid circular deps
let router: Router | null = null;

export function setApiClientRouter(r: Router) {
  router = r;
}

// Request Interceptor: Attach access token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      if (typeof config.headers.set === 'function') {
        config.headers.set('Authorization', `Bearer ${token}`);
      } else {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle 401 with token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const res = await apiClient.post('/auth/refresh');
        const newToken = res.data?.data?.access_token;
        if (newToken) {
          localStorage.setItem('access_token', newToken);
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed — clear auth and redirect
        localStorage.removeItem('access_token');
        if (router && !router.currentRoute.value.path.includes('/login')) {
          router.push({ path: '/login', query: { redirect: router.currentRoute.value.fullPath } });
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export function useApi() {
  return apiClient;
}
