/**
 * Script API Client
 *
 * Layer 2: Test Scripts - Script Management and Execution
 * Provides functions for managing and executing test scripts.
 */

import apiClient, { type PaginatedResponse } from './index';

// Script Types
export type ScriptType = 'setup' | 'main' | 'teardown' | 'utility';
export type AssertionType =
  | 'equals'
  | 'notEquals'
  | 'contains'
  | 'notContains'
  | 'greaterThan'
  | 'lessThan'
  | 'regexMatch'
  | 'jsonPath'
  | 'statusCode'
  | 'responseTime'
  | 'custom';
export type ParameterType = 'string' | 'integer' | 'float' | 'boolean' | 'json' | 'array' | 'file';

export interface Assertion {
  type: AssertionType;
  expected?: unknown;
  path?: string;
  assertion?: string;
  message?: string;
}

export interface TestScript {
  id: number;
  uuid: string;
  name: string;
  description?: string;
  apiDefinitionId: number;
  scriptType: ScriptType;
  executionOrder: number;
  variables?: Record<string, unknown>;
  assertions?: Assertion[];
  validators?: Record<string, unknown>;
  preScript?: string;
  postScript?: string;
  extractVariables?: Record<string, string>;
  outputVariables?: string[];
  debugMode: boolean;
  debugBreakpoints?: unknown[];
  retryCount: number;
  retryInterval: number;
  timeoutOverride?: number;
  isActive: boolean;
  version: string;
  tags?: string[];
  createdBy?: number;
  createdAt: string;
  updatedAt: string;
}

export interface TestScriptCreate {
  name: string;
  description?: string;
  apiDefinitionId: number;
  scriptType?: ScriptType;
  executionOrder?: number;
  variables?: Record<string, unknown>;
  assertions?: Assertion[];
  validators?: Record<string, unknown>;
  preScript?: string;
  postScript?: string;
  extractVariables?: Record<string, string>;
  outputVariables?: string[];
  debugMode?: boolean;
  debugBreakpoints?: unknown[];
  retryCount?: number;
  retryInterval?: number;
  timeoutOverride?: number;
  isActive?: boolean;
  version?: string;
  tags?: string[];
  createdBy?: number;
}

export interface TestScriptUpdate {
  name?: string;
  description?: string;
  apiDefinitionId?: number;
  scriptType?: ScriptType;
  executionOrder?: number;
  variables?: Record<string, unknown>;
  assertions?: Assertion[];
  validators?: Record<string, unknown>;
  preScript?: string;
  postScript?: string;
  extractVariables?: Record<string, string>;
  outputVariables?: string[];
  debugMode?: boolean;
  debugBreakpoints?: unknown[];
  retryCount?: number;
  retryInterval?: number;
  timeoutOverride?: number;
  isActive?: boolean;
  version?: string;
  tags?: string[];
}

export interface ScriptParameter {
  id: number;
  uuid: string;
  scriptId: number;
  name: string;
  description?: string;
  parameterType: ParameterType;
  defaultValue?: string;
  isRequired: boolean;
  validationRules?: Record<string, unknown>;
  order: number;
  group?: string;
  isSensitive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface ScriptParameterCreate {
  scriptId: number;
  name: string;
  description?: string;
  parameterType?: ParameterType;
  defaultValue?: string;
  isRequired?: boolean;
  validationRules?: Record<string, unknown>;
  order?: number;
  group?: string;
  isSensitive?: boolean;
}

export interface ScriptParameterUpdate {
  name?: string;
  description?: string;
  parameterType?: ParameterType;
  defaultValue?: string;
  isRequired?: boolean;
  validationRules?: Record<string, unknown>;
  order?: number;
  group?: string;
  isSensitive?: boolean;
}

export interface ScriptListParams {
  page?: number;
  pageSize?: number;
  scriptType?: ScriptType;
  isActive?: boolean;
  search?: string;
  tags?: string[];
  apiDefinitionId?: number;
}

export interface ScriptExecutionResult {
  success: boolean;
  statusCode?: number;
  responseData?: unknown;
  extractedVariables?: Record<string, unknown>;
  assertionResults?: Array<{
    assertion: Assertion;
    passed: boolean;
    message?: string;
  }>;
  error?: string;
  duration: number;
  timestamp: string;
}

// Script API Functions

/**
 * Get list of scripts with pagination and filtering
 */
export async function getScripts(
  params?: ScriptListParams,
): Promise<PaginatedResponse<TestScript>> {
  const response = await apiClient.get<PaginatedResponse<TestScript>>('/scripts', { params });
  return response.data;
}

/**
 * Get a single script by ID
 */
export async function getScript(id: number): Promise<TestScript> {
  const response = await apiClient.get<TestScript>(`/scripts/${id}`);
  return response.data;
}

/**
 * Create a new script
 */
export async function createScript(data: TestScriptCreate): Promise<TestScript> {
  const response = await apiClient.post<TestScript>('/scripts', data);
  return response.data;
}

/**
 * Update an existing script
 */
export async function updateScript(id: number, data: TestScriptUpdate): Promise<TestScript> {
  const response = await apiClient.patch<TestScript>(`/scripts/${id}`, data);
  return response.data;
}

/**
 * Delete a script
 */
export async function deleteScript(id: number): Promise<void> {
  await apiClient.delete(`/scripts/${id}`);
}

/**
 * Duplicate a script
 */
export async function duplicateScript(id: number, newName?: string): Promise<TestScript> {
  const response = await apiClient.post<TestScript>(`/scripts/${id}/duplicate`, { name: newName });
  return response.data;
}

/**
 * Execute a script (for debugging)
 */
export async function executeScript(
  id: number,
  runtimeParams?: Record<string, unknown>,
): Promise<ScriptExecutionResult> {
  const response = await apiClient.post<ScriptExecutionResult>(`/scripts/${id}/execute`, {
    runtimeParameters: runtimeParams,
  });
  return response.data;
}

/**
 * Debug a script with breakpoints
 */
export async function debugScript(
  id: number,
  breakpoints?: unknown[],
  runtimeParams?: Record<string, unknown>,
): Promise<ScriptExecutionResult> {
  const response = await apiClient.post<ScriptExecutionResult>(`/scripts/${id}/debug`, {
    breakpoints,
    runtimeParameters: runtimeParams,
  });
  return response.data;
}

/**
 * Get scripts by type
 */
export async function getScriptsByType(scriptType: ScriptType): Promise<TestScript[]> {
  const response = await apiClient.get<PaginatedResponse<TestScript>>('/scripts', {
    params: { scriptType, pageSize: 100 },
  });
  return response.data.items;
}

/**
 * Get scripts by API definition
 */
export async function getScriptsByApiDefinition(apiDefinitionId: number): Promise<TestScript[]> {
  const response = await apiClient.get<PaginatedResponse<TestScript>>('/scripts', {
    params: { apiDefinitionId, pageSize: 100 },
  });
  return response.data.items;
}

/**
 * Search scripts by name or tags
 */
export async function searchScripts(query: string): Promise<TestScript[]> {
  const response = await apiClient.get<PaginatedResponse<TestScript>>('/scripts', {
    params: { search: query, pageSize: 50 },
  });
  return response.data.items;
}

// Script Parameter Functions

/**
 * Get parameters for a script
 */
export async function getScriptParameters(scriptId: number): Promise<ScriptParameter[]> {
  const response = await apiClient.get<PaginatedResponse<ScriptParameter>>(
    `/scripts/${scriptId}/parameters`,
  );
  return response.data.items;
}

/**
 * Create a script parameter
 */
export async function createScriptParameter(data: ScriptParameterCreate): Promise<ScriptParameter> {
  const response = await apiClient.post<ScriptParameter>('/script-parameters', data);
  return response.data;
}

/**
 * Update a script parameter
 */
export async function updateScriptParameter(
  id: number,
  data: ScriptParameterUpdate,
): Promise<ScriptParameter> {
  const response = await apiClient.patch<ScriptParameter>(`/script-parameters/${id}`, data);
  return response.data;
}

/**
 * Delete a script parameter
 */
export async function deleteScriptParameter(id: number): Promise<void> {
  await apiClient.delete(`/script-parameters/${id}`);
}
