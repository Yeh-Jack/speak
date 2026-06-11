import axios from 'axios';

declare global {
  interface Window {
    __API_URL__?: string;
    __API_CONFIG_PROMISE__?: Promise<void>;
  }
}

// Fetch config once at startup
if (typeof window !== 'undefined' && !window.__API_CONFIG_PROMISE__) {
  window.__API_CONFIG_PROMISE__ = fetch('/config.js')
    .then(r => r.text())
    .then(text => {
      const match = text.match(/window\.__API_URL__\s*=\s*['"]([^'"]+)['"]/);
      if (match && match[1] && match[1] !== '__BACKEND_API_URL__' && match[1].includes('://')) {
        window.__API_URL__ = match[1];
      }
    })
    .catch(() => {
      // Config fetch failed, use same-origin
    });
}

export const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to ensure config is loaded before making requests
api.interceptors.request.use(async (config) => {
  if (window.__API_CONFIG_PROMISE__) {
    await window.__API_CONFIG_PROMISE__;
  }
  if (window.__API_URL__ && window.__API_URL__.includes('://')) {
    config.baseURL = `${window.__API_URL__}/api/v1`;
  }
  return config;
}, (error) => Promise.reject(error));

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Ignore cancellation errors (happens during navigation/unmount)
    if (error.name === 'CanceledError' || error.code === 'ERR_CANCELED') {
      return Promise.reject(error);
    }
    console.error('API error:', error.config?.url, error.response?.status, error.message);
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
