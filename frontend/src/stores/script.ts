/**
 * Script Store
 *
 * Layer 2: Test Scripts - Script Management and Execution
 * Manages state for test scripts that reference API definitions.
 */

import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import {
  createScript,
  createScriptParameter,
  debugScript,
  deleteScript,
  deleteScriptParameter,
  duplicateScript,
  executeScript,
  getScript,
  getScriptParameters,
  getScripts,
  getScriptsByApiDefinition,
  getScriptsByType,
  type ScriptExecutionResult,
  type ScriptListParams,
  type ScriptParameter,
  type ScriptParameterCreate,
  type ScriptParameterUpdate,
  type ScriptType,
  searchScripts,
  type TestScript,
  type TestScriptCreate,
  type TestScriptUpdate,
  updateScript,
  updateScriptParameter,
} from '@/api/script';

export const useScriptStore = defineStore('script', () => {
  // State
  const scripts = ref<TestScript[]>([]);
  const currentScript = ref<TestScript | null>(null);
  const scriptParameters = ref<ScriptParameter[]>([]);
  const isLoading = ref(false);
  const isSaving = ref(false);
  const isExecuting = ref(false);
  const isDebugging = ref(false);
  const error = ref<string | null>(null);
  const executionResult = ref<ScriptExecutionResult | null>(null);
  const totalCount = ref(0);
  const currentPage = ref(1);
  const pageSize = ref(20);

  // Computed
  const setupScripts = computed(() =>
    scripts.value.filter(s => s.scriptType === 'setup' && s.isActive),
  );

  const mainScripts = computed(() =>
    scripts.value.filter(s => s.scriptType === 'main' && s.isActive),
  );

  const teardownScripts = computed(() =>
    scripts.value.filter(s => s.scriptType === 'teardown' && s.isActive),
  );

  const utilityScripts = computed(() =>
    scripts.value.filter(s => s.scriptType === 'utility' && s.isActive),
  );

  const activeScripts = computed(() => scripts.value.filter(s => s.isActive));

  const debugModeScripts = computed(() => scripts.value.filter(s => s.debugMode));

  const hasScripts = computed(() => scripts.value.length > 0);

  const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value));

  const scriptsByType = computed(() => {
    const grouped: Record<ScriptType, TestScript[]> = {
      setup: [],
      main: [],
      teardown: [],
      utility: [],
    };

    scripts.value.forEach(script => {
      if (script.isActive) {
        grouped[script.scriptType].push(script);
      }
    });

    return grouped;
  });

  // Actions
  async function fetchScripts(params?: ScriptListParams): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await getScripts({
        page: currentPage.value,
        pageSize: pageSize.value,
        ...params,
      });

      scripts.value = response.items;
      totalCount.value = response.total;
      currentPage.value = response.page;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch scripts';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchScriptById(id: number): Promise<TestScript> {
    isLoading.value = true;
    error.value = null;

    try {
      const script = await getScript(id);
      currentScript.value = script;
      return script;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch script';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function createNewScript(data: TestScriptCreate): Promise<TestScript> {
    isSaving.value = true;
    error.value = null;

    try {
      const script = await createScript(data);
      scripts.value.unshift(script);
      totalCount.value += 1;
      return script;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create script';
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  async function updateExistingScript(id: number, data: TestScriptUpdate): Promise<TestScript> {
    isSaving.value = true;
    error.value = null;

    try {
      const updatedScript = await updateScript(id, data);

      // Update in list
      const index = scripts.value.findIndex(s => s.id === id);
      if (index !== -1) {
        scripts.value[index] = updatedScript;
      }

      // Update current if it's the same
      if (currentScript.value?.id === id) {
        currentScript.value = updatedScript;
      }

      return updatedScript;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update script';
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  async function deleteScriptById(id: number): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      await deleteScript(id);

      // Remove from list
      scripts.value = scripts.value.filter(s => s.id !== id);
      totalCount.value -= 1;

      // Clear current if it's the same
      if (currentScript.value?.id === id) {
        currentScript.value = null;
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete script';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function duplicateExistingScript(id: number, newName?: string): Promise<TestScript> {
    isSaving.value = true;
    error.value = null;

    try {
      const duplicated = await duplicateScript(id, newName);
      scripts.value.unshift(duplicated);
      totalCount.value += 1;
      return duplicated;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to duplicate script';
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  async function executeScriptById(
    id: number,
    runtimeParams?: Record<string, unknown>,
  ): Promise<ScriptExecutionResult> {
    isExecuting.value = true;
    error.value = null;
    executionResult.value = null;

    try {
      const result = await executeScript(id, runtimeParams);
      executionResult.value = result;
      return result;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to execute script';
      throw err;
    } finally {
      isExecuting.value = false;
    }
  }

  async function debugScriptById(
    id: number,
    breakpoints?: unknown[],
    runtimeParams?: Record<string, unknown>,
  ): Promise<ScriptExecutionResult> {
    isDebugging.value = true;
    error.value = null;
    executionResult.value = null;

    try {
      const result = await debugScript(id, breakpoints, runtimeParams);
      executionResult.value = result;
      return result;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to debug script';
      throw err;
    } finally {
      isDebugging.value = false;
    }
  }

  async function fetchScriptsByType(scriptType: ScriptType): Promise<TestScript[]> {
    isLoading.value = true;
    error.value = null;

    try {
      const typedScripts = await getScriptsByType(scriptType);
      return typedScripts;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch scripts by type';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchScriptsByApiDefinition(apiDefinitionId: number): Promise<TestScript[]> {
    isLoading.value = true;
    error.value = null;

    try {
      const apiScripts = await getScriptsByApiDefinition(apiDefinitionId);
      return apiScripts;
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to fetch scripts by API definition';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function searchScriptsByQuery(query: string): Promise<TestScript[]> {
    isLoading.value = true;
    error.value = null;

    try {
      const results = await searchScripts(query);
      return results;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to search scripts';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // Script Parameter Actions
  async function fetchScriptParameters(scriptId: number): Promise<ScriptParameter[]> {
    isLoading.value = true;
    error.value = null;

    try {
      const params = await getScriptParameters(scriptId);
      scriptParameters.value = params;
      return params;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch script parameters';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function createNewScriptParameter(data: ScriptParameterCreate): Promise<ScriptParameter> {
    isSaving.value = true;
    error.value = null;

    try {
      const param = await createScriptParameter(data);
      scriptParameters.value.push(param);
      return param;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create script parameter';
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  async function updateExistingScriptParameter(
    id: number,
    data: ScriptParameterUpdate,
  ): Promise<ScriptParameter> {
    isSaving.value = true;
    error.value = null;

    try {
      const updatedParam = await updateScriptParameter(id, data);

      // Update in list
      const index = scriptParameters.value.findIndex(p => p.id === id);
      if (index !== -1) {
        scriptParameters.value[index] = updatedParam;
      }

      return updatedParam;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update script parameter';
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  async function deleteScriptParameterById(id: number): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      await deleteScriptParameter(id);

      // Remove from list
      scriptParameters.value = scriptParameters.value.filter(p => p.id !== id);
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete script parameter';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  function setCurrentScript(script: TestScript | null): void {
    currentScript.value = script;
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

  function clearExecutionResult(): void {
    executionResult.value = null;
  }

  function clearCurrentScript(): void {
    currentScript.value = null;
  }

  function clearScriptParameters(): void {
    scriptParameters.value = [];
  }

  function reset(): void {
    scripts.value = [];
    currentScript.value = null;
    scriptParameters.value = [];
    isLoading.value = false;
    isSaving.value = false;
    isExecuting.value = false;
    isDebugging.value = false;
    error.value = null;
    executionResult.value = null;
    totalCount.value = 0;
    currentPage.value = 1;
  }

  // Return store interface
  return {
    // State
    scripts,
    currentScript,
    scriptParameters,
    isLoading,
    isSaving,
    isExecuting,
    isDebugging,
    error,
    executionResult,
    totalCount,
    currentPage,
    pageSize,

    // Computed
    setupScripts,
    mainScripts,
    teardownScripts,
    utilityScripts,
    activeScripts,
    debugModeScripts,
    hasScripts,
    totalPages,
    scriptsByType,

    // Actions
    fetchScripts,
    fetchScriptById,
    createNewScript,
    updateExistingScript,
    deleteScriptById,
    duplicateExistingScript,
    executeScriptById,
    debugScriptById,
    fetchScriptsByType,
    fetchScriptsByApiDefinition,
    searchScriptsByQuery,
    fetchScriptParameters,
    createNewScriptParameter,
    updateExistingScriptParameter,
    deleteScriptParameterById,
    setCurrentScript,
    setPage,
    setPageSize,
    clearError,
    clearExecutionResult,
    clearCurrentScript,
    clearScriptParameters,
    reset,
  };
});
