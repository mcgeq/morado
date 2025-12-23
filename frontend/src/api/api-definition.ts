/**
 * API Definition API Client
 *
 * Layer 1: API Definition Components - API Definition Management
 * Provides functions for managing complete API interface definitions.
 */

import apiClient, { type PaginatedResponse } from './index';

// API Definition Types
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE' | 'HEAD' | 'OPTIONS';

export interface ApiDefinition {
  id: number;
  uuid: string;
  name: string;
  description?: string;
  method: HttpMethod;
  path: string;
  baseUrl?: string;
  headerId?: number;
  requestBodyId?: number;
  responseBodyId?: number;
  inlineRequestBody?: Record<string, unknown>;
  inlineResponseBody?: Record<string, unknown>;
  queryParameters?: Record<string, unknown>;
  pathParameters?: Record<string, unknown>;
  timeout: number;
  isActive: boolean;
  version: string;
  tags?: string[];
  createdBy?: number;
  createdAt: string;
  updatedAt: string;
}

export interface ApiDefinitionCreate {
  name: string;
  description?: string;
  method: HttpMethod;
  path: string;
  baseUrl?: string;
  headerId?: number;
  requestBodyId?: number;
  responseBodyId?: number;
  inlineRequestBody?: Record<string, unknown>;
  inlineResponseBody?: Record<string, unknown>;
  queryParameters?: Record<string, unknown>;
  pathParameters?: Record<string, unknown>;
  timeout?: number;
  isActive?: boolean;
  version?: string;
  tags?: string[];
  createdBy?: number;
}

export interface ApiDefinitionUpdate {
  name?: string;
  description?: string;
  method?: HttpMethod;
  path?: string;
  baseUrl?: string;
  headerId?: number;
  requestBodyId?: number;
  responseBodyId?: number;
  inlineRequestBody?: Record<string, unknown>;
  inlineResponseBody?: Record<string, unknown>;
  queryParameters?: Record<string, unknown>;
  pathParameters?: Record<string, unknown>;
  timeout?: number;
  isActive?: boolean;
  version?: string;
  tags?: string[];
}

export interface ApiDefinitionListParams {
  page?: number;
  pageSize?: number;
  method?: HttpMethod;
  isActive?: boolean;
  search?: string;
  tags?: string[];
}

// API Definition API Functions

/**
 * Get list of API definitions with pagination and filtering
 */
export async function getApiDefinitions(
  params?: ApiDefinitionListParams,
): Promise<PaginatedResponse<ApiDefinition>> {
  const response = await apiClient.get<PaginatedResponse<ApiDefinition>>('/api-definitions', {
    params,
  });
  return response.data;
}

/**
 * Get a single API definition by ID
 */
export async function getApiDefinition(id: number): Promise<ApiDefinition> {
  const response = await apiClient.get<ApiDefinition>(`/api-definitions/${id}`);
  return response.data;
}

/**
 * Create a new API definition
 */
export async function createApiDefinition(data: ApiDefinitionCreate): Promise<ApiDefinition> {
  const response = await apiClient.post<ApiDefinition>('/api-definitions', data);
  return response.data;
}

/**
 * Update an existing API definition
 */
export async function updateApiDefinition(
  id: number,
  data: ApiDefinitionUpdate,
): Promise<ApiDefinition> {
  const response = await apiClient.patch<ApiDefinition>(`/api-definitions/${id}`, data);
  return response.data;
}

/**
 * Delete an API definition
 */
export async function deleteApiDefinition(id: number): Promise<void> {
  await apiClient.delete(`/api-definitions/${id}`);
}

/**
 * Duplicate an API definition
 */
export async function duplicateApiDefinition(id: number, newName?: string): Promise<ApiDefinition> {
  const response = await apiClient.post<ApiDefinition>(`/api-definitions/${id}/duplicate`, {
    name: newName,
  });
  return response.data;
}

/**
 * Get API definitions by HTTP method
 */
export async function getApiDefinitionsByMethod(method: HttpMethod): Promise<ApiDefinition[]> {
  const response = await apiClient.get<PaginatedResponse<ApiDefinition>>('/api-definitions', {
    params: { method, pageSize: 100 },
  });
  return response.data.items;
}

/**
 * Search API definitions by name or tags
 */
export async function searchApiDefinitions(query: string): Promise<ApiDefinition[]> {
  const response = await apiClient.get<PaginatedResponse<ApiDefinition>>('/api-definitions', {
    params: { search: query, pageSize: 50 },
  });
  return response.data.items;
}

/**
 * Test an API definition (dry run)
 */
export async function testApiDefinition(
  id: number,
  testData?: Record<string, unknown>,
): Promise<{
  success: boolean;
  statusCode?: number;
  responseData?: unknown;
  error?: string;
  duration?: number;
}> {
  const response = await apiClient.post(`/api-definitions/${id}/test`, testData);
  return response.data;
}

/**
 * Get API definitions that reference a specific header
 */
export async function getApiDefinitionsByHeader(headerId: number): Promise<ApiDefinition[]> {
  const response = await apiClient.get<PaginatedResponse<ApiDefinition>>('/api-definitions', {
    params: { headerId, pageSize: 100 },
  });
  return response.data.items;
}

/**
 * Get API definitions that reference a specific body
 */
export async function getApiDefinitionsByBody(
  bodyId: number,
  bodyType: 'request' | 'response',
): Promise<ApiDefinition[]> {
  const paramKey = bodyType === 'request' ? 'requestBodyId' : 'responseBodyId';
  const response = await apiClient.get<PaginatedResponse<ApiDefinition>>('/api-definitions', {
    params: { [paramKey]: bodyId, pageSize: 100 },
  });
  return response.data.items;
}
