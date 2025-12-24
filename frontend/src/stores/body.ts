/**
 * Body Store
 *
 * Layer 1: API Definition Components - Body Management
 * Manages state for reusable request/response body templates.
 */

import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import {
  type Body,
  type BodyCreate,
  type BodyListParams,
  type BodyScope,
  type BodyType,
  type BodyUpdate,
  createBody,
  deleteBody,
  duplicateBody,
  getBodies,
  getBodiesByScope,
  getBodiesByType,
  getBody,
  searchBodies,
  updateBody,
  validateBodySchema,
} from '@/api/body';

export const useBodyStore = defineStore('body', () => {
  // State
  const bodies = ref<Body[]>([]);
  const currentBody = ref<Body | null>(null);
  const isLoading = ref(false);
  const isSaving = ref(false);
  const isValidating = ref(false);
  const error = ref<string | null>(null);
  const validationErrors = ref<string[]>([]);
  const totalCount = ref(0);
  const currentPage = ref(1);
  const pageSize = ref(20);

  // Computed
  const requestBodies = computed(() =>
    bodies.value.filter(b => (b.bodyType === 'request' || b.bodyType === 'both') && b.isActive),
  );

  const responseBodies = computed(() =>
    bodies.value.filter(b => (b.bodyType === 'response' || b.bodyType === 'both') && b.isActive),
  );

  const globalBodies = computed(() => bodies.value.filter(b => b.scope === 'global' && b.isActive));

  const projectBodies = computed(() =>
    bodies.value.filter(b => b.scope === 'project' && b.isActive),
  );

  const privateBodies = computed(() =>
    bodies.value.filter(b => b.scope === 'private' && b.isActive),
  );

  const activeBodies = computed(() => bodies.value.filter(b => b.isActive));

  const hasBodies = computed(() => bodies.value.length > 0);

  const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value));

  // Actions
  async function fetchBodies(params?: BodyListParams): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await getBodies({
        page: currentPage.value,
        pageSize: pageSize.value,
        ...params,
      });

      bodies.value = response.items;
      totalCount.value = response.total;
      currentPage.value = response.page;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch bodies';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchBodyById(id: number): Promise<Body> {
    isLoading.value = true;
    error.value = null;

    try {
      const body = await getBody(id);
      currentBody.value = body;
      return body;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch body';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function createNewBody(data: BodyCreate): Promise<Body> {
    isSaving.value = true;
    error.value = null;

    try {
      const body = await createBody(data);
      bodies.value.unshift(body);
      totalCount.value += 1;
      return body;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create body';
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  async function updateExistingBody(id: number, data: BodyUpdate): Promise<Body> {
    isSaving.value = true;
    error.value = null;

    try {
      const updatedBody = await updateBody(id, data);

      // Update in list
      const index = bodies.value.findIndex(b => b.id === id);
      if (index !== -1) {
        bodies.value[index] = updatedBody;
      }

      // Update current if it's the same
      if (currentBody.value?.id === id) {
        currentBody.value = updatedBody;
      }

      return updatedBody;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update body';
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  async function deleteBodyById(id: number): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      await deleteBody(id);

      // Remove from list
      bodies.value = bodies.value.filter(b => b.id !== id);
      totalCount.value -= 1;

      // Clear current if it's the same
      if (currentBody.value?.id === id) {
        currentBody.value = null;
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete body';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function duplicateExistingBody(id: number, newName?: string): Promise<Body> {
    isSaving.value = true;
    error.value = null;

    try {
      const duplicated = await duplicateBody(id, newName);
      bodies.value.unshift(duplicated);
      totalCount.value += 1;
      return duplicated;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to duplicate body';
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  async function fetchBodiesByType(bodyType: BodyType): Promise<Body[]> {
    isLoading.value = true;
    error.value = null;

    try {
      const typedBodies = await getBodiesByType(bodyType);
      return typedBodies;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch bodies by type';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchBodiesByScope(scope: BodyScope): Promise<Body[]> {
    isLoading.value = true;
    error.value = null;

    try {
      const scopedBodies = await getBodiesByScope(scope);
      return scopedBodies;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch bodies by scope';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function searchBodiesByQuery(query: string): Promise<Body[]> {
    isLoading.value = true;
    error.value = null;

    try {
      const results = await searchBodies(query);
      return results;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to search bodies';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function validateSchema(schema: Record<string, unknown>): Promise<boolean> {
    isValidating.value = true;
    validationErrors.value = [];
    error.value = null;

    try {
      const result = await validateBodySchema(schema);
      if (!result.valid && result.errors) {
        validationErrors.value = result.errors;
      }
      return result.valid;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to validate schema';
      throw err;
    } finally {
      isValidating.value = false;
    }
  }

  function setCurrentBody(body: Body | null): void {
    currentBody.value = body;
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

  function clearValidationErrors(): void {
    validationErrors.value = [];
  }

  function clearCurrentBody(): void {
    currentBody.value = null;
  }

  function reset(): void {
    bodies.value = [];
    currentBody.value = null;
    isLoading.value = false;
    isSaving.value = false;
    isValidating.value = false;
    error.value = null;
    validationErrors.value = [];
    totalCount.value = 0;
    currentPage.value = 1;
  }

  // Return store interface
  return {
    // State
    bodies,
    currentBody,
    isLoading,
    isSaving,
    isValidating,
    error,
    validationErrors,
    totalCount,
    currentPage,
    pageSize,

    // Computed
    requestBodies,
    responseBodies,
    globalBodies,
    projectBodies,
    privateBodies,
    activeBodies,
    hasBodies,
    totalPages,

    // Actions
    fetchBodies,
    fetchBodyById,
    createNewBody,
    updateExistingBody,
    deleteBodyById,
    duplicateExistingBody,
    fetchBodiesByType,
    fetchBodiesByScope,
    searchBodiesByQuery,
    validateSchema,
    setCurrentBody,
    setPage,
    setPageSize,
    clearError,
    clearValidationErrors,
    clearCurrentBody,
    reset,
  };
});
