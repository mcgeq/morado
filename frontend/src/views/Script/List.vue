<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-3xl font-bold">Test Scripts</h1>
      <button
        @click="navigateToCreate"
        class="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
      >
        Create Script
      </button>
    </div>

    <!-- Filters -->
    <div class="mb-6 flex gap-4">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search scripts..."
        class="flex-1 rounded-lg border px-4 py-2"
        @input="handleSearch"
      />
      <select
        v-model="selectedType"
        class="rounded-lg border px-4 py-2"
        @change="handleFilterChange"
      >
        <option value="">All Types</option>
        <option value="setup">Setup</option>
        <option value="main">Main</option>
        <option value="teardown">Teardown</option>
        <option value="utility">Utility</option>
      </select>
    </div>

    <!-- Loading State -->
    <div v-if="scriptStore.isLoading" class="text-center py-12">
      <p class="text-gray-500">Loading scripts...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="scriptStore.error" class="rounded-lg bg-red-50 p-4 text-red-700">
      {{ scriptStore.error }}
    </div>

    <!-- Empty State -->
    <div v-else-if="!scriptStore.hasScripts" class="text-center py-12">
      <p class="text-gray-500 mb-4">No scripts found</p>
      <button
        @click="navigateToCreate"
        class="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
      >
        Create Your First Script
      </button>
    </div>

    <!-- Scripts List -->
    <div v-else class="space-y-4">
      <div
        v-for="script in scriptStore.scripts"
        :key="script.id"
        class="rounded-lg border bg-white p-6 shadow-sm hover:shadow-md transition-shadow"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <h3 class="text-xl font-semibold mb-2">{{ script.name }}</h3>
            <p v-if="script.description" class="text-gray-600 mb-3">{{ script.description }}</p>
            <div class="flex gap-2 mb-3">
              <span class="rounded-full bg-purple-100 px-3 py-1 text-sm text-purple-700">
                {{ script.scriptType }}
              </span>
              <span
                v-if="script.debugMode"
                class="rounded-full bg-yellow-100 px-3 py-1 text-sm text-yellow-700"
              >
                Debug Mode
              </span>
              <span
                v-if="!script.isActive"
                class="rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-700"
              >
                Inactive
              </span>
              <span
                v-for="tag in script.tags"
                :key="tag"
                class="rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-700"
              >
                {{ tag }}
              </span>
            </div>
            <div class="text-sm text-gray-500">
              Order: {{ script.executionOrder }}
              <span v-if="script.assertions"> • {{ script.assertions.length }}assertion(s)</span>
              <span v-if="script.retryCount > 0"> • Retry: {{ script.retryCount }}</span>
            </div>
          </div>
          <div class="flex gap-2">
            <button
              @click="navigateToDebug(script.id)"
              class="rounded-lg bg-green-100 px-3 py-2 text-green-700 hover:bg-green-200"
            >
              Debug
            </button>
            <button
              @click="navigateToEdit(script.id)"
              class="rounded-lg bg-gray-100 px-3 py-2 text-gray-700 hover:bg-gray-200"
            >
              Edit
            </button>
            <button
              @click="handleDuplicate(script.id)"
              class="rounded-lg bg-gray-100 px-3 py-2 text-gray-700 hover:bg-gray-200"
            >
              Duplicate
            </button>
            <button
              @click="handleDelete(script.id)"
              class="rounded-lg bg-red-100 px-3 py-2 text-red-700 hover:bg-red-200"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="scriptStore.totalPages > 1" class="mt-6 flex justify-center gap-2">
      <button
        v-for="page in scriptStore.totalPages"
        :key="page"
        @click="handlePageChange(page)"
        :class="[
          'rounded-lg px-4 py-2',
          page === scriptStore.currentPage
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
  import type { ScriptType } from '@/api/script';
  import { useScriptStore } from '@/stores/script';

  const router = useRouter();
  const scriptStore = useScriptStore();

  const searchQuery = ref('');
  const selectedType = ref<ScriptType | ''>('');

  onMounted(async () => {
    await scriptStore.fetchScripts();
  });

  function navigateToCreate() {
    router.push('/scripts/new');
  }

  function navigateToEdit(id: number) {
    router.push(`/scripts/${id}/edit`);
  }

  function navigateToDebug(id: number) {
    router.push(`/scripts/${id}/debug`);
  }

  async function handleSearch() {
    if (searchQuery.value) {
      await scriptStore.searchScriptsByQuery(searchQuery.value);
    } else {
      await scriptStore.fetchScripts();
    }
  }

  async function handleFilterChange() {
    await scriptStore.fetchScripts({
      scriptType: selectedType.value || undefined,
    });
  }

  async function handlePageChange(page: number) {
    scriptStore.setPage(page);
    await scriptStore.fetchScripts();
  }

  async function handleDuplicate(id: number) {
    if (confirm('Duplicate this script?')) {
      try {
        await scriptStore.duplicateExistingScript(id);
      } catch (error) {
        console.error('Failed to duplicate script:', error);
      }
    }
  }

  async function handleDelete(id: number) {
    if (confirm('Are you sure you want to delete this script?')) {
      try {
        await scriptStore.deleteScriptById(id);
      } catch (error) {
        console.error('Failed to delete script:', error);
      }
    }
  }
</script>
