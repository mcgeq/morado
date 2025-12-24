/**
 * Dashboard Store
 *
 * Manages dashboard state, data fetching, and caching for the home dashboard.
 */

import axios from 'axios';
import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { memoize } from '@/utils/performance';

// ============================================================================
// Type Definitions
// ============================================================================

export interface UserData {
  id: string;
  username: string;
  avatar: string | null;
  registrationDate: string;
  metrics: UserMetrics;
}

export interface UserMetrics {
  totalExecutions: number;
  passedTests: number;
  failedTests: number;
}

export interface StepStatistics {
  completed: number;
  sqlFailed: number;
  apiRequest: number;
}

export interface ApiUsageData {
  apiCompletion: {
    percentage: number;
    totalApis: number;
    completedApis: number;
    taggedApis: number;
  };
  testCaseCompletion: {
    percentage: number;
    totalTestCases: number;
    passedTestCases: number;
    taggedTestCases: number;
  };
}

export interface TrendDataPoint {
  date: string; // YYYY-MM-DD format
  scheduledComponents: number;
  testCaseComponents: number;
  actualComponents: number;
  detectionComponents: number;
}

export interface DashboardStatistics {
  steps: StepStatistics;
  apiUsage: ApiUsageData;
  trends: TrendDataPoint[];
}

export interface DashboardState {
  loading: boolean;
  error: string | null;
  lastUpdated: Date | null;
  userData: UserData | null;
  statistics: DashboardStatistics | null;
}

// API Response Types
export interface UserMetricsResponse {
  user_id: string;
  username: string;
  avatar_url: string | null;
  registration_date: string;
  total_executions: number;
  passed_tests: number;
  failed_tests: number;
}

export interface StepStatisticsResponse {
  completed: number;
  sql_failed: number;
  api_request: number;
  total: number;
}

export interface ApiUsageResponse {
  api_completion_rate: number;
  total_apis: number;
  completed_apis: number;
  tagged_apis: number;
  test_case_completion_rate: number;
  total_test_cases: number;
  passed_test_cases: number;
  tagged_test_cases: number;
}

export interface TrendsResponse {
  data: Array<{
    date: string;
    scheduled_components: number;
    test_case_components: number;
    actual_components: number;
    detection_components: number;
  }>;
}

// Cache Types
interface CacheData {
  userData: UserData;
  statistics: DashboardStatistics;
  timestamp: number;
}

// ============================================================================
// Cache Utilities
// ============================================================================

const CACHE_KEY = 'dashboard_cache';
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes in milliseconds

/**
 * Check if cached data is still valid (less than 5 minutes old)
 */
export function isCacheValid(): boolean {
  try {
    const cached = localStorage.getItem(CACHE_KEY);
    if (!cached) return false;

    const cacheData: CacheData = JSON.parse(cached);
    const now = Date.now();
    const age = now - cacheData.timestamp;

    return age < CACHE_DURATION;
  } catch {
    return false;
  }
}

/**
 * Get cached dashboard data if valid
 */
export function getCacheData(): CacheData | null {
  try {
    if (!isCacheValid()) return null;

    const cached = localStorage.getItem(CACHE_KEY);
    if (!cached) return null;

    return JSON.parse(cached);
  } catch {
    return null;
  }
}

/**
 * Set cache data with current timestamp
 */
export function setCacheData(userData: UserData, statistics: DashboardStatistics): void {
  try {
    const cacheData: CacheData = {
      userData,
      statistics,
      timestamp: Date.now(),
    };
    localStorage.setItem(CACHE_KEY, JSON.stringify(cacheData));
  } catch (error) {
    console.error('Failed to cache dashboard data:', error);
  }
}

/**
 * Clear cached dashboard data
 */
export function clearCache(): void {
  try {
    localStorage.removeItem(CACHE_KEY);
  } catch (error) {
    console.error('Failed to clear dashboard cache:', error);
  }
}

// ============================================================================
// Dashboard Store
// ============================================================================

export const useDashboardStore = defineStore('dashboard', () => {
  // State
  const loading = ref(false);
  const error = ref<string | null>(null);
  const lastUpdated = ref<Date | null>(null);
  const userData = ref<UserData | null>(null);
  const statistics = ref<DashboardStatistics | null>(null);
  const partialErrors = ref<Record<string, string>>({});

  // Computed
  const hasData = computed(() => userData.value !== null && statistics.value !== null);
  const isError = computed(() => error.value !== null);
  const hasPartialErrors = computed(() => Object.keys(partialErrors.value).length > 0);

  // ============================================================================
  // API Transformation Functions
  // ============================================================================

  function transformUserMetrics(response: UserMetricsResponse): UserData {
    return {
      id: response.user_id,
      username: response.username,
      avatar: response.avatar_url,
      registrationDate: response.registration_date,
      metrics: {
        totalExecutions: response.total_executions,
        passedTests: response.passed_tests,
        failedTests: response.failed_tests,
      },
    };
  }

  function transformStepStatistics(response: StepStatisticsResponse): StepStatistics {
    return {
      completed: response.completed,
      sqlFailed: response.sql_failed,
      apiRequest: response.api_request,
    };
  }

  function transformApiUsage(response: ApiUsageResponse): ApiUsageData {
    return {
      apiCompletion: {
        percentage: response.api_completion_rate,
        totalApis: response.total_apis,
        completedApis: response.completed_apis,
        taggedApis: response.tagged_apis,
      },
      testCaseCompletion: {
        percentage: response.test_case_completion_rate,
        totalTestCases: response.total_test_cases,
        passedTestCases: response.passed_test_cases,
        taggedTestCases: response.tagged_test_cases,
      },
    };
  }

  function transformTrends(response: TrendsResponse): TrendDataPoint[] {
    return response.data.map(item => ({
      date: item.date,
      scheduledComponents: item.scheduled_components,
      testCaseComponents: item.test_case_components,
      actualComponents: item.actual_components,
      detectionComponents: item.detection_components,
    }));
  }

  // ============================================================================
  // Retry Configuration
  // ============================================================================

  const MAX_RETRIES = 3;
  const RETRY_DELAY = 1000; // 1 second

  /**
   * Retry a function with exponential backoff
   */
  async function retryWithBackoff<T>(
    fn: () => Promise<T>,
    retries = MAX_RETRIES,
    delay = RETRY_DELAY,
  ): Promise<T> {
    try {
      return await fn();
    } catch (error) {
      if (retries <= 0) {
        throw error;
      }

      // Wait with exponential backoff
      await new Promise(resolve => setTimeout(resolve, delay));

      // Retry with increased delay
      return retryWithBackoff(fn, retries - 1, delay * 2);
    }
  }

  /**
   * Handle API errors and extract meaningful error messages
   */
  function handleApiError(error: unknown, defaultMessage: string): string {
    if (axios.isAxiosError(error)) {
      // Handle specific HTTP status codes
      if (error.response) {
        switch (error.response.status) {
          case 401:
            return '会话已过期，请重新登录';
          case 403:
            return '您没有权限访问此数据';
          case 404:
            return '请求的数据不存在';
          case 500:
            return '服务器错误，请稍后重试';
          case 503:
            return '服务暂时不可用，请稍后重试';
          default:
            return error.response.data?.message || defaultMessage;
        }
      } else if (error.request) {
        return '网络连接失败，请检查您的网络';
      }
    }

    return error instanceof Error ? error.message : defaultMessage;
  }

  // ============================================================================
  // Actions
  // ============================================================================

  /**
   * Fetch user metrics from API with retry logic
   */
  async function fetchUserMetrics(): Promise<UserData> {
    try {
      const response = await retryWithBackoff(() =>
        axios.get<UserMetricsResponse>('/api/dashboard/user-metrics'),
      );

      // Validate response data
      if (!response.data || typeof response.data.user_id !== 'string') {
        throw new Error('Invalid user metrics data received');
      }

      return transformUserMetrics(response.data);
    } catch (err) {
      const message = handleApiError(err, '获取用户指标失败');
      throw new Error(message);
    }
  }

  /**
   * Fetch step statistics from API with retry logic
   */
  async function fetchStepStatistics(): Promise<StepStatistics> {
    try {
      const response = await retryWithBackoff(() =>
        axios.get<StepStatisticsResponse>('/api/dashboard/step-statistics'),
      );

      // Validate response data
      if (!response.data || typeof response.data.completed !== 'number') {
        throw new Error('Invalid step statistics data received');
      }

      return transformStepStatistics(response.data);
    } catch (err) {
      const message = handleApiError(err, '获取步骤统计失败');
      throw new Error(message);
    }
  }

  /**
   * Fetch API usage data from API with retry logic
   */
  async function fetchApiUsage(): Promise<ApiUsageData> {
    try {
      const response = await retryWithBackoff(() =>
        axios.get<ApiUsageResponse>('/api/dashboard/api-usage'),
      );

      // Validate response data
      if (!response.data || typeof response.data.api_completion_rate !== 'number') {
        throw new Error('Invalid API usage data received');
      }

      return transformApiUsage(response.data);
    } catch (err) {
      const message = handleApiError(err, '获取API使用情况失败');
      throw new Error(message);
    }
  }

  /**
   * Fetch trend data from API with retry logic
   */
  async function fetchTrends(days = 7): Promise<TrendDataPoint[]> {
    try {
      const response = await retryWithBackoff(() =>
        axios.get<TrendsResponse>('/api/dashboard/trends', {
          params: { days },
        }),
      );

      // Validate response data
      if (!response.data || !Array.isArray(response.data.data)) {
        throw new Error('Invalid trends data received');
      }

      return transformTrends(response.data);
    } catch (err) {
      const message = handleApiError(err, '获取趋势数据失败');
      throw new Error(message);
    }
  }

  /**
   * Load dashboard data from cache if available and valid
   */
  function loadFromCache(): boolean {
    const cached = getCacheData();
    if (cached) {
      userData.value = cached.userData;
      statistics.value = cached.statistics;
      lastUpdated.value = new Date(cached.timestamp);
      return true;
    }
    return false;
  }

  /**
   * Refresh all dashboard data from API with partial failure handling
   */
  async function refreshDashboard(useCache = true): Promise<void> {
    // Try to load from cache first if requested
    if (useCache && loadFromCache()) {
      // Data loaded from cache, optionally refresh in background
      return;
    }

    loading.value = true;
    error.value = null;
    partialErrors.value = {};

    try {
      // Fetch all data concurrently with individual error handling
      const results = await Promise.allSettled([
        fetchUserMetrics(),
        fetchStepStatistics(),
        fetchApiUsage(),
        fetchTrends(),
      ]);

      // Process results and handle partial failures
      const [userMetricsResult, stepStatsResult, apiUsageResult, trendsResult] = results;

      // Handle user metrics
      if (userMetricsResult.status === 'fulfilled') {
        userData.value = userMetricsResult.value;
      } else {
        partialErrors.value.userMetrics = userMetricsResult.reason.message;
        console.error('Failed to fetch user metrics:', userMetricsResult.reason);
      }

      // Handle step statistics
      let stepStats: StepStatistics | null = null;
      if (stepStatsResult.status === 'fulfilled') {
        stepStats = stepStatsResult.value;
      } else {
        partialErrors.value.stepStatistics = stepStatsResult.reason.message;
        console.error('Failed to fetch step statistics:', stepStatsResult.reason);
      }

      // Handle API usage
      let apiUsageData: ApiUsageData | null = null;
      if (apiUsageResult.status === 'fulfilled') {
        apiUsageData = apiUsageResult.value;
      } else {
        partialErrors.value.apiUsage = apiUsageResult.reason.message;
        console.error('Failed to fetch API usage:', apiUsageResult.reason);
      }

      // Handle trends
      let trendsData: TrendDataPoint[] | null = null;
      if (trendsResult.status === 'fulfilled') {
        trendsData = trendsResult.value;
      } else {
        partialErrors.value.trends = trendsResult.reason.message;
        console.error('Failed to fetch trends:', trendsResult.reason);
      }

      // Update statistics if at least some data was fetched
      if (stepStats || apiUsageData || trendsData) {
        statistics.value = {
          steps: stepStats || { completed: 0, sqlFailed: 0, apiRequest: 0 },
          apiUsage: apiUsageData || {
            apiCompletion: {
              percentage: 0,
              totalApis: 0,
              completedApis: 0,
              taggedApis: 0,
            },
            testCaseCompletion: {
              percentage: 0,
              totalTestCases: 0,
              passedTestCases: 0,
              taggedTestCases: 0,
            },
          },
          trends: trendsData || [],
        };
      }

      // Check if all requests failed
      if (results.every(result => result.status === 'rejected')) {
        throw new Error('所有数据加载失败，请检查网络连接或稍后重试');
      }

      lastUpdated.value = new Date();

      // Cache the data if we have complete data
      if (userData.value && statistics.value && Object.keys(partialErrors.value).length === 0) {
        setCacheData(userData.value, statistics.value);
      }
    } catch (err) {
      error.value = handleApiError(err, '刷新仪表板失败');
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Clear error state
   */
  function clearError(): void {
    error.value = null;
  }

  /**
   * Clear partial errors
   */
  function clearPartialErrors(): void {
    partialErrors.value = {};
  }

  /**
   * Reset dashboard state
   */
  function reset(): void {
    loading.value = false;
    error.value = null;
    partialErrors.value = {};
    lastUpdated.value = null;
    userData.value = null;
    statistics.value = null;
    clearCache();
  }

  // Return store interface
  return {
    // State
    loading,
    error,
    lastUpdated,
    userData,
    statistics,
    partialErrors,

    // Computed
    hasData,
    isError,
    hasPartialErrors,

    // Actions
    fetchUserMetrics,
    fetchStepStatistics,
    fetchApiUsage,
    fetchTrends,
    refreshDashboard,
    loadFromCache,
    clearError,
    clearPartialErrors,
    reset,
  };
});
