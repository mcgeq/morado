<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-3xl font-bold">HTTP Headers</h1>
      <button
        @click="navigateToCreate"
        class="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
      >
        Create Header
      </button>
    </div>

    <!-- Filters -->
    <div class="mb-6 flex gap-4">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search headers..."
        class="flex-1 rounded-lg border px-4 py-2"
        @input="handleSearch"
      />
      <select
        v-model="selectedScope"
        class="rounded-lg border px-4 py-2"
        @change="handleFilterChange"
      >
        <option value="">All Scopes</option>
        <option value="global">Global</option>
        <option value="project">Project</option>
        <option value="private">Private</option>
      </select>
    </div>

    <!-- Loading State -->
    <div v-if="headerStore.isLoading" class="text-center py-12">
      <p class="text-gray-500">Loading headers...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="headerStore.error" class="rounded-lg bg-red-50 p-4 text-red-700">
      {{ headerStore.error }}
    </div>

    <!-- Empty State -->
    <div v-else-if="!headerStore.hasHeaders" class="text-center py-12">
      <p class="text-gray-500 mb-4">No headers found</p>
      <button
        @click="navigateToCreate"
        class="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
      >
        Create Your First Header
      </button>
    </div>

    <!-- Headers List -->
    <div v-else class="space-y-4">
      <div
        v-for="header in headerStore.headers"
        :key="header.id"
        class="rounded-lg border bg-white p-6 shadow-sm hover:shadow-md transition-shadow"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <h3 class="text-xl font-semibold mb-2">{{ header.name }}</h3>
            <p v-if="header.description" class="text-gray-600 mb-3">{{ header.description }}</p>
            <div class="flex gap-2 mb-3">
              <span class="rounded-full bg-blue-100 px-3 py-1 text-sm text-blue-700">
                {{ header.scope }}
              </span>
              <span
                v-if="!header.isActive"
                class="rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-700"
              >
                Inactive
              </span>
              <span
                v-for="tag in header.tags"
                :key="tag"
                class="rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-700"
              >
                {{ tag }}
              </span>
            </div>
            <div class="text-sm text-gray-500">
              {{ Object.keys(header.headers).length }}header(s) • Version {{ header.version }}
            </div>
          </div>
          <div class="flex gap-2">
            <button
              @click="navigateToEdit(header.id)"
              class="rounded-lg bg-gray-100 px-3 py-2 text-gray-700 hover:bg-gray-200"
            >
              Edit
            </button>
            <button
              @click="handleDuplicate(header.id)"
              class="rounded-lg bg-gray-100 px-3 py-2 text-gray-700 hover:bg-gray-200"
            >
              Duplicate
            </button>
            <button
              @click="handleDelete(header.id)"
              class="rounded-lg bg-red-100 px-3 py-2 text-red-700 hover:bg-red-200"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="headerStore.totalPages > 1" class="mt-6 flex justify-center gap-2">
      <button
        v-for="page in headerStore.totalPages"
        :key="page"
        @click="handlePageChange(page)"
        :class="[
          'rounded-lg px-4 py-2',
          page === headerStore.currentPage
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
  import type { HeaderScope } from '@/api/header';
  import { useHeaderStore } from '@/stores/header';

  const router = useRouter();
  const headerStore = useHeaderStore();

  const searchQuery = ref('');
  const selectedScope = ref<HeaderScope | ''>('');

  onMounted(async () => {
    await headerStore.fetchHeaders();
  });

  function navigateToCreate() {
    router.push('/headers/new');
  }

  function navigateToEdit(id: number) {
    router.push(`/headers/${id}/edit`);
  }

  async function handleSearch() {
    if (searchQuery.value) {
      await headerStore.searchHeadersByQuery(searchQuery.value);
    } else {
      await headerStore.fetchHeaders();
    }
  }

  async function handleFilterChange() {
    await headerStore.fetchHeaders({
      scope: selectedScope.value || undefined,
    });
  }

  async function handlePageChange(page: number) {
    headerStore.setPage(page);
    await headerStore.fetchHeaders();
  }

  async function handleDuplicate(id: number) {
    if (confirm('Duplicate this header?')) {
      try {
        await headerStore.duplicateExistingHeader(id);
      } catch (error) {
        console.error('Failed to duplicate header:', error);
      }
    }
  }

  async function handleDelete(id: number) {
    if (confirm('Are you sure you want to delete this header?')) {
      try {
        await headerStore.deleteHeaderById(id);
      } catch (error) {
        console.error('Failed to delete header:', error);
      }
    }
  }
</script>
