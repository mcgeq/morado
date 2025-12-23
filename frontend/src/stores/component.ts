/**
 * Component Store
 *
 * Layer 3: Test Components - Component Management and Execution
 * Manages state for composite components that combine multiple scripts.
 */

import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import {
  addScriptToComponent,
  type ComponentExecutionResult,
  type ComponentListParams,
  type ComponentScript,
  type ComponentScriptCreate,
  type ComponentScriptUpdate,
  type ComponentType,
  createComponent,
  deleteComponent,
  duplicateComponent,
  type ExecutionMode,
  executeComponent,
  getChildComponents,
  getComponent,
  getComponentHierarchy,
  getComponentScripts,
  getComponents,
  getComponentsByType,
  removeScriptFromComponent,
  reorderComponentScripts,
  searchComponents,
  type TestComponent,
  type TestComponentCreate,
  type TestComponentUpdate,
  updateComponent,
  updateComponentScript,
} from '@/api/component';

export const useComponentStore = defineStore('component', () => {
  // State
  const components = ref<TestComponent[]>([]);
  const currentComponent = ref<TestComponent | null>(null);
  const componentScripts = ref<ComponentScript[]>([]);
  const componentHierarchy = ref<{
    component: TestComponent;
    children: TestComponent[];
    scripts: ComponentScript[];
  } | null>(null);
  const isLoading = ref(false);
  const isSaving = ref(false);
  const isExecuting = ref(false);
  const error = ref<string | null>(null);
  const executionResult = ref<ComponentExecutionResult | null>(null);
  const totalCount = ref(0);
  const currentPage = ref(1);
  const pageSize = ref(20);

  // Computed
  const simpleComponents = computed(() =>
    components.value.filter(c => c.componentType === 'simple' && c.isActive),
  );

  const compositeComponents = computed(() =>
    components.value.filter(c => c.componentType === 'composite' && c.isActive),
  );

  const templateComponents = computed(() =>
    components.value.filter(c => c.componentType === 'template' && c.isActive),
  );

  const sequentialComponents = computed(() =>
    components.value.filter(c => c.executionMode === 'sequential' && c.isActive),
  );

  const parallelComponents = computed(() =>
    components.value.filter(c => c.executionMode === 'parallel' && c.isActive),
  );

  const conditionalComponents = computed(() =>
    components.value.filter(c => c.executionMode === 'conditional' && c.isActive),
  );

  const rootComponents = computed(() =>
    components.value.filter(c => !c.parentComponentId && c.isActive),
  );

  const nestedComponents = computed(() =>
    components.value.filter(c => c.parentComponentId && c.isActive),
  );

  const activeComponents = computed(() => components.value.filter(c => c.isActive));

  const hasComponents = computed(() => components.value.length > 0);

  const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value));

  const componentsByType = computed(() => {
    const grouped: Record<ComponentType, TestComponent[]> = {
      simple: [],
      composite: [],
      template: [],
    };

    components.value.forEach(component => {
      if (component.isActive) {
        grouped[component.componentType].push(component);
      }
    });

    return grouped;
  });

  const componentsByExecutionMode = computed(() => {
    const grouped: Record<ExecutionMode, TestComponent[]> = {
      sequential: [],
      parallel: [],
      conditional: [],
    };

    components.value.forEach(component => {
      if (component.isActive) {
        grouped[component.executionMode].push(component);
      }
    });

    return grouped;
  });

  // Actions
  async function fetchComponents(params?: ComponentListParams): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await getComponents({
        page: currentPage.value,
        pageSize: pageSize.value,
        ...params,
      });

      components.value = response.items;
      totalCount.value = response.total;
      currentPage.value = response.page;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch components';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchComponentById(id: number): Promise<TestComponent> {
    isLoading.value = true;
    error.value = null;

    try {
      const component = await getComponent(id);
      currentComponent.value = component;
      return component;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch component';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function createNewComponent(data: TestComponentCreate): Promise<TestComponent> {
    isSaving.value = true;
    error.value = null;

    try {
      const component = await createComponent(data);
      components.value.unshift(component);
      totalCount.value += 1;
      return component;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create component';
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  async function updateExistingComponent(
    id: number,
    data: TestComponentUpdate,
  ): Promise<TestComponent> {
    isSaving.value = true;
    error.value = null;

    try {
      const updatedComponent = await updateComponent(id, data);

      // Update in list
      const index = components.value.findIndex(c => c.id === id);
      if (index !== -1) {
        components.value[index] = updatedComponent;
      }

      // Update current if it's the same
      if (currentComponent.value?.id === id) {
        currentComponent.value = updatedComponent;
      }

      return updatedComponent;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update component';
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  async function deleteComponentById(id: number): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      await deleteComponent(id);

      // Remove from list
      components.value = components.value.filter(c => c.id !== id);
      totalCount.value -= 1;

      // Clear current if it's the same
      if (currentComponent.value?.id === id) {
        currentComponent.value = null;
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete component';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function duplicateExistingComponent(id: number, newName?: string): Promise<TestComponent> {
    isSaving.value = true;
    error.value = null;

    try {
      const duplicated = await duplicateComponent(id, newName);
      components.value.unshift(duplicated);
      totalCount.value += 1;
      return duplicated;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to duplicate component';
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  async function executeComponentById(
    id: number,
    runtimeParams?: Record<string, unknown>,
  ): Promise<ComponentExecutionResult> {
    isExecuting.value = true;
    error.value = null;
    executionResult.value = null;

    try {
      const result = await executeComponent(id, runtimeParams);
      executionResult.value = result;
      return result;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to execute component';
      throw err;
    } finally {
      isExecuting.value = false;
    }
  }

  async function fetchComponentHierarchy(id: number): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      const hierarchy = await getComponentHierarchy(id);
      componentHierarchy.value = hierarchy;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch component hierarchy';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchChildComponents(parentId: number): Promise<TestComponent[]> {
    isLoading.value = true;
    error.value = null;

    try {
      const children = await getChildComponents(parentId);
      return children;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch child components';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchComponentsByType(componentType: ComponentType): Promise<TestComponent[]> {
    isLoading.value = true;
    error.value = null;

    try {
      const typedComponents = await getComponentsByType(componentType);
      return typedComponents;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch components by type';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function searchComponentsByQuery(query: string): Promise<TestComponent[]> {
    isLoading.value = true;
    error.value = null;

    try {
      const results = await searchComponents(query);
      return results;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to search components';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // Component-Script Association Actions
  async function fetchComponentScripts(componentId: number): Promise<ComponentScript[]> {
    isLoading.value = true;
    error.value = null;

    try {
      const scripts = await getComponentScripts(componentId);
      componentScripts.value = scripts;
      return scripts;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch component scripts';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function addScriptToComponentById(data: ComponentScriptCreate): Promise<ComponentScript> {
    isSaving.value = true;
    error.value = null;

    try {
      const componentScript = await addScriptToComponent(data);
      componentScripts.value.push(componentScript);
      return componentScript;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to add script to component';
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  async function updateExistingComponentScript(
    id: number,
    data: ComponentScriptUpdate,
  ): Promise<ComponentScript> {
    isSaving.value = true;
    error.value = null;

    try {
      const updatedComponentScript = await updateComponentScript(id, data);

      // Update in list
      const index = componentScripts.value.findIndex(cs => cs.id === id);
      if (index !== -1) {
        componentScripts.value[index] = updatedComponentScript;
      }

      return updatedComponentScript;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update component script';
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  async function removeScriptFromComponentById(id: number): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      await removeScriptFromComponent(id);

      // Remove from list
      componentScripts.value = componentScripts.value.filter(cs => cs.id !== id);
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to remove script from component';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function reorderScripts(
    componentId: number,
    scriptOrders: Array<{ scriptId: number; executionOrder: number }>,
  ): Promise<void> {
    isSaving.value = true;
    error.value = null;

    try {
      await reorderComponentScripts(componentId, scriptOrders);

      // Refresh component scripts
      await fetchComponentScripts(componentId);
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to reorder component scripts';
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  function setCurrentComponent(component: TestComponent | null): void {
    currentComponent.value = component;
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

  function clearCurrentComponent(): void {
    currentComponent.value = null;
  }

  function clearComponentScripts(): void {
    componentScripts.value = [];
  }

  function clearComponentHierarchy(): void {
    componentHierarchy.value = null;
  }

  function reset(): void {
    components.value = [];
    currentComponent.value = null;
    componentScripts.value = [];
    componentHierarchy.value = null;
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
    components,
    currentComponent,
    componentScripts,
    componentHierarchy,
    isLoading,
    isSaving,
    isExecuting,
    error,
    executionResult,
    totalCount,
    currentPage,
    pageSize,

    // Computed
    simpleComponents,
    compositeComponents,
    templateComponents,
    sequentialComponents,
    parallelComponents,
    conditionalComponents,
    rootComponents,
    nestedComponents,
    activeComponents,
    hasComponents,
    totalPages,
    componentsByType,
    componentsByExecutionMode,

    // Actions
    fetchComponents,
    fetchComponentById,
    createNewComponent,
    updateExistingComponent,
    deleteComponentById,
    duplicateExistingComponent,
    executeComponentById,
    fetchComponentHierarchy,
    fetchChildComponents,
    fetchComponentsByType,
    searchComponentsByQuery,
    fetchComponentScripts,
    addScriptToComponentById,
    updateExistingComponentScript,
    removeScriptFromComponentById,
    reorderScripts,
    setCurrentComponent,
    setPage,
    setPageSize,
    clearError,
    clearExecutionResult,
    clearCurrentComponent,
    clearComponentScripts,
    clearComponentHierarchy,
    reset,
  };
});
