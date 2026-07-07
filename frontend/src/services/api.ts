import axios from 'axios';

// Get the actual hostname if running in browser to support local network access
const getBaseUrl = () => {
  if (typeof window !== 'undefined') {
    // Return to using proxy URL to avoid CORS/Network issues
    return '/api-proxy/v1/';
  }
  // Server-side calls still hit Django directly
  return 'http://127.0.0.1:8000/api/v1/';
};

export const api = axios.create({
  baseURL: getBaseUrl(),
  timeout: 300000,
});

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    config.baseURL = '/api-proxy/v1/';
    const token = localStorage.getItem('access_token');
    const isAuth = config.url && (config.url.includes('auth/login') || config.url.includes('auth/register'));

    if (token && !isAuth) {
      if (!config.headers) {
        config.headers = {} as any;
      }
      if (typeof config.headers.set === 'function') {
        config.headers.set('Authorization', `Bearer ${token}`);
      } else {
        (config.headers as any).Authorization = `Bearer ${token}`;
      }
    }
  }

  // Strip leading slash to ensure Axios respects the baseURL 
  if (config.url && config.url.startsWith('/')) {
    config.url = config.url.substring(1);
  }

  return config;
});
