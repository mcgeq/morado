<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-3xl font-bold">API Definitions</h1>
      <button
        @click="navigateToCreate"
        class="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
      >
        Create API Definition
      </button>
    </div>

    <!-- Filters -->
    <div class="mb-6 flex gap-4">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search API definitions..."
        class="flex-1 rounded-lg border px-4 py-2"
        @input="handleSearch"
      />
      <select
        v-model="selectedMethod"
        class="rounded-lg border px-4 py-2"
        @change="handleFilterChange"
      >
        <option value="">All Methods</option>
        <option value="GET">GET</option>
        <option value="POST">POST</option>
        <option value="PUT">PUT</option>
        <option value="PATCH">PATCH</option>
        <option value="DELETE">DELETE</option>
      </select>
    </div>

    <!-- Loading State -->
    <div v-if="apiDefinitionStore.isLoading" class="text-center py-12">
      <p class="text-gray-500">Loading API definitions...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="apiDefinitionStore.error" class="rounded-lg bg-red-50 p-4 text-red-700">
      {{ apiDefinitionStore.error }}
    </div>

    <!-- Empty State -->
    <div v-else-if="!apiDefinitionStore.hasApiDefinitions" class="text-center py-12">
      <p class="text-gray-500 mb-4">No API definitions found</p>
      <button
        @click="navigateToCreate"
        class="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
      >
        Create Your First API Definition
      </button>
    </div>

    <!-- API Definitions List -->
    <div v-else class="space-y-4">
      <div
        v-for="api in apiDefinitionStore.apiDefinitions"
        :key="api.id"
        class="rounded-lg border bg-white p-6 shadow-sm hover:shadow-md transition-shadow"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <span
                :class="[
                  'rounded px-2 py-1 text-sm font-semibold',
                  getMethodColor(api.method),
                ]"
              >
                {{ api.method }}
              </span>
              <h3 class="text-xl font-semibold">{{ api.name }}</h3>
            </div>
            <p class="text-gray-600 mb-2 font-mono text-sm">{{ api.url }}</p>
            <p v-if="api.description" class="text-gray-600 mb-3">{{ api.description }}</p>
            <div class="flex gap-2 mb-3">
              <span
                v-if="!api.isActive"
                class="rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-700"
              >
                Inactive
              </span>
              <span
                v-for="tag in api.tags"
                :key="tag"
                class="rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-700"
              >
                {{ tag }}
              </span>
            </div>
            <div class="text-sm text-gray-500">
              <span v-if="api.headerId">Header Component</span>
              <span v-if="api.requestBodyId"> • Request Body</span>
              <span v-if="api.responseBodyId"> • Response Body</span>
              <span v-if="api.inlineRequestBody"> • Inline Request</span>
              <span v-if="api.inlineResponseBody"> • Inline Response</span>
            </div>
          </div>
          <div class="flex gap-2">
            <button
              @click="navigateToEdit(api.id)"
              class="rounded-lg bg-gray-100 px-3 py-2 text-gray-700 hover:bg-gray-200"
            >
              Edit
            </button>
            <button
              @click="handleDuplicate(api.id)"
              class="rounded-lg bg-gray-100 px-3 py-2 text-gray-700 hover:bg-gray-200"
            >
              Duplicate
            </button>
            <button
              @click="handleDelete(api.id)"
              class="rounded-lg bg-red-100 px-3 py-2 text-red-700 hover:bg-red-200"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="apiDefinitionStore.totalPages > 1" class="mt-6 flex justify-center gap-2">
      <button
        v-for="page in apiDefinitionStore.totalPages"
        :key="page"
        @click="handlePageChange(page)"
        :class="[
          'rounded-lg px-4 py-2',
          page === apiDefinitionStore.currentPage
            ? 'bg-blue-600 text-white'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200',
        ]"
      >
        {{ page }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useApiDefinitionStore } from '@/stores/apiDefinition';
import type { HttpMethod } from '@/api/api-definition';

const router = useRouter();
const apiDefinitionStore = useApiDefinitionStore();

const searchQuery = ref('');
const selectedMethod = ref<HttpMethod | ''>('');

onMounted(async () => {
  await apiDefinitionStore.fetchApiDefinitions();
});

function getMethodColor(method: string): string {
  const colors: Record<string, string> = {
    GET: 'bg-green-100 text-green-700',
    POST: 'bg-blue-100 text-blue-700',
    PUT: 'bg-yellow-100 text-yellow-700',
    PATCH: 'bg-orange-100 text-orange-700',
    DELETE: 'bg-red-100 text-red-700',
  };
  return colors[method] || 'bg-gray-100 text-gray-700';
}

function navigateToCreate() {
  router.push('/api-definitions/new');
}

function navigateToEdit(id: number) {
  router.push(`/api-definitions/${id}/edit`);
}

async function handleSearch() {
  if (searchQuery.value) {
    await apiDefinitionStore.searchApiDefinitionsByQuery(searchQuery.value);
  } else {
    await apiDefinitionStore.fetchApiDefinitions();
  }
}

async function handleFilterChange() {
  await apiDefinitionStore.fetchApiDefinitions({
    method: selectedMethod.value || undefined,
  });
}

async function handlePageChange(page: number) {
  apiDefinitionStore.setPage(page);
  await apiDefinitionStore.fetchApiDefinitions();
}

async function handleDuplicate(id: number) {
  if (confirm('Duplicate this API definition?')) {
    try {
      await apiDefinitionStore.duplicateExistingApiDefinition(id);
    } catch (error) {
      console.error('Failed to duplicate API definition:', error);
    }
  }
}

async function handleDelete(id: number) {
  if (confirm('Are you sure you want to delete this API definition?')) {
    try {
      await apiDefinitionStore.deleteApiDefinitionById(id);
    } catch (error) {
      console.error('Failed to delete API definition:', error);
    }
  }
}
</script>
