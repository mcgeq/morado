<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-3xl font-bold">Request/Response Bodies</h1>
      <button
        @click="navigateToCreate"
        class="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
      >
        Create Body
      </button>
    </div>

    <!-- Filters -->
    <div class="mb-6 flex gap-4">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search bodies..."
        class="flex-1 rounded-lg border px-4 py-2"
        @input="handleSearch"
      />
      <select
        v-model="selectedType"
        class="rounded-lg border px-4 py-2"
        @change="handleFilterChange"
      >
        <option value="">All Types</option>
        <option value="request">Request</option>
        <option value="response">Response</option>
        <option value="both">Both</option>
      </select>
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
    <div v-if="bodyStore.isLoading" class="text-center py-12">
      <p class="text-gray-500">Loading bodies...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="bodyStore.error" class="rounded-lg bg-red-50 p-4 text-red-700">
      {{ bodyStore.error }}
    </div>

    <!-- Empty State -->
    <div v-else-if="!bodyStore.hasBodies" class="text-center py-12">
      <p class="text-gray-500 mb-4">No bodies found</p>
      <button
        @click="navigateToCreate"
        class="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
      >
        Create Your First Body
      </button>
    </div>

    <!-- Bodies List -->
    <div v-else class="space-y-4">
      <div
        v-for="body in bodyStore.bodies"
        :key="body.id"
        class="rounded-lg border bg-white p-6 shadow-sm hover:shadow-md transition-shadow"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <h3 class="text-xl font-semibold mb-2">{{ body.name }}</h3>
            <p v-if="body.description" class="text-gray-600 mb-3">{{ body.description }}</p>
            <div class="flex gap-2 mb-3">
              <span class="rounded-full bg-purple-100 px-3 py-1 text-sm text-purple-700">
                {{ body.bodyType }}
              </span>
              <span class="rounded-full bg-blue-100 px-3 py-1 text-sm text-blue-700">
                {{ body.scope }}
              </span>
              <span class="rounded-full bg-green-100 px-3 py-1 text-sm text-green-700">
                {{ body.contentType }}
              </span>
              <span
                v-if="!body.isActive"
                class="rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-700"
              >
                Inactive
              </span>
              <span
                v-for="tag in body.tags"
                :key="tag"
                class="rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-700"
              >
                {{ tag }}
              </span>
            </div>
            <div class="text-sm text-gray-500">
              Version {{ body.version }}
              <span v-if="body.bodySchema"> • Has Schema</span>
              <span v-if="body.exampleData"> • Has Example</span>
            </div>
          </div>
          <div class="flex gap-2">
            <button
              @click="navigateToEdit(body.id)"
              class="rounded-lg bg-gray-100 px-3 py-2 text-gray-700 hover:bg-gray-200"
            >
              Edit
            </button>
            <button
              @click="handleDuplicate(body.id)"
              class="rounded-lg bg-gray-100 px-3 py-2 text-gray-700 hover:bg-gray-200"
            >
              Duplicate
            </button>
            <button
              @click="handleDelete(body.id)"
              class="rounded-lg bg-red-100 px-3 py-2 text-red-700 hover:bg-red-200"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="bodyStore.totalPages > 1" class="mt-6 flex justify-center gap-2">
      <button
        v-for="page in bodyStore.totalPages"
        :key="page"
        @click="handlePageChange(page)"
        :class="[
          'rounded-lg px-4 py-2',
          page === bodyStore.currentPage
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
  import type { BodyScope, BodyType } from '@/api/body';
  import { useBodyStore } from '@/stores/body';

  const router = useRouter();
  const bodyStore = useBodyStore();

  const searchQuery = ref('');
  const selectedType = ref<BodyType | ''>('');
  const selectedScope = ref<BodyScope | ''>('');

  onMounted(async () => {
    await bodyStore.fetchBodies();
  });

  function navigateToCreate() {
    router.push('/bodies/new');
  }

  function navigateToEdit(id: number) {
    router.push(`/bodies/${id}/edit`);
  }

  async function handleSearch() {
    if (searchQuery.value) {
      await bodyStore.searchBodiesByQuery(searchQuery.value);
    } else {
      await bodyStore.fetchBodies();
    }
  }

  async function handleFilterChange() {
    await bodyStore.fetchBodies({
      bodyType: selectedType.value || undefined,
      scope: selectedScope.value || undefined,
    });
  }

  async function handlePageChange(page: number) {
    bodyStore.setPage(page);
    await bodyStore.fetchBodies();
  }

  async function handleDuplicate(id: number) {
    if (confirm('Duplicate this body?')) {
      try {
        await bodyStore.duplicateExistingBody(id);
      } catch (error) {
        console.error('Failed to duplicate body:', error);
      }
    }
  }

  async function handleDelete(id: number) {
    if (confirm('Are you sure you want to delete this body?')) {
      try {
        await bodyStore.deleteBodyById(id);
      } catch (error) {
        console.error('Failed to delete body:', error);
      }
    }
  }
</script>
