/**
 * Component API Client
 *
 * Layer 3: Test Components - Component Management and Execution
 * Provides functions for managing composite components that combine multiple scripts.
 */

import apiClient, { type PaginatedResponse } from './index';

// Component Types
export type ComponentType = 'simple' | 'composite' | 'template';
export type ExecutionMode = 'sequential' | 'parallel' | 'conditional';

export interface TestComponent {
  id: number;
  uuid: string;
  name: string;
  description?: string;
  componentType: ComponentType;
  executionMode: ExecutionMode;
  parentComponentId?: number;
  sharedVariables?: Record<string, unknown>;
  timeout: number;
  timeoutOverride?: number;
  retryCount: number;
  continueOnFailure: boolean;
  executionCondition?: string;
  isActive: boolean;
  version: string;
  tags?: string[];
  scriptCount?: number;
  createdBy?: number;
  createdAt: string;
  updatedAt: string;
}

export interface TestComponentCreate {
  name: string;
  description?: string;
  componentType?: ComponentType;
  executionMode?: ExecutionMode;
  parentComponentId?: number;
  sharedVariables?: Record<string, unknown>;
  timeout?: number;
  retryCount?: number;
  continueOnFailure?: boolean;
  executionCondition?: string;
  isActive?: boolean;
  version?: string;
  tags?: string[];
  createdBy?: number;
}

export interface TestComponentUpdate {
  name?: string;
  description?: string;
  componentType?: ComponentType;
  executionMode?: ExecutionMode;
  parentComponentId?: number;
  sharedVariables?: Record<string, unknown>;
  timeout?: number;
  retryCount?: number;
  continueOnFailure?: boolean;
  executionCondition?: string;
  isActive?: boolean;
  version?: string;
  tags?: string[];
}

export interface ComponentScript {
  id: number;
  componentId: number;
  scriptId: number;
  executionOrder: number;
  isEnabled: boolean;
  scriptParameters?: Record<string, unknown>;
  parameterOverrides?: Record<string, unknown>;
  executionCondition?: string;
  skipOnCondition: boolean;
  description?: string;
  script?: {
    id: number;
    name: string;
    scriptType: 'setup' | 'main' | 'teardown' | 'utility';
  };
  createdAt: string;
  updatedAt: string;
}

export interface ComponentScriptCreate {
  componentId: number;
  scriptId: number;
  executionOrder?: number;
  isEnabled?: boolean;
  scriptParameters?: Record<string, unknown>;
  executionCondition?: string;
  skipOnCondition?: boolean;
  description?: string;
}

export interface ComponentScriptUpdate {
  executionOrder?: number;
  isEnabled?: boolean;
  scriptParameters?: Record<string, unknown>;
  executionCondition?: string;
  skipOnCondition?: boolean;
  description?: string;
}

export interface ComponentListParams {
  page?: number;
  pageSize?: number;
  componentType?: ComponentType;
  executionMode?: ExecutionMode;
  isActive?: boolean;
  search?: string;
  tags?: string[];
  parentComponentId?: number;
}

export interface ComponentExecutionResult {
  success: boolean;
  componentId: number;
  scriptResults: Array<{
    scriptId: number;
    scriptName: string;
    success: boolean;
    duration: number;
    error?: string;
  }>;
  totalDuration: number;
  timestamp: string;
  sharedVariables?: Record<string, unknown>;
}

// Component API Functions

/**
 * Get list of components with pagination and filtering
 */
export async function getComponents(
  params?: ComponentListParams,
): Promise<PaginatedResponse<TestComponent>> {
  const response = await apiClient.get<PaginatedResponse<TestComponent>>('/components', { params });
  return response.data;
}

/**
 * Get a single component by ID
 */
export async function getComponent(id: number): Promise<TestComponent> {
  const response = await apiClient.get<TestComponent>(`/components/${id}`);
  return response.data;
}

/**
 * Create a new component
 */
export async function createComponent(data: TestComponentCreate): Promise<TestComponent> {
  const response = await apiClient.post<TestComponent>('/components', data);
  return response.data;
}

/**
 * Update an existing component
 */
export async function updateComponent(
  id: number,
  data: TestComponentUpdate,
): Promise<TestComponent> {
  const response = await apiClient.patch<TestComponent>(`/components/${id}`, data);
  return response.data;
}

/**
 * Delete a component
 */
export async function deleteComponent(id: number): Promise<void> {
  await apiClient.delete(`/components/${id}`);
}

/**
 * Duplicate a component
 */
export async function duplicateComponent(id: number, newName?: string): Promise<TestComponent> {
  const response = await apiClient.post<TestComponent>(`/components/${id}/duplicate`, {
    name: newName,
  });
  return response.data;
}

/**
 * Execute a component
 */
export async function executeComponent(
  id: number,
  runtimeParams?: Record<string, unknown>,
): Promise<ComponentExecutionResult> {
  const response = await apiClient.post<ComponentExecutionResult>(`/components/${id}/execute`, {
    runtimeParameters: runtimeParams,
  });
  return response.data;
}

/**
 * Get component hierarchy (nested components)
 */
export async function getComponentHierarchy(id: number): Promise<{
  component: TestComponent;
  children: TestComponent[];
  scripts: ComponentScript[];
}> {
  const response = await apiClient.get(`/components/${id}/hierarchy`);
  return response.data;
}

/**
 * Get child components
 */
export async function getChildComponents(parentId: number): Promise<TestComponent[]> {
  const response = await apiClient.get<PaginatedResponse<TestComponent>>('/components', {
    params: { parentComponentId: parentId, pageSize: 100 },
  });
  return response.data.items;
}

/**
 * Get components by type
 */
export async function getComponentsByType(componentType: ComponentType): Promise<TestComponent[]> {
  const response = await apiClient.get<PaginatedResponse<TestComponent>>('/components', {
    params: { componentType, pageSize: 100 },
  });
  return response.data.items;
}

/**
 * Search components by name or tags
 */
export async function searchComponents(query: string): Promise<TestComponent[]> {
  const response = await apiClient.get<PaginatedResponse<TestComponent>>('/components', {
    params: { search: query, pageSize: 50 },
  });
  return response.data.items;
}

// Component-Script Association Functions

/**
 * Get scripts associated with a component
 */
export async function getComponentScripts(componentId: number): Promise<ComponentScript[]> {
  const response = await apiClient.get<PaginatedResponse<ComponentScript>>(
    `/components/${componentId}/scripts`,
  );
  return response.data.items;
}

/**
 * Add a script to a component
 */
export async function addScriptToComponent(data: ComponentScriptCreate): Promise<ComponentScript> {
  const response = await apiClient.post<ComponentScript>('/component-scripts', data);
  return response.data;
}

/**
 * Update a component-script association
 */
export async function updateComponentScript(
  id: number,
  data: ComponentScriptUpdate,
): Promise<ComponentScript> {
  const response = await apiClient.patch<ComponentScript>(`/component-scripts/${id}`, data);
  return response.data;
}

/**
 * Remove a script from a component
 */
export async function removeScriptFromComponent(id: number): Promise<void> {
  await apiClient.delete(`/component-scripts/${id}`);
}

/**
 * Reorder scripts in a component
 */
export async function reorderComponentScripts(
  componentId: number,
  scriptOrders: Array<{ scriptId: number; executionOrder: number }>,
): Promise<void> {
  await apiClient.post(`/components/${componentId}/scripts/reorder`, {
    scriptOrders,
  });
}
