// lib/apiClient.js
import axios from 'axios';
import { auth } from '@/firebase/config';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to automatically add Firebase Auth token
apiClient.interceptors.request.use(
  async (config) => {
    try {
      // Get current user and token
      const currentUser = auth.currentUser;
      if (currentUser) {
        const token = await currentUser.getIdToken();
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.warn('Failed to get auth token:', error);
      // Continue with request without token rather than failing
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for centralized error handling
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Centralized error handling
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      
      switch (status) {
        case 401:
          console.error('Unauthorized access - please sign in again');
          // Could trigger logout or redirect to signin here
          break;
        case 403:
          console.error('Forbidden - insufficient permissions');
          break;
        case 404:
          console.error('Resource not found');
          break;
        case 500:
          console.error('Internal server error');
          break;
        default:
          console.error(`API Error ${status}:`, data?.message || error.message);
      }
      
      // Enhance error with user-friendly message
      error.userMessage = data?.message || getErrorMessage(status);
    } else if (error.request) {
      // Request was made but no response received
      console.error('Network error - no response received:', error.message);
      error.userMessage = 'Network error. Please check your connection and try again.';
    } else {
      // Something else happened
      console.error('Request setup error:', error.message);
      error.userMessage = 'An unexpected error occurred. Please try again.';
    }
    
    return Promise.reject(error);
  }
);

// Helper function to get user-friendly error messages
function getErrorMessage(status) {
  switch (status) {
    case 400:
      return 'Invalid request. Please check your input and try again.';
    case 401:
      return 'Please sign in to continue.';
    case 403:
      return 'You do not have permission to perform this action.';
    case 404:
      return 'The requested resource was not found.';
    case 500:
      return 'Server error. Please try again later.';
    default:
      return 'An error occurred. Please try again.';
  }
}

// Helper methods for common API operations
export const api = {
  // Basic HTTP methods
  get: (url, config) => apiClient.get(url, config),
  post: (url, data, config) => apiClient.post(url, data, config),
  put: (url, data, config) => apiClient.put(url, data, config),
  patch: (url, data, config) => apiClient.patch(url, data, config),
  delete: (url, config) => apiClient.delete(url, config),

  // File upload helper
  uploadFile: (url, file, onUploadProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    
    return apiClient.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
  },

  // Helper for external API calls (without base URL)
  external: {
    get: (url, config) => axios.get(url, config),
    post: (url, data, config) => axios.post(url, data, config),
    put: (url, data, config) => axios.put(url, data, config),
    delete: (url, config) => axios.delete(url, config),
  },
};

// Export the configured axios instance for advanced use cases
export default apiClient;