<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-3xl font-bold">Test Suites</h1>
      <button
        @click="navigateToCreate"
        class="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
      >
        Create Test Suite
      </button>
    </div>

    <!-- Search -->
    <div class="mb-6">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search test suites..."
        class="w-full rounded-lg border px-4 py-2"
        @input="handleSearch"
      />
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-12">
      <p class="text-gray-500">Loading test suites...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="testSuites.length === 0" class="text-center py-12">
      <p class="text-gray-500 mb-4">No test suites found</p>
      <button
        @click="navigateToCreate"
        class="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
      >
        Create Your First Test Suite
      </button>
    </div>

    <!-- Test Suites List -->
    <div v-else class="space-y-4">
      <div
        v-for="suite in testSuites"
        :key="suite.id"
        class="rounded-lg border bg-white p-6 shadow-sm hover:shadow-md transition-shadow"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <h3 class="text-xl font-semibold mb-2">{{ suite.name }}</h3>
            <p v-if="suite.description" class="text-gray-600 mb-3">{{ suite.description }}</p>
            <div class="text-sm text-gray-500">
              Created: {{ new Date(suite.createdAt).toLocaleDateString() }}
            </div>
          </div>
          <div class="flex gap-2">
            <button
              @click="handleExecute(suite.id)"
              class="rounded-lg bg-green-100 px-3 py-2 text-green-700 hover:bg-green-200"
            >
              Execute
            </button>
            <button
              @click="handleDelete(suite.id)"
              class="rounded-lg bg-red-100 px-3 py-2 text-red-700 hover:bg-red-200"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { onMounted, ref } from 'vue';
  import { useRouter } from 'vue-router';

  const router = useRouter();

  const searchQuery = ref('');
  const isLoading = ref(false);
  const testSuites = ref<any[]>([]);

  onMounted(async () => {
    // Placeholder - would fetch from API
    isLoading.value = false;
  });

  function navigateToCreate() {
    router.push('/test-suites/new');
  }

  function handleSearch() {
    // Placeholder for search functionality
  }

  function handleExecute(id: number) {
    console.log('Execute test suite:', id);
  }

  function handleDelete(id: number) {
    if (confirm('Are you sure you want to delete this test suite?')) {
      console.log('Delete test suite:', id);
    }
  }
</script>
