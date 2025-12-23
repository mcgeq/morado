/**
 * Body API Client
 *
 * Layer 1: API Definition Components - Body Management
 * Provides functions for managing reusable request/response body templates.
 */

import apiClient, { type PaginatedResponse } from './index';

// Body Types
export type BodyType = 'request' | 'response' | 'both';
export type BodyScope = 'global' | 'project' | 'private';

export interface Body {
  id: number;
  uuid: string;
  name: string;
  description?: string;
  bodyType: BodyType;
  contentType: string;
  bodySchema?: Record<string, unknown>;
  exampleData?: Record<string, unknown>;
  scope: BodyScope;
  projectId?: number;
  isActive: boolean;
  version: string;
  tags?: string[];
  createdBy?: number;
  createdAt: string;
  updatedAt: string;
}

export interface BodyCreate {
  name: string;
  description?: string;
  bodyType?: BodyType;
  contentType?: string;
  bodySchema?: Record<string, unknown>;
  exampleData?: Record<string, unknown>;
  scope?: BodyScope;
  projectId?: number;
  isActive?: boolean;
  version?: string;
  tags?: string[];
  createdBy?: number;
}

export interface BodyUpdate {
  name?: string;
  description?: string;
  bodyType?: BodyType;
  contentType?: string;
  bodySchema?: Record<string, unknown>;
  exampleData?: Record<string, unknown>;
  scope?: BodyScope;
  projectId?: number;
  isActive?: boolean;
  version?: string;
  tags?: string[];
}

export interface BodyListParams {
  page?: number;
  pageSize?: number;
  bodyType?: BodyType;
  scope?: BodyScope;
  isActive?: boolean;
  search?: string;
  tags?: string[];
}

// Body API Functions

/**
 * Get list of bodies with pagination and filtering
 */
export async function getBodies(params?: BodyListParams): Promise<PaginatedResponse<Body>> {
  const response = await apiClient.get<PaginatedResponse<Body>>('/bodies', { params });
  return response.data;
}

/**
 * Get a single body by ID
 */
export async function getBody(id: number): Promise<Body> {
  const response = await apiClient.get<Body>(`/bodies/${id}`);
  return response.data;
}

/**
 * Create a new body
 */
export async function createBody(data: BodyCreate): Promise<Body> {
  const response = await apiClient.post<Body>('/bodies', data);
  return response.data;
}

/**
 * Update an existing body
 */
export async function updateBody(id: number, data: BodyUpdate): Promise<Body> {
  const response = await apiClient.patch<Body>(`/bodies/${id}`, data);
  return response.data;
}

/**
 * Delete a body
 */
export async function deleteBody(id: number): Promise<void> {
  await apiClient.delete(`/bodies/${id}`);
}

/**
 * Duplicate a body
 */
export async function duplicateBody(id: number, newName?: string): Promise<Body> {
  const response = await apiClient.post<Body>(`/bodies/${id}/duplicate`, { name: newName });
  return response.data;
}

/**
 * Get bodies by type
 */
export async function getBodiesByType(bodyType: BodyType): Promise<Body[]> {
  const response = await apiClient.get<PaginatedResponse<Body>>('/bodies', {
    params: { bodyType, pageSize: 100 },
  });
  return response.data.items;
}

/**
 * Get bodies by scope
 */
export async function getBodiesByScope(scope: BodyScope): Promise<Body[]> {
  const response = await apiClient.get<PaginatedResponse<Body>>('/bodies', {
    params: { scope, pageSize: 100 },
  });
  return response.data.items;
}

/**
 * Search bodies by name or tags
 */
export async function searchBodies(query: string): Promise<Body[]> {
  const response = await apiClient.get<PaginatedResponse<Body>>('/bodies', {
    params: { search: query, pageSize: 50 },
  });
  return response.data.items;
}

/**
 * Validate body schema
 */
export async function validateBodySchema(
  schema: Record<string, unknown>,
): Promise<{ valid: boolean; errors?: string[] }> {
  const response = await apiClient.post<{ valid: boolean; errors?: string[] }>(
    '/bodies/validate-schema',
    { schema },
  );
  return response.data;
}
