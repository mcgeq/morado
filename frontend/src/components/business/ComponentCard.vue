<template>
  <div class="card bg-base-100 shadow-md hover:shadow-lg transition-shadow">
    <div class="card-body">
      <!-- Header -->
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <h3 class="card-title text-lg">
            {{ component.name }}
            <span v-if="!component.isActive" class="badge badge-ghost badge-sm">Inactive</span>
            <span class="badge badge-sm" :class="typeBadgeClass"
              >{{ component.componentType }}</span
            >
            <span class="badge badge-sm" :class="modeBadgeClass"
              >{{ component.executionMode }}</span
            >
          </h3>
          <p v-if="component.description" class="text-sm text-base-content/70 mt-1">
            {{ component.description }}
          </p>
        </div>

        <div class="dropdown dropdown-end">
          <button type="button" tabindex="0" class="btn btn-ghost btn-sm btn-circle">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              class="w-5 h-5 stroke-current"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"
              />
            </svg>
          </button>
          <ul
            tabindex="0"
            class="dropdown-content menu p-2 shadow bg-base-100 rounded-box w-52 z-10"
          >
            <li>
              <a @click="$emit('edit', component)">Edit</a>
            </li>
            <li>
              <a @click="$emit('duplicate', component)">Duplicate</a>
            </li>
            <li>
              <a @click="$emit('execute', component)">Execute</a>
            </li>
            <li>
              <a @click="$emit('viewHierarchy', component)">View Hierarchy</a>
            </li>
            <li>
              <a @click="$emit('view', component)">View Details</a>
            </li>
            <li class="divider"></li>
            <li>
              <a @click="$emit('delete', component)" class="text-error">Delete</a>
            </li>
          </ul>
        </div>
      </div>

      <!-- Component Stats -->
      <div class="mt-4 grid grid-cols-2 gap-3">
        <!-- Script Count -->
        <div class="flex items-center gap-2 text-sm">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-4 w-4 text-base-content/50"
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
          <span class="text-xs text-base-content/70">
            {{ component.scriptCount || 0 }}Scripts
          </span>
        </div>

        <!-- Parent Component -->
        <div v-if="component.parentComponentId" class="flex items-center gap-2 text-sm">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-4 w-4 text-base-content/50"
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
          <span class="text-xs text-base-content/70"> Nested Component </span>
        </div>

        <!-- Timeout -->
        <div v-if="component.timeoutOverride" class="flex items-center gap-2 text-sm">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-4 w-4 text-base-content/50"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <span class="text-xs text-base-content/70">
            Timeout: {{ component.timeoutOverride }}s
          </span>
        </div>

        <!-- Retry -->
        <div class="flex items-center gap-2 text-sm">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-4 w-4 text-base-content/50"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
          <span class="text-xs text-base-content/70"> Retry: {{ component.retryCount }}x </span>
        </div>
      </div>

      <!-- Shared Variables -->
      <div v-if="hasSharedVariables" class="mt-3">
        <div class="text-xs font-semibold text-base-content/60 mb-2">Shared Variables</div>
        <div class="flex flex-wrap gap-1">
          <span
            v-for="(_, key) in previewVariables"
            :key="key"
            class="badge badge-sm badge-outline"
          >
            {{ key }}
          </span>
          <span v-if="hasMoreVariables" class="badge badge-sm badge-ghost">
            +{{ remainingVariableCount }}more
          </span>
        </div>
      </div>

      <!-- Tags -->
      <div v-if="component.tags && component.tags.length > 0" class="mt-3 flex flex-wrap gap-1">
        <span v-for="tag in component.tags" :key="tag" class="badge badge-sm badge-outline">
          {{ tag }}
        </span>
      </div>

      <!-- Footer -->
      <div class="card-actions justify-between items-center mt-4 pt-3 border-t border-base-300">
        <div class="text-xs text-base-content/50">
          v{{ component.version }}• {{ formatDate(component.updatedAt) }}
        </div>
        <div class="flex gap-2">
          <button
            v-if="component.parentComponentId"
            type="button"
            class="btn btn-sm btn-outline"
            @click="$emit('viewHierarchy', component)"
          >
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
          </button>
          <button type="button" class="btn btn-primary btn-sm" @click="$emit('execute', component)">
            Execute
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed } from 'vue';
  import type { TestComponent } from '@/api/component';

  interface Props {
    component: TestComponent;
    maxPreviewVariables?: number;
  }

  const props = withDefaults(defineProps<Props>(), {
    maxPreviewVariables: 5,
  });

  defineEmits<{
    edit: [component: TestComponent];
    duplicate: [component: TestComponent];
    delete: [component: TestComponent];
    view: [component: TestComponent];
    execute: [component: TestComponent];
    viewHierarchy: [component: TestComponent];
  }>();

  const typeBadgeClass = computed(() => {
    switch (props.component.componentType) {
      case 'simple':
        return 'badge-info';
      case 'composite':
        return 'badge-primary';
      case 'template':
        return 'badge-secondary';
      default:
        return 'badge-ghost';
    }
  });

  const modeBadgeClass = computed(() => {
    switch (props.component.executionMode) {
      case 'sequential':
        return 'badge-success';
      case 'parallel':
        return 'badge-warning';
      case 'conditional':
        return 'badge-accent';
      default:
        return 'badge-ghost';
    }
  });

  const hasSharedVariables = computed(() => {
    return (
      props.component.sharedVariables && Object.keys(props.component.sharedVariables).length > 0
    );
  });

  const variableCount = computed(() => {
    return props.component.sharedVariables
      ? Object.keys(props.component.sharedVariables).length
      : 0;
  });

  const previewVariables = computed(() => {
    if (!props.component.sharedVariables) return {};
    const entries = Object.entries(props.component.sharedVariables);
    return Object.fromEntries(entries.slice(0, props.maxPreviewVariables));
  });

  const hasMoreVariables = computed(() => variableCount.value > props.maxPreviewVariables);

  const remainingVariableCount = computed(() => variableCount.value - props.maxPreviewVariables);

  function formatDate(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
    return date.toLocaleDateString();
  }
</script>
