<template>
  <div class="card bg-base-100 shadow-md hover:shadow-lg transition-shadow">
    <div class="card-body">
      <!-- Header -->
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <h3 class="card-title text-lg">
            {{ script.name }}
            <span v-if="!script.isActive" class="badge badge-ghost badge-sm">Inactive</span>
            <span class="badge badge-sm" :class="typeBadgeClass">{{ script.scriptType }}</span>
            <span v-if="script.debugMode" class="badge badge-sm badge-warning">Debug</span>
          </h3>
          <p v-if="script.description" class="text-sm text-base-content/70 mt-1">
            {{ script.description }}
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
              <a @click="$emit('edit', script)">Edit</a>
            </li>
            <li>
              <a @click="$emit('duplicate', script)">Duplicate</a>
            </li>
            <li>
              <a @click="$emit('execute', script)">Execute</a>
            </li>
            <li>
              <a @click="$emit('debug', script)">Debug</a>
            </li>
            <li>
              <a @click="$emit('view', script)">View Details</a>
            </li>
            <li class="divider"></li>
            <li>
              <a @click="$emit('delete', script)" class="text-error">Delete</a>
            </li>
          </ul>
        </div>
      </div>

      <!-- Script Info -->
      <div class="mt-4 grid grid-cols-2 gap-3">
        <!-- API Definition -->
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
              d="M13 10V3L4 14h7v7l9-11h-7z"
            />
          </svg>
          <span class="text-xs text-base-content/70"> API: #{{ script.apiDefinitionId }} </span>
        </div>

        <!-- Execution Order -->
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
              d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14"
            />
          </svg>
          <span class="text-xs text-base-content/70"> Order: {{ script.executionOrder }} </span>
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
          <span class="text-xs text-base-content/70"> Retry: {{ script.retryCount }}x </span>
        </div>

        <!-- Timeout -->
        <div v-if="script.timeoutOverride" class="flex items-center gap-2 text-sm">
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
          <span class="text-xs text-base-content/70"> Timeout: {{ script.timeoutOverride }}s </span>
        </div>
      </div>

      <!-- Features -->
      <div class="mt-3">
        <div class="flex flex-wrap gap-2">
          <span v-if="hasVariables" class="badge badge-sm badge-outline">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-3 w-3 mr-1"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
              />
            </svg>
            {{ variableCount }}Variables
          </span>
          <span v-if="hasAssertions" class="badge badge-sm badge-outline">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-3 w-3 mr-1"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            {{ assertionCount }}Assertions
          </span>
          <span v-if="hasPreScript" class="badge badge-sm badge-outline">Pre-Script</span>
          <span v-if="hasPostScript" class="badge badge-sm badge-outline">Post-Script</span>
          <span v-if="hasOutputVariables" class="badge badge-sm badge-outline">
            {{ outputVariableCount }}Outputs
          </span>
        </div>
      </div>

      <!-- Tags -->
      <div v-if="script.tags && script.tags.length > 0" class="mt-3 flex flex-wrap gap-1">
        <span v-for="tag in script.tags" :key="tag" class="badge badge-sm badge-outline">
          {{ tag }}
        </span>
      </div>

      <!-- Footer -->
      <div class="card-actions justify-between items-center mt-4 pt-3 border-t border-base-300">
        <div class="text-xs text-base-content/50">
          v{{ script.version }}• {{ formatDate(script.updatedAt) }}
        </div>
        <div class="flex gap-2">
          <button type="button" class="btn btn-sm btn-outline" @click="$emit('debug', script)">
            Debug
          </button>
          <button type="button" class="btn btn-primary btn-sm" @click="$emit('execute', script)">
            Execute
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed } from 'vue';
  import type { TestScript } from '@/api/script';

  interface Props {
    script: TestScript;
  }

  const props = defineProps<Props>();

  defineEmits<{
    edit: [script: TestScript];
    duplicate: [script: TestScript];
    delete: [script: TestScript];
    view: [script: TestScript];
    execute: [script: TestScript];
    debug: [script: TestScript];
  }>();

  const typeBadgeClass = computed(() => {
    switch (props.script.scriptType) {
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
  });

  const hasVariables = computed(() => {
    return props.script.variables && Object.keys(props.script.variables).length > 0;
  });

  const variableCount = computed(() => {
    return props.script.variables ? Object.keys(props.script.variables).length : 0;
  });

  const hasAssertions = computed(() => {
    return props.script.assertions && props.script.assertions.length > 0;
  });

  const assertionCount = computed(() => {
    return props.script.assertions ? props.script.assertions.length : 0;
  });

  const hasPreScript = computed(() => {
    return !!props.script.preScript;
  });

  const hasPostScript = computed(() => {
    return !!props.script.postScript;
  });

  const hasOutputVariables = computed(() => {
    return props.script.outputVariables && props.script.outputVariables.length > 0;
  });

  const outputVariableCount = computed(() => {
    return props.script.outputVariables ? props.script.outputVariables.length : 0;
  });

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
