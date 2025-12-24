<template>
  <div class="card bg-base-100 shadow-md hover:shadow-lg transition-shadow">
    <div class="card-body">
      <!-- Header -->
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <h3 class="card-title text-lg">
            {{ testCase.name }}
            <span class="badge badge-sm" :class="statusBadgeClass">{{ testCase.status }}</span>
            <span class="badge badge-sm" :class="priorityBadgeClass">{{ testCase.priority }}</span>
            <span v-if="testCase.isAutomated" class="badge badge-sm badge-accent">Automated</span>
          </h3>
          <p v-if="testCase.description" class="text-sm text-base-content/70 mt-1">
            {{ testCase.description }}
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
              <a @click="$emit('edit', testCase)">Edit</a>
            </li>
            <li>
              <a @click="$emit('duplicate', testCase)">Duplicate</a>
            </li>
            <li>
              <a @click="$emit('execute', testCase)">Execute</a>
            </li>
            <li>
              <a @click="$emit('viewHistory', testCase)">View History</a>
            </li>
            <li>
              <a @click="$emit('view', testCase)">View Details</a>
            </li>
            <li class="divider"></li>
            <li>
              <a @click="$emit('delete', testCase)" class="text-error">Delete</a>
            </li>
          </ul>
        </div>
      </div>

      <!-- Category -->
      <div v-if="testCase.category" class="mt-3">
        <div class="flex items-center gap-2">
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
              d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
            />
          </svg>
          <span class="text-sm text-base-content/70">{{ testCase.category }}</span>
        </div>
      </div>

      <!-- Test Case Stats -->
      <div class="mt-4 grid grid-cols-2 gap-3">
        <!-- Scripts -->
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
          <span class="text-xs text-base-content/70"> {{ testCase.scriptCount || 0 }}Scripts </span>
        </div>

        <!-- Components -->
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
              d="M4 6a2 2 0 012-2h2a2 2 0 012 6v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"
            />
          </svg>
          <span class="text-xs text-base-content/70">
            {{ testCase.componentCount || 0 }}Components
          </span>
        </div>

        <!-- Timeout -->
        <div v-if="testCase.timeoutOverride" class="flex items-center gap-2 text-sm">
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
            Timeout: {{ testCase.timeoutOverride }}s
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
          <span class="text-xs text-base-content/70"> Retry: {{ testCase.retryCount }}x </span>
        </div>
      </div>

      <!-- Test Data Preview -->
      <div v-if="hasTestData" class="mt-3">
        <div class="text-xs font-semibold text-base-content/60 mb-2">Test Data</div>
        <div class="flex flex-wrap gap-1">
          <span v-for="(_, key) in previewTestData" :key="key" class="badge badge-sm badge-outline">
            {{ key }}
          </span>
          <span v-if="hasMoreTestData" class="badge badge-sm badge-ghost">
            +{{ remainingTestDataCount }}more
          </span>
        </div>
      </div>

      <!-- Last Execution -->
      <div v-if="testCase.lastExecutionAt" class="mt-3">
        <div class="flex items-center justify-between text-xs">
          <span class="text-base-content/60">Last Execution:</span>
          <div class="flex items-center gap-2">
            <span
              v-if="testCase.lastExecutionStatus"
              class="badge badge-xs"
              :class="getExecutionStatusBadge(testCase.lastExecutionStatus)"
            >
              {{ testCase.lastExecutionStatus }}
            </span>
            <span class="text-base-content/70">{{ formatDate(testCase.lastExecutionAt) }}</span>
          </div>
        </div>
      </div>

      <!-- Tags -->
      <div v-if="testCase.tags && testCase.tags.length > 0" class="mt-3 flex flex-wrap gap-1">
        <span v-for="tag in testCase.tags" :key="tag" class="badge badge-sm badge-outline">
          {{ tag }}
        </span>
      </div>

      <!-- Footer -->
      <div class="card-actions justify-between items-center mt-4 pt-3 border-t border-base-300">
        <div class="text-xs text-base-content/50">
          v{{ testCase.version }}• {{ formatDate(testCase.updatedAt) }}
        </div>
        <button type="button" class="btn btn-primary btn-sm" @click="$emit('execute', testCase)">
          Execute
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed } from 'vue';
  import type { TestCase } from '@/api/test-case';

  interface Props {
    testCase: TestCase;
    maxPreviewData?: number;
  }

  const props = withDefaults(defineProps<Props>(), {
    maxPreviewData: 5,
  });

  defineEmits<{
    edit: [testCase: TestCase];
    duplicate: [testCase: TestCase];
    delete: [testCase: TestCase];
    view: [testCase: TestCase];
    execute: [testCase: TestCase];
    viewHistory: [testCase: TestCase];
  }>();

  const statusBadgeClass = computed(() => {
    switch (props.testCase.status) {
      case 'draft':
        return 'badge-ghost';
      case 'active':
        return 'badge-success';
      case 'deprecated':
        return 'badge-warning';
      case 'archived':
        return 'badge-error';
      default:
        return 'badge-ghost';
    }
  });

  const priorityBadgeClass = computed(() => {
    switch (props.testCase.priority) {
      case 'low':
        return 'badge-info';
      case 'medium':
        return 'badge-primary';
      case 'high':
        return 'badge-warning';
      case 'critical':
        return 'badge-error';
      default:
        return 'badge-ghost';
    }
  });

  const hasTestData = computed(() => {
    return props.testCase.testData && Object.keys(props.testCase.testData).length > 0;
  });

  const testDataCount = computed(() => {
    return props.testCase.testData ? Object.keys(props.testCase.testData).length : 0;
  });

  const previewTestData = computed(() => {
    if (!props.testCase.testData) return {};
    const entries = Object.entries(props.testCase.testData);
    return Object.fromEntries(entries.slice(0, props.maxPreviewData));
  });

  const hasMoreTestData = computed(() => testDataCount.value > props.maxPreviewData);

  const remainingTestDataCount = computed(() => testDataCount.value - props.maxPreviewData);

  function getExecutionStatusBadge(status: string): string {
    switch (status) {
      case 'passed':
        return 'badge-success';
      case 'failed':
        return 'badge-error';
      case 'skipped':
        return 'badge-warning';
      default:
        return 'badge-ghost';
    }
  }

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
