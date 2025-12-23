/**
 * API Definition Store
 *
 * Layer 1: API Definition Components - API Definition Management
 * Manages state for complete API interface definitions.
 */

import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import {
  type ApiDefinition,
  type ApiDefinitionCreate,
  type ApiDefinitionListParams,
  type ApiDefinitionUpdate,
  createApiDefinition,
  deleteApiDefinition,
  duplicateApiDefinition,
  getApiDefinition,
  getApiDefinitions,
  getApiDefinitionsByBody,
  getApiDefinitionsByHeader,
  getApiDefinitionsByMethod,
  type HttpMethod,
  searchApiDefinitions,
  testApiDefinition,
  updateApiDefinition,
} from '@/api/api-definition';

export const useApiDefinitionStore = defineStore('apiDefinition', () => {
  // State
  const apiDefinitions = ref<ApiDefinition[]>([]);
  const currentApiDefinition = ref<ApiDefinition | null>(null);
  const isLoading = ref(false);
  const isSaving = ref(false);
  const isTesting = ref(false);
  const error = ref<string | null>(null);
  const testResult = ref<{
    success: boolean;
    status_code?: number;
    response_data?: unknown;
    error?: string;
    duration?: number;
  } | null>(null);
  const totalCount = ref(0);
  const currentPage = ref(1);
  const pageSize = ref(20);

  // Computed
  const getApiDefinitionsList = computed(() =>
    apiDefinitions.value.filter(api => api.method === 'GET' && api.isActive),
  );

  const postApiDefinitions = computed(() =>
    apiDefinitions.value.filter(api => api.method === 'POST' && api.isActive),
  );

  const putApiDefinitions = computed(() =>
    apiDefinitions.value.filter(api => api.method === 'PUT' && api.isActive),
  );

  const patchApiDefinitions = computed(() =>
    apiDefinitions.value.filter(api => api.method === 'PATCH' && api.isActive),
  );

  const deleteApiDefinitions = computed(() =>
    apiDefinitions.value.filter(api => api.method === 'DELETE' && api.isActive),
  );

  const activeApiDefinitions = computed(() => apiDefinitions.value.filter(api => api.isActive));

  const hasApiDefinitions = computed(() => apiDefinitions.value.length > 0);

  const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value));

  // Group by method for easy access
  const apiDefinitionsByMethod = computed(() => {
    const grouped: Record<HttpMethod, ApiDefinition[]> = {
      GET: [],
      POST: [],
      PUT: [],
      PATCH: [],
      DELETE: [],
      HEAD: [],
      OPTIONS: [],
    };

    apiDefinitions.value.forEach(api => {
      if (api.isActive) {
        grouped[api.method].push(api);
      }
    });

    return grouped;
  });

  // Actions
  async function fetchApiDefinitions(params?: ApiDefinitionListParams): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await getApiDefinitions({
        page: currentPage.value,
        pageSize: pageSize.value,
        ...params,
      });

      apiDefinitions.value = response.items;
      totalCount.value = response.total;
      currentPage.value = response.page;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch API definitions';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchApiDefinitionById(id: number): Promise<ApiDefinition> {
    isLoading.value = true;
    error.value = null;

    try {
      const apiDef = await getApiDefinition(id);
      currentApiDefinition.value = apiDef;
      return apiDef;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch API definition';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function createNewApiDefinition(data: ApiDefinitionCreate): Promise<ApiDefinition> {
    isSaving.value = true;
    error.value = null;

    try {
      const apiDef = await createApiDefinition(data);
      apiDefinitions.value.unshift(apiDef);
      totalCount.value += 1;
      return apiDef;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create API definition';
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  async function updateExistingApiDefinition(
    id: number,
    data: ApiDefinitionUpdate,
  ): Promise<ApiDefinition> {
    isSaving.value = true;
    error.value = null;

    try {
      const updatedApiDef = await updateApiDefinition(id, data);

      // Update in list
      const index = apiDefinitions.value.findIndex(api => api.id === id);
      if (index !== -1) {
        apiDefinitions.value[index] = updatedApiDef;
      }

      // Update current if it's the same
      if (currentApiDefinition.value?.id === id) {
        currentApiDefinition.value = updatedApiDef;
      }

      return updatedApiDef;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update API definition';
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  async function deleteApiDefinitionById(id: number): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      await deleteApiDefinition(id);

      // Remove from list
      apiDefinitions.value = apiDefinitions.value.filter(api => api.id !== id);
      totalCount.value -= 1;

      // Clear current if it's the same
      if (currentApiDefinition.value?.id === id) {
        currentApiDefinition.value = null;
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete API definition';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function duplicateExistingApiDefinition(
    id: number,
    newName?: string,
  ): Promise<ApiDefinition> {
    isSaving.value = true;
    error.value = null;

    try {
      const duplicated = await duplicateApiDefinition(id, newName);
      apiDefinitions.value.unshift(duplicated);
      totalCount.value += 1;
      return duplicated;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to duplicate API definition';
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  async function fetchApiDefinitionsByMethod(method: HttpMethod): Promise<ApiDefinition[]> {
    isLoading.value = true;
    error.value = null;

    try {
      const methodApiDefs = await getApiDefinitionsByMethod(method);
      return methodApiDefs;
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to fetch API definitions by method';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function searchApiDefinitionsByQuery(query: string): Promise<ApiDefinition[]> {
    isLoading.value = true;
    error.value = null;

    try {
      const results = await searchApiDefinitions(query);
      return results;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to search API definitions';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function testApiDefinitionById(
    id: number,
    testData?: Record<string, unknown>,
  ): Promise<void> {
    isTesting.value = true;
    error.value = null;
    testResult.value = null;

    try {
      const result = await testApiDefinition(id, testData);
      testResult.value = result;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to test API definition';
      throw err;
    } finally {
      isTesting.value = false;
    }
  }

  async function fetchApiDefinitionsByHeader(headerId: number): Promise<ApiDefinition[]> {
    isLoading.value = true;
    error.value = null;

    try {
      const headerApiDefs = await getApiDefinitionsByHeader(headerId);
      return headerApiDefs;
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to fetch API definitions by header';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchApiDefinitionsByBody(
    bodyId: number,
    bodyType: 'request' | 'response',
  ): Promise<ApiDefinition[]> {
    isLoading.value = true;
    error.value = null;

    try {
      const bodyApiDefs = await getApiDefinitionsByBody(bodyId, bodyType);
      return bodyApiDefs;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch API definitions by body';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  function setCurrentApiDefinition(apiDef: ApiDefinition | null): void {
    currentApiDefinition.value = apiDef;
  }

  function setPage(page: number): void {
    currentPage.value = page;
  }

  function setPageSize(size: number): void {
    pageSize.value = size;
    currentPage.value = 1; // Reset to first page
  }

  function clearError(): void {
    error.value = null;
  }

  function clearTestResult(): void {
    testResult.value = null;
  }

  function clearCurrentApiDefinition(): void {
    currentApiDefinition.value = null;
  }

  function reset(): void {
    apiDefinitions.value = [];
    currentApiDefinition.value = null;
    isLoading.value = false;
    isSaving.value = false;
    isTesting.value = false;
    error.value = null;
    testResult.value = null;
    totalCount.value = 0;
    currentPage.value = 1;
  }

  // Return store interface
  return {
    // State
    apiDefinitions,
    currentApiDefinition,
    isLoading,
    isSaving,
    isTesting,
    error,
    testResult,
    totalCount,
    currentPage,
    pageSize,

    // Computed
    getApiDefinitionsList,
    postApiDefinitions,
    putApiDefinitions,
    patchApiDefinitions,
    deleteApiDefinitions,
    activeApiDefinitions,
    hasApiDefinitions,
    totalPages,
    apiDefinitionsByMethod,

    // Actions
    fetchApiDefinitions,
    fetchApiDefinitionById,
    createNewApiDefinition,
    updateExistingApiDefinition,
    deleteApiDefinitionById,
    duplicateExistingApiDefinition,
    fetchApiDefinitionsByMethod,
    searchApiDefinitionsByQuery,
    testApiDefinitionById,
    fetchApiDefinitionsByHeader,
    fetchApiDefinitionsByBody,
    setCurrentApiDefinition,
    setPage,
    setPageSize,
    clearError,
    clearTestResult,
    clearCurrentApiDefinition,
    reset,
  };
});
