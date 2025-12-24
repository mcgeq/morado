<template>
  <div class="card bg-base-100 shadow-md hover:shadow-lg transition-shadow">
    <div class="card-body">
      <!-- Header -->
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <h3 class="card-title text-lg">
            {{ apiDefinition.name }}
            <span v-if="!apiDefinition.isActive" class="badge badge-ghost badge-sm">Inactive</span>
            <span class="badge badge-sm" :class="methodBadgeClass">{{ apiDefinition.method }}</span>
          </h3>
          <p v-if="apiDefinition.description" class="text-sm text-base-content/70 mt-1">
            {{ apiDefinition.description }}
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
              <a @click="$emit('edit', apiDefinition)">Edit</a>
            </li>
            <li>
              <a @click="$emit('duplicate', apiDefinition)">Duplicate</a>
            </li>
            <li>
              <a @click="$emit('test', apiDefinition)">Test API</a>
            </li>
            <li>
              <a @click="$emit('view', apiDefinition)">View Details</a>
            </li>
            <li class="divider"></li>
            <li>
              <a @click="$emit('delete', apiDefinition)" class="text-error">Delete</a>
            </li>
          </ul>
        </div>
      </div>

      <!-- Endpoint -->
      <div class="mt-4">
        <div class="text-xs font-semibold text-base-content/60 mb-2">Endpoint</div>
        <div class="flex items-center gap-2">
          <code class="text-xs bg-base-200 px-3 py-2 rounded flex-1 font-mono">{{ fullUrl }}</code>
        </div>
      </div>

      <!-- Components -->
      <div class="mt-3 grid grid-cols-2 gap-2">
        <!-- Header Reference -->
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
              d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
            />
          </svg>
          <span class="text-xs text-base-content/70">
            {{ apiDefinition.headerId ? 'Header: Referenced' : 'Header: Inline' }}
          </span>
        </div>

        <!-- Request Body -->
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
          <span class="text-xs text-base-content/70"> {{ requestBodyType }} </span>
        </div>

        <!-- Response Body -->
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
          <span class="text-xs text-base-content/70"> {{ responseBodyType }} </span>
        </div>

        <!-- Timeout -->
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
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <span class="text-xs text-base-content/70"> Timeout: {{ apiDefinition.timeout }}s </span>
        </div>
      </div>

      <!-- Parameters -->
      <div v-if="hasParameters" class="mt-3">
        <div class="text-xs font-semibold text-base-content/60 mb-2">Parameters</div>
        <div class="flex flex-wrap gap-1">
          <span v-if="queryParamCount > 0" class="badge badge-sm badge-outline">
            Query: {{ queryParamCount }}
          </span>
          <span v-if="pathParamCount > 0" class="badge badge-sm badge-outline">
            Path: {{ pathParamCount }}
          </span>
        </div>
      </div>

      <!-- Tags -->
      <div
        v-if="apiDefinition.tags && apiDefinition.tags.length > 0"
        class="mt-3 flex flex-wrap gap-1"
      >
        <span v-for="tag in apiDefinition.tags" :key="tag" class="badge badge-sm badge-outline">
          {{ tag }}
        </span>
      </div>

      <!-- Footer -->
      <div class="card-actions justify-between items-center mt-4 pt-3 border-t border-base-300">
        <div class="text-xs text-base-content/50">
          v{{ apiDefinition.version }}• {{ formatDate(apiDefinition.updatedAt) }}
        </div>
        <button type="button" class="btn btn-primary btn-sm" @click="$emit('use', apiDefinition)">
          Use API
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed } from 'vue';
  import type { ApiDefinition } from '@/api/api-definition';

  interface Props {
    apiDefinition: ApiDefinition;
  }

  const props = defineProps<Props>();

  defineEmits<{
    edit: [apiDefinition: ApiDefinition];
    duplicate: [apiDefinition: ApiDefinition];
    delete: [apiDefinition: ApiDefinition];
    view: [apiDefinition: ApiDefinition];
    test: [apiDefinition: ApiDefinition];
    use: [apiDefinition: ApiDefinition];
  }>();

  const methodBadgeClass = computed(() => {
    switch (props.apiDefinition.method) {
      case 'GET':
        return 'badge-info';
      case 'POST':
        return 'badge-success';
      case 'PUT':
        return 'badge-warning';
      case 'PATCH':
        return 'badge-warning';
      case 'DELETE':
        return 'badge-error';
      default:
        return 'badge-ghost';
    }
  });

  const fullUrl = computed(() => {
    const base = props.apiDefinition.baseUrl || '';
    const path = props.apiDefinition.path || '';
    return `${base}${path}`;
  });

  const requestBodyType = computed(() => {
    if (props.apiDefinition.requestBodyId) return 'Request: Referenced';
    if (props.apiDefinition.inlineRequestBody) return 'Request: Inline';
    return 'Request: None';
  });

  const responseBodyType = computed(() => {
    if (props.apiDefinition.responseBodyId) return 'Response: Referenced';
    if (props.apiDefinition.inlineResponseBody) return 'Response: Inline';
    return 'Response: None';
  });

  const queryParamCount = computed(() => {
    return props.apiDefinition.queryParameters
      ? Object.keys(props.apiDefinition.queryParameters).length
      : 0;
  });

  const pathParamCount = computed(() => {
    return props.apiDefinition.pathParameters
      ? Object.keys(props.apiDefinition.pathParameters).length
      : 0;
  });

  const hasParameters = computed(() => queryParamCount.value > 0 || pathParamCount.value > 0);

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
