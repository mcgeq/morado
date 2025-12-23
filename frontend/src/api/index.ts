/**
 * API Client Configuration
 *
 * This module provides the base Axios configuration with interceptors
 * for request/response handling, error handling, and authentication.
 * Automatically converts between snake_case (backend) and camelCase (frontend).
 */

import axios, { type AxiosError, type AxiosInstance, type InternalAxiosRequestConfig } from 'axios';
import { keysToCamel, keysToSnake } from '@/utils/caseConverter';

// Extend Axios config to include metadata
declare module 'axios' {
  export interface InternalAxiosRequestConfig {
    metadata?: {
      startTime: Date;
    };
  }
}

// API Base Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';
const API_TIMEOUT = 30000; // 30 seconds

// Create Axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Add authentication token if available
    const token = localStorage.getItem('auth_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Convert request data from camelCase to snake_case
    if (config.data) {
      config.data = keysToSnake(config.data);
    }

    // Convert query params from camelCase to snake_case
    if (config.params) {
      config.params = keysToSnake(config.params);
    }

    // Add request timestamp for logging
    config.metadata = { startTime: new Date() };

    return config;
  },
  (error: AxiosError) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  },
);

// Response Interceptor
apiClient.interceptors.response.use(
  response => {
    // Log response time
    const config = response.config;
    if (config.metadata?.startTime) {
      const duration = Date.now() - config.metadata.startTime.getTime();
      console.debug(`API ${config.method?.toUpperCase()} ${config.url} - ${duration}ms`);
    }

    // Convert response data from snake_case to camelCase
    if (response.data) {
      response.data = keysToCamel(response.data);
    }

    return response;
  },
  (error: AxiosError) => {
    // Handle different error scenarios
    if (error.response) {
      // Convert error response data to camelCase
      if (error.response.data) {
        error.response.data = keysToCamel(error.response.data);
      }

      // Server responded with error status
      const status = error.response.status;
      const data = error.response.data as { error?: { message?: string; code?: string } };

      switch (status) {
        case 401:
          // Unauthorized - redirect to login
          console.error('Unauthorized access - redirecting to login');
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
          break;
        case 403:
          // Forbidden
          console.error('Access forbidden:', data.error?.message || 'Insufficient permissions');
          break;
        case 404:
          // Not found
          console.error('Resource not found:', error.config?.url);
          break;
        case 422:
          // Validation error
          console.error('Validation error:', data.error?.message || 'Invalid data');
          break;
        case 500:
          // Server error
          console.error('Server error:', data.error?.message || 'Internal server error');
          break;
        default:
          console.error(`API error (${status}):`, data.error?.message || error.message);
      }
    } else if (error.request) {
      // Request made but no response received
      console.error('Network error - no response received:', error.message);
    } else {
      // Error in request configuration
      console.error('Request configuration error:', error.message);
    }

    return Promise.reject(error);
  },
);

// Common API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  timestamp?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
    timestamp?: string;
    requestId?: string;
  };
}

// Export configured client
export default apiClient;
