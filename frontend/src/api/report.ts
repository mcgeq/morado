/**
 * Report API Client
 *
 * Test Report and Analytics
 * Provides functions for generating test reports and analytics.
 */

import apiClient from './index';

// Report Types
export interface ExecutionSummaryReport {
  total_executions: number;
  passed_executions: number;
  failed_executions: number;
  success_rate: number;
  average_duration: number;
  total_duration: number;
  environment?: string;
  start_date?: string;
  end_date?: string;
  test_case_count?: number;
  test_suite_count?: number;
}

export interface TestCaseReport {
  test_case_id: number;
  test_case_name: string;
  total_executions: number;
  passed_executions: number;
  failed_executions: number;
  success_rate: number;
  average_duration: number;
  last_execution?: {
    timestamp: string;
    success: boolean;
    duration: number;
    error?: string;
  };
  recent_executions: Array<{
    execution_id: number;
    timestamp: string;
    success: boolean;
    duration: number;
    environment: string;
  }>;
}

export interface TestSuiteReport {
  test_suite_id: number;
  test_suite_name: string;
  total_executions: number;
  passed_executions: number;
  failed_executions: number;
  success_rate: number;
  average_duration: number;
  test_case_count: number;
  last_execution?: {
    timestamp: string;
    success: boolean;
    duration: number;
    passed_count: number;
    failed_count: number;
  };
  recent_executions: Array<{
    execution_id: number;
    timestamp: string;
    success: boolean;
    duration: number;
    environment: string;
    passed_count: number;
    failed_count: number;
  }>;
}

export interface TrendReport {
  days: number;
  environment?: string;
  daily_trends: Array<{
    date: string;
    total_executions: number;
    passed_executions: number;
    failed_executions: number;
    success_rate: number;
    average_duration: number;
  }>;
}

export interface EnvironmentComparisonReport {
  start_date?: string;
  end_date?: string;
  environments: Array<{
    environment: string;
    total_executions: number;
    passed_executions: number;
    failed_executions: number;
    success_rate: number;
    average_duration: number;
  }>;
}

export interface FailureAnalysisReport {
  start_date?: string;
  end_date?: string;
  total_failures: number;
  top_failures: Array<{
    test_case_id: number;
    test_case_name: string;
    failure_count: number;
    failure_rate: number;
    common_errors: Array<{
      error_message: string;
      count: number;
    }>;
    last_failure: {
      timestamp: string;
      error: string;
      environment: string;
    };
  }>;
}

export interface ExecutionSummaryParams {
  start_date?: string;
  end_date?: string;
  environment?: string;
  test_case_id?: number;
  test_suite_id?: number;
}

export interface TrendReportParams {
  days?: number;
  environment?: string;
}

export interface EnvironmentComparisonParams {
  start_date?: string;
  end_date?: string;
}

export interface FailureAnalysisParams {
  start_date?: string;
  end_date?: string;
  limit?: number;
}

// Report API Functions

/**
 * Get execution summary report
 * Provides aggregated statistics about test executions within a specified time period
 */
export async function getExecutionSummaryReport(
  params?: ExecutionSummaryParams,
): Promise<ExecutionSummaryReport> {
  const response = await apiClient.get<ExecutionSummaryReport>('/reports/execution-summary', {
    params,
  });
  return response.data;
}

/**
 * Get test case execution report
 * Provides execution history and statistics for a specific test case
 */
export async function getTestCaseReport(testCaseId: number, limit = 10): Promise<TestCaseReport> {
  const response = await apiClient.get<TestCaseReport>(`/reports/test-case/${testCaseId}`, {
    params: { limit },
  });
  return response.data;
}

/**
 * Get test suite execution report
 * Provides execution history and statistics for a specific test suite
 */
export async function getTestSuiteReport(
  testSuiteId: number,
  limit = 10,
): Promise<TestSuiteReport> {
  const response = await apiClient.get<TestSuiteReport>(`/reports/test-suite/${testSuiteId}`, {
    params: { limit },
  });
  return response.data;
}

/**
 * Get execution trend report
 * Provides daily execution trends over a specified period
 */
export async function getTrendReport(params?: TrendReportParams): Promise<TrendReport> {
  const response = await apiClient.get<TrendReport>('/reports/trend', { params });
  return response.data;
}

/**
 * Get environment comparison report
 * Provides statistics comparing test executions across different environments
 */
export async function getEnvironmentComparisonReport(
  params?: EnvironmentComparisonParams,
): Promise<EnvironmentComparisonReport> {
  const response = await apiClient.get<EnvironmentComparisonReport>(
    '/reports/environment-comparison',
    { params },
  );
  return response.data;
}

/**
 * Get failure analysis report
 * Provides analysis of failed test executions, including error messages and failure patterns
 */
export async function getFailureAnalysisReport(
  params?: FailureAnalysisParams,
): Promise<FailureAnalysisReport> {
  const response = await apiClient.get<FailureAnalysisReport>('/reports/failure-analysis', {
    params,
  });
  return response.data;
}

/**
 * Export report to CSV
 */
export async function exportReportToCSV(
  reportType: 'execution-summary' | 'trend' | 'environment-comparison' | 'failure-analysis',
  params?: Record<string, unknown>,
): Promise<Blob> {
  const response = await apiClient.get(`/reports/${reportType}/export`, {
    params,
    responseType: 'blob',
  });
  return response.data;
}

/**
 * Export report to PDF
 */
export async function exportReportToPDF(
  reportType: 'execution-summary' | 'trend' | 'environment-comparison' | 'failure-analysis',
  params?: Record<string, unknown>,
): Promise<Blob> {
  const response = await apiClient.get(`/reports/${reportType}/export-pdf`, {
    params,
    responseType: 'blob',
  });
  return response.data;
}

/**
 * Get dashboard summary
 * Provides a quick overview of key metrics for the dashboard
 */
export async function getDashboardSummary(environment?: string): Promise<{
  total_test_cases: number;
  total_test_suites: number;
  recent_executions: number;
  success_rate: number;
  average_duration: number;
  trending_failures: Array<{
    test_case_id: number;
    test_case_name: string;
    failure_count: number;
  }>;
}> {
  const response = await apiClient.get('/reports/dashboard-summary', {
    params: { environment },
  });
  return response.data;
}
