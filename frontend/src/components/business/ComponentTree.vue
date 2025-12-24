<template>
  <div class="component-tree">
    <!-- Root Component -->
    <div class="card bg-base-100 shadow-md mb-4">
      <div class="card-body p-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6 text-primary"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
              />
            </svg>
            <div>
              <h4 class="font-bold">{{ rootComponent.name }}</h4>
              <div class="flex gap-2 mt-1">
                <span
                  class="badge badge-sm"
                  :class="getTypeBadgeClass(rootComponent.componentType)"
                >
                  {{ rootComponent.componentType }}
                </span>
                <span
                  class="badge badge-sm"
                  :class="getModeBadgeClass(rootComponent.executionMode)"
                >
                  {{ rootComponent.executionMode }}
                </span>
              </div>
            </div>
          </div>
          <button
            type="button"
            class="btn btn-sm btn-ghost"
            @click="$emit('selectComponent', rootComponent)"
          >
            View
          </button>
        </div>
      </div>
    </div>

    <!-- Scripts -->
    <div v-if="scripts && scripts.length > 0" class="ml-8 mb-4">
      <div class="text-sm font-semibold text-base-content/60 mb-2 flex items-center gap-2">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-4 w-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
        Scripts ({{ scripts.length }})
      </div>
      <div class="space-y-2">
        <div
          v-for="script in sortedScripts"
          :key="script.id"
          class="card bg-base-200 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
          @click="$emit('selectScript', script)"
        >
          <div class="card-body p-3">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="badge badge-sm badge-ghost">{{ script.executionOrder }}</span>
                <span class="text-sm font-medium"
                  >{{ script.script?.name || `Script #${script.scriptId}` }}</span
                >
                <span
                  v-if="script.script"
                  class="badge badge-xs"
                  :class="getScriptTypeBadgeClass(script.script.scriptType)"
                >
                  {{ script.script.scriptType }}
                </span>
              </div>
              <div
                v-if="script.parameterOverrides && Object.keys(script.parameterOverrides).length > 0"
                class="tooltip"
                data-tip="Has parameter overrides"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-4 w-4 text-warning"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Child Components -->
    <div v-if="children && children.length > 0" class="ml-8">
      <div class="text-sm font-semibold text-base-content/60 mb-2 flex items-center gap-2">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-4 w-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"
          />
        </svg>
        Child Components ({{ children.length }})
      </div>
      <div class="space-y-4">
        <ComponentTree
          v-for="child in children"
          :key="child.id"
          :root-component="child"
          :children="[]"
          :scripts="[]"
          @select-component="$emit('selectComponent', $event)"
          @select-script="$emit('selectScript', $event)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed } from 'vue';
  import type { ComponentScript, TestComponent } from '@/api/component';

  interface Props {
    rootComponent: TestComponent;
    children?: TestComponent[];
    scripts?: ComponentScript[];
  }

  const props = withDefaults(defineProps<Props>(), {
    children: () => [],
    scripts: () => [],
  });

  defineEmits<{
    selectComponent: [component: TestComponent];
    selectScript: [script: ComponentScript];
  }>();

  const sortedScripts = computed(() => {
    return [...props.scripts].sort((a, b) => a.executionOrder - b.executionOrder);
  });

  function getTypeBadgeClass(type: string): string {
    switch (type) {
      case 'simple':
        return 'badge-info';
      case 'composite':
        return 'badge-primary';
      case 'template':
        return 'badge-secondary';
      default:
        return 'badge-ghost';
    }
  }

  function getModeBadgeClass(mode: string): string {
    switch (mode) {
      case 'sequential':
        return 'badge-success';
      case 'parallel':
        return 'badge-warning';
      case 'conditional':
        return 'badge-accent';
      default:
        return 'badge-ghost';
    }
  }

  function getScriptTypeBadgeClass(type: string): string {
    switch (type) {
      case 'setup':
        return 'badge-info';
      case 'main':
        return 'badge-primary';
      case 'teardown':
        return 'badge-secondary';
      case 'utility':
        return 'badge-accent';
      default:
        return 'badge-ghost';
    }
  }
</script>

<style scoped>
  .component-tree {
    position: relative;
  }

  .component-tree::before {
    content: "";
    position: absolute;
    left: -1rem;
    top: 2rem;
    bottom: 2rem;
    width: 2px;
    background: oklch(var(--bc) / 0.1);
  }

  .component-tree > .ml-8::before {
    content: "";
    position: absolute;
    left: -0.5rem;
    top: 0.75rem;
    width: 0.5rem;
    height: 2px;
    background: oklch(var(--bc) / 0.1);
  }
</style>
