<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-6">
      <button @click="goBack" class="mb-4 text-blue-600 hover:text-blue-700">
        ← Back to Test Cases
      </button>
      <h1 class="text-3xl font-bold">
        {{ isEditMode ? 'Edit Test Case' : 'Create Test Case' }}
      </h1>
    </div>

    <form @submit.prevent="handleSubmit" class="max-w-3xl space-y-6">
      <div>
        <label class="block text-sm font-medium mb-2">Name *</label>
        <input
          v-model="formData.name"
          type="text"
          required
          class="w-full rounded-lg border px-4 py-2"
          placeholder="e.g., User Login Test"
        />
      </div>

      <div>
        <label class="block text-sm font-medium mb-2">Description</label>
        <textarea
          v-model="formData.description"
          rows="3"
          class="w-full rounded-lg border px-4 py-2"
          placeholder="Describe this test case..."
        />
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium mb-2">Priority</label>
          <select v-model="formData.priority" class="w-full rounded-lg border px-4 py-2">
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">Status</label>
          <select v-model="formData.status" class="w-full rounded-lg border px-4 py-2">
            <option value="draft">Draft</option>
            <option value="active">Active</option>
            <option value="deprecated">Deprecated</option>
            <option value="archived">Archived</option>
          </select>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium mb-2">Test Data (JSON)</label>
        <textarea
          v-model="testDataInput"
          rows="10"
          class="w-full rounded-lg border px-4 py-2 font-mono text-sm"
          placeholder='{"key": "value"}'
          @blur="updateTestData"
        />
      </div>

      <div>
        <label class="block text-sm font-medium mb-2">Tags</label>
        <input
          v-model="tagsInput"
          type="text"
          class="w-full rounded-lg border px-4 py-2"
          placeholder="Enter tags separated by commas"
          @blur="updateTags"
        />
      </div>

      <div class="flex gap-4">
        <button
          type="submit"
          :disabled="testCaseStore.isSaving"
          class="rounded-lg bg-blue-600 px-6 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {{ testCaseStore.isSaving ? 'Saving...' : isEditMode ? 'Update' : 'Create' }}
        </button>
        <button
          type="button"
          @click="goBack"
          class="rounded-lg bg-gray-100 px-6 py-2 text-gray-700 hover:bg-gray-200"
        >
          Cancel
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useTestCaseStore } from '@/stores/testCase';
import type { TestCaseCreate, TestCasePriority, TestCaseStatus } from '@/api/test-case';

const route = useRoute();
const router = useRouter();
const testCaseStore = useTestCaseStore();

const isEditMode = computed(() => route.params.id !== 'new');
const testCaseId = computed(() => (isEditMode.value ? Number(route.params.id) : null));

const formData = ref<TestCaseCreate>({
  name: '',
  description: '',
  status: 'draft' as TestCaseStatus,
  priority: 'medium' as TestCasePriority,
  tags: [],
});

const testDataInput = ref('');
const tagsInput = ref('');

onMounted(async () => {
  if (isEditMode.value && testCaseId.value) {
    try {
      const testCase = await testCaseStore.fetchTestCaseById(testCaseId.value);
      formData.value = {
        name: testCase.name,
        description: testCase.description,
        testData: testCase.testData,
        status: testCase.status,
        priority: testCase.priority,
        tags: testCase.tags || [],
      };
      testDataInput.value = testCase.testData ? JSON.stringify(testCase.testData, null, 2) : '';
      tagsInput.value = (testCase.tags || []).join(', ');
    } catch (error) {
      console.error('Failed to load test case:', error);
    }
  }
});

function updateTestData() {
  try {
    if (testDataInput.value.trim()) {
      formData.value.testData = JSON.parse(testDataInput.value);
    } else {
      formData.value.testData = undefined;
    }
  } catch (error) {
    console.error('Invalid JSON for test data:', error);
  }
}

function updateTags() {
  formData.value.tags = tagsInput.value
    .split(',')
    .map(tag => tag.trim())
    .filter(tag => tag.length > 0);
}

async function handleSubmit() {
  try {
    updateTestData();
    updateTags();

    if (isEditMode.value && testCaseId.value) {
      await testCaseStore.updateExistingTestCase(testCaseId.value, formData.value);
    } else {
      await testCaseStore.createNewTestCase(formData.value);
    }

    router.push('/test-cases');
  } catch (error) {
    console.error('Failed to save test case:', error);
  }
}

function goBack() {
  router.push('/test-cases');
}
</script>
