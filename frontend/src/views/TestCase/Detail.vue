<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-6">
      <button @click="goBack" class="mb-4 text-blue-600 hover:text-blue-700">
        ← Back to Test Cases
      </button>
      <h1 class="text-3xl font-bold">{{ testCase?.name }}</h1>
    </div>

    <!-- Loading State -->
    <div v-if="testCaseStore.isLoading" class="text-center py-12">
      <p class="text-gray-500">Loading test case...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="testCaseStore.error" class="rounded-lg bg-red-50 p-4 text-red-700 mb-6">
      {{ testCaseStore.error }}
    </div>

    <!-- Test Case Details -->
    <div v-else-if="testCase" class="space-y-6">
      <!-- Basic Info -->
      <div class="rounded-lg border bg-white p-6">
        <h2 class="text-xl font-semibold mb-4">Basic Information</h2>
        <div class="space-y-3">
          <div>
            <span class="font-medium">Name:</span>
            <span class="ml-2">{{ testCase.name }}</span>
          </div>
          <div v-if="testCase.description">
            <span class="font-medium">Description:</span>
            <p class="mt-1 text-gray-600">{{ testCase.description }}</p>
          </div>
          <div>
            <span class="font-medium">Status:</span>
            <span
              :class="[
                'ml-2 rounded-full px-3 py-1 text-sm',
                testCase.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700',
              ]"
            >
              {{ testCase.status }}
            </span>
          </div>
          <div v-if="testCase.tags && testCase.tags.length > 0">
            <span class="font-medium">Tags:</span>
            <div class="mt-2 flex gap-2">
              <span
                v-for="tag in testCase.tags"
                :key="tag"
                class="rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-700"
              >
                {{ tag }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Test Data -->
      <div v-if="testCase.testData" class="rounded-lg border bg-white p-6">
        <h2 class="text-xl font-semibold mb-4">Test Data</h2>
        <pre
          class="rounded-lg bg-gray-50 p-4 text-sm overflow-auto"
        >{{ JSON.stringify(testCase.testData, null, 2) }}</pre>
      </div>

      <!-- Actions -->
      <div class="flex gap-4">
        <button
          @click="navigateToEdit"
          class="rounded-lg bg-blue-600 px-6 py-2 text-white hover:bg-blue-700"
        >
          Edit Test Case
        </button>
        <button
          @click="handleExecute"
          :disabled="testCaseStore.isExecuting"
          class="rounded-lg bg-green-600 px-6 py-2 text-white hover:bg-green-700 disabled:opacity-50"
        >
          {{ testCaseStore.isExecuting ? 'Executing...' : 'Execute Test Case' }}
        </button>
      </div>

      <!-- Execution Result -->
      <div v-if="testCaseStore.executionResult" class="rounded-lg border bg-white p-6">
        <h2 class="text-xl font-semibold mb-4">Last Execution Result</h2>
        <pre
          class="rounded-lg bg-gray-50 p-4 text-sm overflow-auto max-h-96"
        >{{ JSON.stringify(testCaseStore.executionResult, null, 2) }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, onMounted } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import { useTestCaseStore } from '@/stores/testCase';

  const route = useRoute();
  const router = useRouter();
  const testCaseStore = useTestCaseStore();

  const testCaseId = computed(() => Number(route.params.id));
  const testCase = computed(() => testCaseStore.currentTestCase);

  onMounted(async () => {
    if (testCaseId.value) {
      await testCaseStore.fetchTestCaseById(testCaseId.value);
    }
  });

  function navigateToEdit() {
    router.push(`/test-cases/${testCaseId.value}/edit`);
  }

  async function handleExecute() {
    try {
      await testCaseStore.executeTestCaseById(testCaseId.value);
    } catch (error) {
      console.error('Failed to execute test case:', error);
    }
  }

  function goBack() {
    router.push('/test-cases');
  }
</script>
