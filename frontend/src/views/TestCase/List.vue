<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-3xl font-bold">Test Cases</h1>
      <button
        @click="navigateToCreate"
        class="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
      >
        Create Test Case
      </button>
    </div>

    <!-- Filters -->
    <div class="mb-6 flex gap-4">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search test cases..."
        class="flex-1 rounded-lg border px-4 py-2"
        @input="handleSearch"
      />
    </div>

    <!-- Loading State -->
    <div v-if="testCaseStore.isLoading" class="text-center py-12">
      <p class="text-gray-500">Loading test cases...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="testCaseStore.error" class="rounded-lg bg-red-50 p-4 text-red-700">
      {{ testCaseStore.error }}
    </div>

    <!-- Empty State -->
    <div v-else-if="!testCaseStore.hasTestCases" class="text-center py-12">
      <p class="text-gray-500 mb-4">No test cases found</p>
      <button
        @click="navigateToCreate"
        class="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
      >
        Create Your First Test Case
      </button>
    </div>

    <!-- Test Cases List -->
    <div v-else class="space-y-4">
      <div
        v-for="testCase in testCaseStore.testCases"
        :key="testCase.id"
        class="rounded-lg border bg-white p-6 shadow-sm hover:shadow-md transition-shadow"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <h3 class="text-xl font-semibold mb-2">{{ testCase.name }}</h3>
            <p v-if="testCase.description" class="text-gray-600 mb-3">{{ testCase.description }}</p>
            <div class="flex gap-2 mb-3">
              <span
                :class="[
                  'rounded-full px-3 py-1 text-sm',
                  testCase.status === 'active'
                    ? 'bg-green-100 text-green-700'
                    : testCase.status === 'draft'
                    ? 'bg-yellow-100 text-yellow-700'
                    : 'bg-gray-100 text-gray-700',
                ]"
              >
                {{ testCase.status }}
              </span>
              <span
                :class="[
                  'rounded-full px-3 py-1 text-sm',
                  testCase.priority === 'critical'
                    ? 'bg-red-100 text-red-700'
                    : testCase.priority === 'high'
                    ? 'bg-orange-100 text-orange-700'
                    : testCase.priority === 'medium'
                    ? 'bg-blue-100 text-blue-700'
                    : 'bg-gray-100 text-gray-700',
                ]"
              >
                {{ testCase.priority }}
              </span>
              <span
                v-for="tag in testCase.tags"
                :key="tag"
                class="rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-700"
              >
                {{ tag }}
              </span>
            </div>
          </div>
          <div class="flex gap-2">
            <button
              @click="navigateToDetail(testCase.id)"
              class="rounded-lg bg-blue-100 px-3 py-2 text-blue-700 hover:bg-blue-200"
            >
              View
            </button>
            <button
              @click="navigateToEdit(testCase.id)"
              class="rounded-lg bg-gray-100 px-3 py-2 text-gray-700 hover:bg-gray-200"
            >
              Edit
            </button>
            <button
              @click="handleDelete(testCase.id)"
              class="rounded-lg bg-red-100 px-3 py-2 text-red-700 hover:bg-red-200"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="testCaseStore.totalPages > 1" class="mt-6 flex justify-center gap-2">
      <button
        v-for="page in testCaseStore.totalPages"
        :key="page"
        @click="handlePageChange(page)"
        :class="[
          'rounded-lg px-4 py-2',
          page === testCaseStore.currentPage
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
  import { useTestCaseStore } from '@/stores/testCase';

  const router = useRouter();
  const testCaseStore = useTestCaseStore();

  const searchQuery = ref('');

  onMounted(async () => {
    await testCaseStore.fetchTestCases();
  });

  function navigateToCreate() {
    router.push('/test-cases/new');
  }

  function navigateToEdit(id: number) {
    router.push(`/test-cases/${id}/edit`);
  }

  function navigateToDetail(id: number) {
    router.push(`/test-cases/${id}`);
  }

  async function handleSearch() {
    if (searchQuery.value) {
      await testCaseStore.searchTestCasesByQuery(searchQuery.value);
    } else {
      await testCaseStore.fetchTestCases();
    }
  }

  async function handlePageChange(page: number) {
    testCaseStore.setPage(page);
    await testCaseStore.fetchTestCases();
  }

  async function handleDelete(id: number) {
    if (confirm('Are you sure you want to delete this test case?')) {
      try {
        await testCaseStore.deleteTestCaseById(id);
      } catch (error) {
        console.error('Failed to delete test case:', error);
      }
    }
  }
</script>
