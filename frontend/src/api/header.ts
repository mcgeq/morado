/**
 * Header API Client
 *
 * Layer 1: API Definition Components - Header Management
 * Provides functions for managing reusable HTTP header components.
 */

import apiClient, { type PaginatedResponse } from './index';

// Header Types
export type HeaderScope = 'global' | 'project' | 'private';

export interface Header {
  id: number;
  uuid: string;
  name: string;
  description?: string;
  headers: Record<string, string>;
  scope: HeaderScope;
  projectId?: number;
  isActive: boolean;
  version: string;
  tags?: string[];
  createdBy?: number;
  createdAt: string;
  updatedAt: string;
}

export interface HeaderCreate {
  name: string;
  description?: string;
  headers: Record<string, string>;
  scope?: HeaderScope;
  projectId?: number;
  isActive?: boolean;
  version?: string;
  tags?: string[];
  createdBy?: number;
}

export interface HeaderUpdate {
  name?: string;
  description?: string;
  headers?: Record<string, string>;
  scope?: HeaderScope;
  projectId?: number;
  isActive?: boolean;
  version?: string;
  tags?: string[];
}

export interface HeaderListParams {
  page?: number;
  pageSize?: number;
  scope?: HeaderScope;
  isActive?: boolean;
  search?: string;
  tags?: string[];
}

// Header API Functions

/**
 * Get list of headers with pagination and filtering
 */
export async function getHeaders(params?: HeaderListParams): Promise<PaginatedResponse<Header>> {
  const response = await apiClient.get<PaginatedResponse<Header>>('/headers', { params });
  return response.data;
}

/**
 * Get a single header by ID
 */
export async function getHeader(id: number): Promise<Header> {
  const response = await apiClient.get<Header>(`/headers/${id}`);
  return response.data;
}

/**
 * Create a new header
 */
export async function createHeader(data: HeaderCreate): Promise<Header> {
  const response = await apiClient.post<Header>('/headers', data);
  return response.data;
}

/**
 * Update an existing header
 */
export async function updateHeader(id: number, data: HeaderUpdate): Promise<Header> {
  const response = await apiClient.patch<Header>(`/headers/${id}`, data);
  return response.data;
}

/**
 * Delete a header
 */
export async function deleteHeader(id: number): Promise<void> {
  await apiClient.delete(`/headers/${id}`);
}

/**
 * Duplicate a header
 */
export async function duplicateHeader(id: number, newName?: string): Promise<Header> {
  const response = await apiClient.post<Header>(`/headers/${id}/duplicate`, { name: newName });
  return response.data;
}

/**
 * Get headers by scope
 */
export async function getHeadersByScope(scope: HeaderScope): Promise<Header[]> {
  const response = await apiClient.get<PaginatedResponse<Header>>('/headers', {
    params: { scope, pageSize: 100 },
  });
  return response.data.items;
}

/**
 * Search headers by name or tags
 */
export async function searchHeaders(query: string): Promise<Header[]> {
  const response = await apiClient.get<PaginatedResponse<Header>>('/headers', {
    params: { search: query, pageSize: 50 },
  });
  return response.data.items;
}
