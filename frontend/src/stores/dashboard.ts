/**
 * Dashboard Store
 *
 * Manages dashboard state, data fetching, and caching for the home dashboard.
 */

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from 'axios';

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

  // Computed
  const hasData = computed(() => userData.value !== null && statistics.value !== null);
  const isError = computed(() => error.value !== null);

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
  // Actions
  // ============================================================================

  /**
   * Fetch user metrics from API
   */
  async function fetchUserMetrics(): Promise<UserData> {
    try {
      const response = await axios.get<UserMetricsResponse>('/api/dashboard/user-metrics');
      return transformUserMetrics(response.data);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch user metrics';
      throw new Error(message);
    }
  }

  /**
   * Fetch step statistics from API
   */
  async function fetchStepStatistics(): Promise<StepStatistics> {
    try {
      const response = await axios.get<StepStatisticsResponse>('/api/dashboard/step-statistics');
      return transformStepStatistics(response.data);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch step statistics';
      throw new Error(message);
    }
  }

  /**
   * Fetch API usage data from API
   */
  async function fetchApiUsage(): Promise<ApiUsageData> {
    try {
      const response = await axios.get<ApiUsageResponse>('/api/dashboard/api-usage');
      return transformApiUsage(response.data);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch API usage';
      throw new Error(message);
    }
  }

  /**
   * Fetch trend data from API
   */
  async function fetchTrends(days = 7): Promise<TrendDataPoint[]> {
    try {
      const response = await axios.get<TrendsResponse>('/api/dashboard/trends', {
        params: { days },
      });
      return transformTrends(response.data);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch trends';
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
   * Refresh all dashboard data from API
   */
  async function refreshDashboard(useCache = true): Promise<void> {
    // Try to load from cache first if requested
    if (useCache && loadFromCache()) {
      // Data loaded from cache, optionally refresh in background
      return;
    }

    loading.value = true;
    error.value = null;

    try {
      // Fetch all data concurrently
      const [userMetrics, stepStats, apiUsageData, trendsData] = await Promise.all([
        fetchUserMetrics(),
        fetchStepStatistics(),
        fetchApiUsage(),
        fetchTrends(),
      ]);

      // Update state
      userData.value = userMetrics;
      statistics.value = {
        steps: stepStats,
        apiUsage: apiUsageData,
        trends: trendsData,
      };
      lastUpdated.value = new Date();

      // Cache the data
      setCacheData(userData.value, statistics.value);
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to refresh dashboard';
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
   * Reset dashboard state
   */
  function reset(): void {
    loading.value = false;
    error.value = null;
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

    // Computed
    hasData,
    isError,

    // Actions
    fetchUserMetrics,
    fetchStepStatistics,
    fetchApiUsage,
    fetchTrends,
    refreshDashboard,
    loadFromCache,
    clearError,
    reset,
  };
});
