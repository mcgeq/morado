/**
 * Header Store
 *
 * Layer 1: API Definition Components - Header Management
 * Manages state for reusable HTTP header components.
 */

import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import {
  createHeader,
  deleteHeader,
  duplicateHeader,
  getHeader,
  getHeaders,
  getHeadersByScope,
  type Header,
  type HeaderCreate,
  type HeaderListParams,
  type HeaderScope,
  type HeaderUpdate,
  searchHeaders,
  updateHeader,
} from '@/api/header';

export const useHeaderStore = defineStore('header', () => {
  // State
  const headers = ref<Header[]>([]);
  const currentHeader = ref<Header | null>(null);
  const isLoading = ref(false);
  const isSaving = ref(false);
  const error = ref<string | null>(null);
  const totalCount = ref(0);
  const currentPage = ref(1);
  const pageSize = ref(20);

  // Computed
  const globalHeaders = computed(() =>
    headers.value.filter(h => h.scope === 'global' && h.isActive),
  );

  const projectHeaders = computed(() =>
    headers.value.filter(h => h.scope === 'project' && h.isActive),
  );

  const privateHeaders = computed(() =>
    headers.value.filter(h => h.scope === 'private' && h.isActive),
  );

  const activeHeaders = computed(() => headers.value.filter(h => h.isActive));

  const hasHeaders = computed(() => headers.value.length > 0);

  const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value));

  // Actions
  async function fetchHeaders(params?: HeaderListParams): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await getHeaders({
        page: currentPage.value,
        pageSize: pageSize.value,
        ...params,
      });

      headers.value = response.items;
      totalCount.value = response.total;
      currentPage.value = response.page;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch headers';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchHeaderById(id: number): Promise<Header> {
    isLoading.value = true;
    error.value = null;

    try {
      const header = await getHeader(id);
      currentHeader.value = header;
      return header;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch header';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function createNewHeader(data: HeaderCreate): Promise<Header> {
    isSaving.value = true;
    error.value = null;

    try {
      const header = await createHeader(data);
      headers.value.unshift(header);
      totalCount.value += 1;
      return header;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create header';
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  async function updateExistingHeader(id: number, data: HeaderUpdate): Promise<Header> {
    isSaving.value = true;
    error.value = null;

    try {
      const updatedHeader = await updateHeader(id, data);

      // Update in list
      const index = headers.value.findIndex(h => h.id === id);
      if (index !== -1) {
        headers.value[index] = updatedHeader;
      }

      // Update current if it's the same
      if (currentHeader.value?.id === id) {
        currentHeader.value = updatedHeader;
      }

      return updatedHeader;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update header';
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  async function deleteHeaderById(id: number): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      await deleteHeader(id);

      // Remove from list
      headers.value = headers.value.filter(h => h.id !== id);
      totalCount.value -= 1;

      // Clear current if it's the same
      if (currentHeader.value?.id === id) {
        currentHeader.value = null;
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete header';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function duplicateExistingHeader(id: number, newName?: string): Promise<Header> {
    isSaving.value = true;
    error.value = null;

    try {
      const duplicated = await duplicateHeader(id, newName);
      headers.value.unshift(duplicated);
      totalCount.value += 1;
      return duplicated;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to duplicate header';
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  async function fetchHeadersByScope(scope: HeaderScope): Promise<Header[]> {
    isLoading.value = true;
    error.value = null;

    try {
      const scopedHeaders = await getHeadersByScope(scope);
      return scopedHeaders;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch headers by scope';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function searchHeadersByQuery(query: string): Promise<Header[]> {
    isLoading.value = true;
    error.value = null;

    try {
      const results = await searchHeaders(query);
      return results;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to search headers';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  function setCurrentHeader(header: Header | null): void {
    currentHeader.value = header;
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

  function clearCurrentHeader(): void {
    currentHeader.value = null;
  }

  function reset(): void {
    headers.value = [];
    currentHeader.value = null;
    isLoading.value = false;
    isSaving.value = false;
    error.value = null;
    totalCount.value = 0;
    currentPage.value = 1;
  }

  // Return store interface
  return {
    // State
    headers,
    currentHeader,
    isLoading,
    isSaving,
    error,
    totalCount,
    currentPage,
    pageSize,

    // Computed
    globalHeaders,
    projectHeaders,
    privateHeaders,
    activeHeaders,
    hasHeaders,
    totalPages,

    // Actions
    fetchHeaders,
    fetchHeaderById,
    createNewHeader,
    updateExistingHeader,
    deleteHeaderById,
    duplicateExistingHeader,
    fetchHeadersByScope,
    searchHeadersByQuery,
    setCurrentHeader,
    setPage,
    setPageSize,
    clearError,
    clearCurrentHeader,
    reset,
  };
});
