<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-3xl font-bold">Test Components</h1>
      <button
        @click="navigateToCreate"
        class="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
      >
        Create Component
      </button>
    </div>

    <!-- Filters -->
    <div class="mb-6 flex gap-4">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search components..."
        class="flex-1 rounded-lg border px-4 py-2"
        @input="handleSearch"
      />
      <select
        v-model="selectedType"
        class="rounded-lg border px-4 py-2"
        @change="handleFilterChange"
      >
        <option value="">All Types</option>
        <option value="simple">Simple</option>
        <option value="composite">Composite</option>
        <option value="template">Template</option>
      </select>
    </div>

    <!-- Loading State -->
    <div v-if="componentStore.isLoading" class="text-center py-12">
      <p class="text-gray-500">Loading components...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="componentStore.error" class="rounded-lg bg-red-50 p-4 text-red-700">
      {{ componentStore.error }}
    </div>

    <!-- Empty State -->
    <div v-else-if="!componentStore.hasComponents" class="text-center py-12">
      <p class="text-gray-500 mb-4">No components found</p>
      <button
        @click="navigateToCreate"
        class="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
      >
        Create Your First Component
      </button>
    </div>

    <!-- Components List -->
    <div v-else class="space-y-4">
      <div
        v-for="component in componentStore.components"
        :key="component.id"
        class="rounded-lg border bg-white p-6 shadow-sm hover:shadow-md transition-shadow"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <h3 class="text-xl font-semibold mb-2">{{ component.name }}</h3>
            <p v-if="component.description" class="text-gray-600 mb-3">
              {{ component.description }}
            </p>
            <div class="flex gap-2 mb-3">
              <span class="rounded-full bg-indigo-100 px-3 py-1 text-sm text-indigo-700">
                {{ component.componentType }}
              </span>
              <span class="rounded-full bg-blue-100 px-3 py-1 text-sm text-blue-700">
                {{ component.executionMode }}
              </span>
              <span
                v-if="component.parentComponentId"
                class="rounded-full bg-purple-100 px-3 py-1 text-sm text-purple-700"
              >
                Nested
              </span>
              <span
                v-if="!component.isActive"
                class="rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-700"
              >
                Inactive
              </span>
              <span
                v-for="tag in component.tags"
                :key="tag"
                class="rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-700"
              >
                {{ tag }}
              </span>
            </div>
            <div class="text-sm text-gray-500">
              Version {{ component.version }}
              <span v-if="component.parentComponentId"> • Child Component</span>
            </div>
          </div>
          <div class="flex gap-2">
            <button
              @click="navigateToDebug(component.id)"
              class="rounded-lg bg-green-100 px-3 py-2 text-green-700 hover:bg-green-200"
            >
              Execute
            </button>
            <button
              @click="navigateToEdit(component.id)"
              class="rounded-lg bg-gray-100 px-3 py-2 text-gray-700 hover:bg-gray-200"
            >
              Edit
            </button>
            <button
              @click="handleDuplicate(component.id)"
              class="rounded-lg bg-gray-100 px-3 py-2 text-gray-700 hover:bg-gray-200"
            >
              Duplicate
            </button>
            <button
              @click="handleDelete(component.id)"
              class="rounded-lg bg-red-100 px-3 py-2 text-red-700 hover:bg-red-200"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="componentStore.totalPages > 1" class="mt-6 flex justify-center gap-2">
      <button
        v-for="page in componentStore.totalPages"
        :key="page"
        @click="handlePageChange(page)"
        :class="[
          'rounded-lg px-4 py-2',
          page === componentStore.currentPage
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
  import type { ComponentType } from '@/api/component';
  import { useComponentStore } from '@/stores/component';

  const router = useRouter();
  const componentStore = useComponentStore();

  const searchQuery = ref('');
  const selectedType = ref<ComponentType | ''>('');

  onMounted(async () => {
    await componentStore.fetchComponents();
  });

  function navigateToCreate() {
    router.push('/components/new');
  }

  function navigateToEdit(id: number) {
    router.push(`/components/${id}/edit`);
  }

  function navigateToDebug(id: number) {
    router.push(`/components/${id}/debug`);
  }

  async function handleSearch() {
    if (searchQuery.value) {
      await componentStore.searchComponentsByQuery(searchQuery.value);
    } else {
      await componentStore.fetchComponents();
    }
  }

  async function handleFilterChange() {
    await componentStore.fetchComponents({
      componentType: selectedType.value || undefined,
    });
  }

  async function handlePageChange(page: number) {
    componentStore.setPage(page);
    await componentStore.fetchComponents();
  }

  async function handleDuplicate(id: number) {
    if (confirm('Duplicate this component?')) {
      try {
        await componentStore.duplicateExistingComponent(id);
      } catch (error) {
        console.error('Failed to duplicate component:', error);
      }
    }
  }

  async function handleDelete(id: number) {
    if (confirm('Are you sure you want to delete this component?')) {
      try {
        await componentStore.deleteComponentById(id);
      } catch (error) {
        console.error('Failed to delete component:', error);
      }
    }
  }
</script>
