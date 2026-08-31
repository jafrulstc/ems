import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  const tenantSlug = localStorage.getItem('tenant_slug');
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  // Login বাদে অন্যান্য সব API কল-এ X-Tenant-Slug পাঠাবো
  if (tenantSlug && !config.url?.includes('/auth/login')) {
    config.headers['X-Tenant-Slug'] = tenantSlug;
  }
  
  return config;
});

export default api;
