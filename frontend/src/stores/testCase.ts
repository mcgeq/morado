/**
 * Test Case Store
 *
 * Layer 4: Test Cases - Test Case Management and Execution
 * Manages state for test cases that reference scripts and components.
 */

import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import {
  addComponentToTestCase,
  addScriptToTestCase,
  createTestCase,
  deleteTestCase,
  duplicateTestCase,
  executeTestCase,
  getTestCase,
  getTestCaseComponents,
  getTestCaseExecutionHistory,
  getTestCaseScripts,
  getTestCases,
  getTestCasesByCategory,
  getTestCasesByPriority,
  getTestCasesByStatus,
  removeComponentFromTestCase,
  removeScriptFromTestCase,
  searchTestCases,
  type TestCase,
  type TestCaseComponent,
  type TestCaseComponentCreate,
  type TestCaseComponentUpdate,
  type TestCaseCreate,
  type TestCaseExecutionResult,
  type TestCaseListParams,
  type TestCasePriority,
  type TestCaseScript,
  type TestCaseScriptCreate,
  type TestCaseScriptUpdate,
  type TestCaseStatus,
  type TestCaseUpdate,
  updateTestCase,
  updateTestCaseComponent,
  updateTestCaseScript,
} from '@/api/test-case';

export const useTestCaseStore = defineStore('testCase', () => {
  // State
  const testCases = ref<TestCase[]>([]);
  const currentTestCase = ref<TestCase | null>(null);
  const testCaseScripts = ref<TestCaseScript[]>([]);
  const testCaseComponents = ref<TestCaseComponent[]>([]);
  const executionHistory = ref<TestCaseExecutionResult[]>([]);
  const isLoading = ref(false);
  const isSaving = ref(false);
  const isExecuting = ref(false);
  const error = ref<string | null>(null);
  const executionResult = ref<TestCaseExecutionResult | null>(null);
  const totalCount = ref(0);
  const currentPage = ref(1);
  const pageSize = ref(20);

  // Computed
  const lowPriorityTestCases = computed(() =>
    testCases.value.filter(tc => tc.priority === 'low' && tc.status === 'active'),
  );

  const mediumPriorityTestCases = computed(() =>
    testCases.value.filter(tc => tc.priority === 'medium' && tc.status === 'active'),
  );

  const highPriorityTestCases = computed(() =>
    testCases.value.filter(tc => tc.priority === 'high' && tc.status === 'active'),
  );

  const criticalPriorityTestCases = computed(() =>
    testCases.value.filter(tc => tc.priority === 'critical' && tc.status === 'active'),
  );

  const draftTestCases = computed(() => testCases.value.filter(tc => tc.status === 'draft'));

  const activeTestCases = computed(() => testCases.value.filter(tc => tc.status === 'active'));

  const deprecatedTestCases = computed(() =>
    testCases.value.filter(tc => tc.status === 'deprecated'),
  );

  const archivedTestCases = computed(() => testCases.value.filter(tc => tc.status === 'archived'));

  const automatedTestCases = computed(() =>
    testCases.value.filter(tc => tc.isAutomated && tc.status === 'active'),
  );

  const manualTestCases = computed(() =>
    testCases.value.filter(tc => !tc.isAutomated && tc.status === 'active'),
  );

  const hasTestCases = computed(() => testCases.value.length > 0);

  const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value));

  const testCasesByPriority = computed(() => {
    const grouped: Record<TestCasePriority, TestCase[]> = {
      low: [],
      medium: [],
      high: [],
      critical: [],
    };

    testCases.value.forEach(testCase => {
      if (testCase.status === 'active') {
        grouped[testCase.priority].push(testCase);
      }
    });

    return grouped;
  });

  const testCasesByStatus = computed(() => {
    const grouped: Record<TestCaseStatus, TestCase[]> = {
      draft: [],
      active: [],
      deprecated: [],
      archived: [],
    };

    testCases.value.forEach(testCase => {
      grouped[testCase.status].push(testCase);
    });

    return grouped;
  });

  const testCasesByCategory = computed(() => {
    const grouped: Record<string, TestCase[]> = {};

    testCases.value.forEach(testCase => {
      const category = testCase.category || 'Uncategorized';
      if (!grouped[category]) {
        grouped[category] = [];
      }
      grouped[category].push(testCase);
    });

    return grouped;
  });

  // Actions
  async function fetchTestCases(params?: TestCaseListParams): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await getTestCases({
        page: currentPage.value,
        pageSize: pageSize.value,
        ...params,
      });

      testCases.value = response.items;
      totalCount.value = response.total;
      currentPage.value = response.page;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch test cases';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchTestCaseById(id: number): Promise<TestCase> {
    isLoading.value = true;
    error.value = null;

    try {
      const testCase = await getTestCase(id);
      currentTestCase.value = testCase;
      return testCase;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch test case';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function createNewTestCase(data: TestCaseCreate): Promise<TestCase> {
    isSaving.value = true;
    error.value = null;

    try {
      const testCase = await createTestCase(data);
      testCases.value.unshift(testCase);
      totalCount.value += 1;
      return testCase;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create test case';
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  async function updateExistingTestCase(id: number, data: TestCaseUpdate): Promise<TestCase> {
    isSaving.value = true;
    error.value = null;

    try {
      const updatedTestCase = await updateTestCase(id, data);

      // Update in list
      const index = testCases.value.findIndex(tc => tc.id === id);
      if (index !== -1) {
        testCases.value[index] = updatedTestCase;
      }

      // Update current if it's the same
      if (currentTestCase.value?.id === id) {
        currentTestCase.value = updatedTestCase;
      }

      return updatedTestCase;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update test case';
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  async function deleteTestCaseById(id: number): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      await deleteTestCase(id);

      // Remove from list
      testCases.value = testCases.value.filter(tc => tc.id !== id);
      totalCount.value -= 1;

      // Clear current if it's the same
      if (currentTestCase.value?.id === id) {
        currentTestCase.value = null;
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete test case';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function duplicateExistingTestCase(id: number, newName?: string): Promise<TestCase> {
    isSaving.value = true;
    error.value = null;

    try {
      const duplicated = await duplicateTestCase(id, newName);
      testCases.value.unshift(duplicated);
      totalCount.value += 1;
      return duplicated;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to duplicate test case';
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  async function executeTestCaseById(
    id: number,
    runtimeParams?: Record<string, unknown>,
  ): Promise<TestCaseExecutionResult> {
    isExecuting.value = true;
    error.value = null;
    executionResult.value = null;

    try {
      const result = await executeTestCase(id, runtimeParams);
      executionResult.value = result;

      // Add to execution history
      executionHistory.value.unshift(result);

      return result;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to execute test case';
      throw err;
    } finally {
      isExecuting.value = false;
    }
  }

  async function fetchTestCasesByPriority(priority: TestCasePriority): Promise<TestCase[]> {
    isLoading.value = true;
    error.value = null;

    try {
      const priorityTestCases = await getTestCasesByPriority(priority);
      return priorityTestCases;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch test cases by priority';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchTestCasesByStatus(status: TestCaseStatus): Promise<TestCase[]> {
    isLoading.value = true;
    error.value = null;

    try {
      const statusTestCases = await getTestCasesByStatus(status);
      return statusTestCases;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch test cases by status';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchTestCasesByCategory(category: string): Promise<TestCase[]> {
    isLoading.value = true;
    error.value = null;

    try {
      const categoryTestCases = await getTestCasesByCategory(category);
      return categoryTestCases;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch test cases by category';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function searchTestCasesByQuery(query: string): Promise<TestCase[]> {
    isLoading.value = true;
    error.value = null;

    try {
      const results = await searchTestCases(query);
      return results;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to search test cases';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // Test Case Script Association Actions
  async function fetchTestCaseScripts(testCaseId: number): Promise<TestCaseScript[]> {
    isLoading.value = true;
    error.value = null;

    try {
      const scripts = await getTestCaseScripts(testCaseId);
      testCaseScripts.value = scripts;
      return scripts;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch test case scripts';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function addScriptToTestCaseById(data: TestCaseScriptCreate): Promise<TestCaseScript> {
    isSaving.value = true;
    error.value = null;

    try {
      const testCaseScript = await addScriptToTestCase(data);
      testCaseScripts.value.push(testCaseScript);
      return testCaseScript;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to add script to test case';
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  async function updateExistingTestCaseScript(
    id: number,
    data: TestCaseScriptUpdate,
  ): Promise<TestCaseScript> {
    isSaving.value = true;
    error.value = null;

    try {
      const updatedTestCaseScript = await updateTestCaseScript(id, data);

      // Update in list
      const index = testCaseScripts.value.findIndex(tcs => tcs.id === id);
      if (index !== -1) {
        testCaseScripts.value[index] = updatedTestCaseScript;
      }

      return updatedTestCaseScript;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update test case script';
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  async function removeScriptFromTestCaseById(id: number): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      await removeScriptFromTestCase(id);

      // Remove from list
      testCaseScripts.value = testCaseScripts.value.filter(tcs => tcs.id !== id);
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to remove script from test case';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // Test Case Component Association Actions
  async function fetchTestCaseComponents(testCaseId: number): Promise<TestCaseComponent[]> {
    isLoading.value = true;
    error.value = null;

    try {
      const components = await getTestCaseComponents(testCaseId);
      testCaseComponents.value = components;
      return components;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch test case components';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function addComponentToTestCaseById(
    data: TestCaseComponentCreate,
  ): Promise<TestCaseComponent> {
    isSaving.value = true;
    error.value = null;

    try {
      const testCaseComponent = await addComponentToTestCase(data);
      testCaseComponents.value.push(testCaseComponent);
      return testCaseComponent;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to add component to test case';
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  async function updateExistingTestCaseComponent(
    id: number,
    data: TestCaseComponentUpdate,
  ): Promise<TestCaseComponent> {
    isSaving.value = true;
    error.value = null;

    try {
      const updatedTestCaseComponent = await updateTestCaseComponent(id, data);

      // Update in list
      const index = testCaseComponents.value.findIndex(tcc => tcc.id === id);
      if (index !== -1) {
        testCaseComponents.value[index] = updatedTestCaseComponent;
      }

      return updatedTestCaseComponent;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update test case component';
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  async function removeComponentFromTestCaseById(id: number): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      await removeComponentFromTestCase(id);

      // Remove from list
      testCaseComponents.value = testCaseComponents.value.filter(tcc => tcc.id !== id);
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to remove component from test case';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchExecutionHistory(testCaseId: number, limit = 10): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      const history = await getTestCaseExecutionHistory(testCaseId, limit);
      executionHistory.value = history;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch execution history';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  function setCurrentTestCase(testCase: TestCase | null): void {
    currentTestCase.value = testCase;
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

  function clearCurrentTestCase(): void {
    currentTestCase.value = null;
  }

  function clearTestCaseScripts(): void {
    testCaseScripts.value = [];
  }

  function clearTestCaseComponents(): void {
    testCaseComponents.value = [];
  }

  function clearExecutionHistory(): void {
    executionHistory.value = [];
  }

  function reset(): void {
    testCases.value = [];
    currentTestCase.value = null;
    testCaseScripts.value = [];
    testCaseComponents.value = [];
    executionHistory.value = [];
    isLoading.value = false;
    isSaving.value = false;
    isExecuting.value = false;
    error.value = null;
    executionResult.value = null;
    totalCount.value = 0;
    currentPage.value = 1;
  }

  // Return store interface
  return {
    // State
    testCases,
    currentTestCase,
    testCaseScripts,
    testCaseComponents,
    executionHistory,
    isLoading,
    isSaving,
    isExecuting,
    error,
    executionResult,
    totalCount,
    currentPage,
    pageSize,

    // Computed
    lowPriorityTestCases,
    mediumPriorityTestCases,
    highPriorityTestCases,
    criticalPriorityTestCases,
    draftTestCases,
    activeTestCases,
    deprecatedTestCases,
    archivedTestCases,
    automatedTestCases,
    manualTestCases,
    hasTestCases,
    totalPages,
    testCasesByPriority,
    testCasesByStatus,
    testCasesByCategory,

    // Actions
    fetchTestCases,
    fetchTestCaseById,
    createNewTestCase,
    updateExistingTestCase,
    deleteTestCaseById,
    duplicateExistingTestCase,
    executeTestCaseById,
    fetchTestCasesByPriority,
    fetchTestCasesByStatus,
    fetchTestCasesByCategory,
    searchTestCasesByQuery,
    fetchTestCaseScripts,
    addScriptToTestCaseById,
    updateExistingTestCaseScript,
    removeScriptFromTestCaseById,
    fetchTestCaseComponents,
    addComponentToTestCaseById,
    updateExistingTestCaseComponent,
    removeComponentFromTestCaseById,
    fetchExecutionHistory,
    setCurrentTestCase,
    setPage,
    setPageSize,
    clearError,
    clearExecutionResult,
    clearCurrentTestCase,
    clearTestCaseScripts,
    clearTestCaseComponents,
    clearExecutionHistory,
    reset,
  };
});
