/**
 * Test Case API Client
 *
 * Layer 4: Test Cases - Test Case Management and Execution
 * Provides functions for managing test cases that reference scripts and components.
 */

import apiClient, { type PaginatedResponse } from './index';

// Test Case Types
export type TestCasePriority = 'low' | 'medium' | 'high' | 'critical';
export type TestCaseStatus = 'draft' | 'active' | 'deprecated' | 'archived';

export interface TestCase {
  id: number;
  uuid: string;
  name: string;
  description?: string;
  priority: TestCasePriority;
  status: TestCaseStatus;
  category?: string;
  tags?: string[];
  preconditions?: string;
  postconditions?: string;
  executionOrder: string;
  timeout: number;
  timeoutOverride?: number;
  retryCount: number;
  continueOnFailure: boolean;
  testData?: Record<string, unknown>;
  environment: string;
  version: string;
  isAutomated: boolean;
  scriptCount?: number;
  componentCount?: number;
  lastExecutionAt?: string;
  lastExecutionStatus?: 'passed' | 'failed' | 'skipped';
  createdBy?: number;
  createdAt: string;
  updatedAt: string;
}

export interface TestCaseCreate {
  name: string;
  description?: string;
  priority?: TestCasePriority;
  status?: TestCaseStatus;
  category?: string;
  tags?: string[];
  preconditions?: string;
  postconditions?: string;
  executionOrder?: string;
  timeout?: number;
  retryCount?: number;
  continueOnFailure?: boolean;
  testData?: Record<string, unknown>;
  environment?: string;
  version?: string;
  isAutomated?: boolean;
  createdBy?: number;
}

export interface TestCaseUpdate {
  name?: string;
  description?: string;
  priority?: TestCasePriority;
  status?: TestCaseStatus;
  category?: string;
  tags?: string[];
  preconditions?: string;
  postconditions?: string;
  executionOrder?: string;
  timeout?: number;
  retryCount?: number;
  continueOnFailure?: boolean;
  testData?: Record<string, unknown>;
  environment?: string;
  version?: string;
  isAutomated?: boolean;
}

export interface TestCaseScript {
  id: number;
  testCaseId: number;
  scriptId: number;
  executionOrder: number;
  isEnabled: boolean;
  scriptParameters?: Record<string, unknown>;
  description?: string;
  createdAt: string;
  updatedAt: string;
}

export interface TestCaseScriptCreate {
  testCaseId: number;
  scriptId: number;
  executionOrder?: number;
  isEnabled?: boolean;
  scriptParameters?: Record<string, unknown>;
  description?: string;
}

export interface TestCaseScriptUpdate {
  executionOrder?: number;
  isEnabled?: boolean;
  scriptParameters?: Record<string, unknown>;
  description?: string;
}

export interface TestCaseComponent {
  id: number;
  testCaseId: number;
  componentId: number;
  executionOrder: number;
  isEnabled: boolean;
  componentParameters?: Record<string, unknown>;
  description?: string;
  createdAt: string;
  updatedAt: string;
}

export interface TestCaseComponentCreate {
  testCaseId: number;
  componentId: number;
  executionOrder?: number;
  isEnabled?: boolean;
  componentParameters?: Record<string, unknown>;
  description?: string;
}

export interface TestCaseComponentUpdate {
  executionOrder?: number;
  isEnabled?: boolean;
  componentParameters?: Record<string, unknown>;
  description?: string;
}

export interface TestCaseListParams {
  page?: number;
  pageSize?: number;
  priority?: TestCasePriority;
  status?: TestCaseStatus;
  category?: string;
  isAutomated?: boolean;
  search?: string;
  tags?: string[];
  environment?: string;
}

export interface TestCaseExecutionResult {
  success: boolean;
  testCaseId: number;
  executionId: number;
  scriptResults: Array<{
    scriptId: number;
    scriptName: string;
    success: boolean;
    duration: number;
    error?: string;
  }>;
  componentResults: Array<{
    componentId: number;
    componentName: string;
    success: boolean;
    duration: number;
    error?: string;
  }>;
  totalDuration: number;
  timestamp: string;
  environment: string;
}

// Test Case API Functions

/**
 * Get list of test cases with pagination and filtering
 */
export async function getTestCases(
  params?: TestCaseListParams,
): Promise<PaginatedResponse<TestCase>> {
  const response = await apiClient.get<PaginatedResponse<TestCase>>('/test-cases', { params });
  return response.data;
}

/**
 * Get a single test case by ID
 */
export async function getTestCase(id: number): Promise<TestCase> {
  const response = await apiClient.get<TestCase>(`/test-cases/${id}`);
  return response.data;
}

/**
 * Create a new test case
 */
export async function createTestCase(data: TestCaseCreate): Promise<TestCase> {
  const response = await apiClient.post<TestCase>('/test-cases', data);
  return response.data;
}

/**
 * Update an existing test case
 */
export async function updateTestCase(id: number, data: TestCaseUpdate): Promise<TestCase> {
  const response = await apiClient.patch<TestCase>(`/test-cases/${id}`, data);
  return response.data;
}

/**
 * Delete a test case
 */
export async function deleteTestCase(id: number): Promise<void> {
  await apiClient.delete(`/test-cases/${id}`);
}

/**
 * Duplicate a test case
 */
export async function duplicateTestCase(id: number, newName?: string): Promise<TestCase> {
  const response = await apiClient.post<TestCase>(`/test-cases/${id}/duplicate`, { name: newName });
  return response.data;
}

/**
 * Execute a test case
 */
export async function executeTestCase(
  id: number,
  runtimeParams?: Record<string, unknown>,
): Promise<TestCaseExecutionResult> {
  const response = await apiClient.post<TestCaseExecutionResult>(`/test-cases/${id}/execute`, {
    runtimeParameters: runtimeParams,
  });
  return response.data;
}

/**
 * Get test cases by priority
 */
export async function getTestCasesByPriority(priority: TestCasePriority): Promise<TestCase[]> {
  const response = await apiClient.get<PaginatedResponse<TestCase>>('/test-cases', {
    params: { priority, pageSize: 100 },
  });
  return response.data.items;
}

/**
 * Get test cases by status
 */
export async function getTestCasesByStatus(status: TestCaseStatus): Promise<TestCase[]> {
  const response = await apiClient.get<PaginatedResponse<TestCase>>('/test-cases', {
    params: { status, pageSize: 100 },
  });
  return response.data.items;
}

/**
 * Get test cases by category
 */
export async function getTestCasesByCategory(category: string): Promise<TestCase[]> {
  const response = await apiClient.get<PaginatedResponse<TestCase>>('/test-cases', {
    params: { category, pageSize: 100 },
  });
  return response.data.items;
}

/**
 * Search test cases by name or tags
 */
export async function searchTestCases(query: string): Promise<TestCase[]> {
  const response = await apiClient.get<PaginatedResponse<TestCase>>('/test-cases', {
    params: { search: query, pageSize: 50 },
  });
  return response.data.items;
}

// Test Case Script Association Functions

/**
 * Get scripts associated with a test case
 */
export async function getTestCaseScripts(testCaseId: number): Promise<TestCaseScript[]> {
  const response = await apiClient.get<PaginatedResponse<TestCaseScript>>(
    `/test-cases/${testCaseId}/scripts`,
  );
  return response.data.items;
}

/**
 * Add a script to a test case
 */
export async function addScriptToTestCase(data: TestCaseScriptCreate): Promise<TestCaseScript> {
  const response = await apiClient.post<TestCaseScript>('/test-case-scripts', data);
  return response.data;
}

/**
 * Update a test case-script association
 */
export async function updateTestCaseScript(
  id: number,
  data: TestCaseScriptUpdate,
): Promise<TestCaseScript> {
  const response = await apiClient.patch<TestCaseScript>(`/test-case-scripts/${id}`, data);
  return response.data;
}

/**
 * Remove a script from a test case
 */
export async function removeScriptFromTestCase(id: number): Promise<void> {
  await apiClient.delete(`/test-case-scripts/${id}`);
}

// Test Case Component Association Functions

/**
 * Get components associated with a test case
 */
export async function getTestCaseComponents(testCaseId: number): Promise<TestCaseComponent[]> {
  const response = await apiClient.get<PaginatedResponse<TestCaseComponent>>(
    `/test-cases/${testCaseId}/components`,
  );
  return response.data.items;
}

/**
 * Add a component to a test case
 */
export async function addComponentToTestCase(
  data: TestCaseComponentCreate,
): Promise<TestCaseComponent> {
  const response = await apiClient.post<TestCaseComponent>('/test-case-components', data);
  return response.data;
}

/**
 * Update a test case-component association
 */
export async function updateTestCaseComponent(
  id: number,
  data: TestCaseComponentUpdate,
): Promise<TestCaseComponent> {
  const response = await apiClient.patch<TestCaseComponent>(`/test-case-components/${id}`, data);
  return response.data;
}

/**
 * Remove a component from a test case
 */
export async function removeComponentFromTestCase(id: number): Promise<void> {
  await apiClient.delete(`/test-case-components/${id}`);
}

/**
 * Get test case execution history
 */
export async function getTestCaseExecutionHistory(
  testCaseId: number,
  limit = 10,
): Promise<TestCaseExecutionResult[]> {
  const response = await apiClient.get<{ items: TestCaseExecutionResult[] }>(
    `/test-cases/${testCaseId}/executions`,
    { params: { limit } },
  );
  return response.data.items;
}
