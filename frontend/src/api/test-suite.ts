/**
 * Test Suite API Client
 *
 * Test Suite Management and Execution
 * Provides functions for managing test suites that group multiple test cases.
 */

import apiClient, { type PaginatedResponse } from './index';

// Test Suite Types
export interface TestSuite {
  id: number;
  uuid: string;
  name: string;
  description?: string;
  execution_order: string;
  parallel_execution: boolean;
  continue_on_failure: boolean;
  schedule_config?: Record<string, unknown>;
  is_scheduled: boolean;
  environment: string;
  global_variables?: Record<string, unknown>;
  tags?: string[];
  version: string;
  created_by?: number;
  created_at: string;
  updated_at: string;
}

export interface TestSuiteCreate {
  name: string;
  description?: string;
  execution_order?: string;
  parallel_execution?: boolean;
  continue_on_failure?: boolean;
  schedule_config?: Record<string, unknown>;
  is_scheduled?: boolean;
  environment?: string;
  global_variables?: Record<string, unknown>;
  tags?: string[];
  version?: string;
  created_by?: number;
}

export interface TestSuiteUpdate {
  name?: string;
  description?: string;
  execution_order?: string;
  parallel_execution?: boolean;
  continue_on_failure?: boolean;
  schedule_config?: Record<string, unknown>;
  is_scheduled?: boolean;
  environment?: string;
  global_variables?: Record<string, unknown>;
  tags?: string[];
  version?: string;
}

export interface TestSuiteCase {
  id: number;
  test_suite_id: number;
  test_case_id: number;
  execution_order: number;
  is_enabled: boolean;
  case_parameters?: Record<string, unknown>;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface TestSuiteCaseCreate {
  test_suite_id: number;
  test_case_id: number;
  execution_order?: number;
  is_enabled?: boolean;
  case_parameters?: Record<string, unknown>;
  description?: string;
}

export interface TestSuiteCaseUpdate {
  execution_order?: number;
  is_enabled?: boolean;
  case_parameters?: Record<string, unknown>;
  description?: string;
}

export interface TestSuiteListParams {
  page?: number;
  page_size?: number;
  is_scheduled?: boolean;
  search?: string;
  tags?: string[];
  environment?: string;
}

export interface TestSuiteExecutionResult {
  success: boolean;
  test_suite_id: number;
  execution_id: number;
  test_case_results: Array<{
    test_case_id: number;
    test_case_name: string;
    success: boolean;
    duration: number;
    error?: string;
  }>;
  total_duration: number;
  timestamp: string;
  environment: string;
  passed_count: number;
  failed_count: number;
  skipped_count: number;
}

// Test Suite API Functions

/**
 * Get list of test suites with pagination and filtering
 */
export async function getTestSuites(
  params?: TestSuiteListParams,
): Promise<PaginatedResponse<TestSuite>> {
  const response = await apiClient.get<PaginatedResponse<TestSuite>>('/test-suites', { params });
  return response.data;
}

/**
 * Get a single test suite by ID
 */
export async function getTestSuite(id: number): Promise<TestSuite> {
  const response = await apiClient.get<TestSuite>(`/test-suites/${id}`);
  return response.data;
}

/**
 * Create a new test suite
 */
export async function createTestSuite(data: TestSuiteCreate): Promise<TestSuite> {
  const response = await apiClient.post<TestSuite>('/test-suites', data);
  return response.data;
}

/**
 * Update an existing test suite
 */
export async function updateTestSuite(id: number, data: TestSuiteUpdate): Promise<TestSuite> {
  const response = await apiClient.patch<TestSuite>(`/test-suites/${id}`, data);
  return response.data;
}

/**
 * Delete a test suite
 */
export async function deleteTestSuite(id: number): Promise<void> {
  await apiClient.delete(`/test-suites/${id}`);
}

/**
 * Duplicate a test suite
 */
export async function duplicateTestSuite(id: number, newName?: string): Promise<TestSuite> {
  const response = await apiClient.post<TestSuite>(`/test-suites/${id}/duplicate`, {
    name: newName,
  });
  return response.data;
}

/**
 * Execute a test suite
 */
export async function executeTestSuite(
  id: number,
  runtimeParams?: Record<string, unknown>,
): Promise<TestSuiteExecutionResult> {
  const response = await apiClient.post<TestSuiteExecutionResult>(`/test-suites/${id}/execute`, {
    runtime_parameters: runtimeParams,
  });
  return response.data;
}

/**
 * Get scheduled test suites
 */
export async function getScheduledTestSuites(): Promise<TestSuite[]> {
  const response = await apiClient.get<PaginatedResponse<TestSuite>>('/test-suites', {
    params: { is_scheduled: true, page_size: 100 },
  });
  return response.data.items;
}

/**
 * Search test suites by name or tags
 */
export async function searchTestSuites(query: string): Promise<TestSuite[]> {
  const response = await apiClient.get<PaginatedResponse<TestSuite>>('/test-suites', {
    params: { search: query, page_size: 50 },
  });
  return response.data.items;
}

// Test Suite Case Association Functions

/**
 * Get test cases associated with a test suite
 */
export async function getTestSuiteCases(testSuiteId: number): Promise<TestSuiteCase[]> {
  const response = await apiClient.get<PaginatedResponse<TestSuiteCase>>(
    `/test-suites/${testSuiteId}/cases`,
  );
  return response.data.items;
}

/**
 * Add a test case to a test suite
 */
export async function addCaseToTestSuite(data: TestSuiteCaseCreate): Promise<TestSuiteCase> {
  const response = await apiClient.post<TestSuiteCase>('/test-suite-cases', data);
  return response.data;
}

/**
 * Update a test suite-case association
 */
export async function updateTestSuiteCase(
  id: number,
  data: TestSuiteCaseUpdate,
): Promise<TestSuiteCase> {
  const response = await apiClient.patch<TestSuiteCase>(`/test-suite-cases/${id}`, data);
  return response.data;
}

/**
 * Remove a test case from a test suite
 */
export async function removeCaseFromTestSuite(id: number): Promise<void> {
  await apiClient.delete(`/test-suite-cases/${id}`);
}

/**
 * Reorder test cases in a test suite
 */
export async function reorderTestSuiteCases(
  testSuiteId: number,
  caseOrders: Array<{ test_case_id: number; execution_order: number }>,
): Promise<void> {
  await apiClient.post(`/test-suites/${testSuiteId}/cases/reorder`, { case_orders: caseOrders });
}

/**
 * Get test suite execution history
 */
export async function getTestSuiteExecutionHistory(
  testSuiteId: number,
  limit = 10,
): Promise<TestSuiteExecutionResult[]> {
  const response = await apiClient.get<{ items: TestSuiteExecutionResult[] }>(
    `/test-suites/${testSuiteId}/executions`,
    { params: { limit } },
  );
  return response.data.items;
}

/**
 * Schedule a test suite
 */
export async function scheduleTestSuite(
  id: number,
  scheduleConfig: Record<string, unknown>,
): Promise<TestSuite> {
  const response = await apiClient.post<TestSuite>(`/test-suites/${id}/schedule`, {
    schedule_config: scheduleConfig,
    is_scheduled: true,
  });
  return response.data;
}

/**
 * Unschedule a test suite
 */
export async function unscheduleTestSuite(id: number): Promise<TestSuite> {
  const response = await apiClient.post<TestSuite>(`/test-suites/${id}/unschedule`, {
    is_scheduled: false,
  });
  return response.data;
}
