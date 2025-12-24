<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-6">
      <button @click="goBack" class="mb-4 text-blue-600 hover:text-blue-700">
        ← Back to Scripts
      </button>
      <h1 class="text-3xl font-bold">Debug Script: {{ script?.name }}</h1>
    </div>

    <!-- Loading State -->
    <div v-if="scriptStore.isLoading" class="text-center py-12">
      <p class="text-gray-500">Loading script...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="scriptStore.error" class="rounded-lg bg-red-50 p-4 text-red-700 mb-6">
      {{ scriptStore.error }}
    </div>

    <!-- Debug Interface -->
    <div v-else-if="script" class="grid grid-cols-2 gap-6">
      <!-- Left Panel: Script Info and Controls -->
      <div class="space-y-6">
        <!-- Script Info -->
        <div class="rounded-lg border bg-white p-6">
          <h2 class="text-xl font-semibold mb-4">Script Information</h2>
          <div class="space-y-2 text-sm">
            <div>
              <span class="font-medium">Type:</span>
              {{ script.scriptType }}
            </div>
            <div>
              <span class="font-medium">API:</span>
              {{ script.apiDefinitionId }}
            </div>
            <div>
              <span class="font-medium">Order:</span>
              {{ script.executionOrder }}
            </div>
            <div v-if="script.retryCount > 0">
              <span class="font-medium">Retry:</span>
              {{ script.retryCount }}times
            </div>
          </div>
        </div>

        <!-- Runtime Parameters -->
        <div class="rounded-lg border bg-white p-6">
          <h2 class="text-xl font-semibold mb-4">Runtime Parameters</h2>
          <textarea
            v-model="runtimeParamsInput"
            rows="8"
            class="w-full rounded-lg border px-4 py-2 font-mono text-sm"
            placeholder='{"key": "value"}'
          />
        </div>

        <!-- Execution Controls -->
        <div class="rounded-lg border bg-white p-6">
          <h2 class="text-xl font-semibold mb-4">Execution Controls</h2>
          <div class="space-y-3">
            <button
              @click="handleExecute"
              :disabled="scriptStore.isExecuting"
              class="w-full rounded-lg bg-green-600 px-4 py-3 text-white hover:bg-green-700 disabled:opacity-50"
            >
              {{ scriptStore.isExecuting ? 'Executing...' : 'Execute Script' }}
            </button>
            <button
              @click="handleDebug"
              :disabled="scriptStore.isDebugging"
              class="w-full rounded-lg bg-yellow-600 px-4 py-3 text-white hover:bg-yellow-700 disabled:opacity-50"
            >
              {{ scriptStore.isDebugging ? 'Debugging...' : 'Debug with Breakpoints' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Right Panel: Execution Results -->
      <div class="space-y-6">
        <!-- Execution Result -->
        <div v-if="scriptStore.executionResult" class="rounded-lg border bg-white p-6">
          <h2 class="text-xl font-semibold mb-4">Execution Result</h2>

          <!-- Status -->
          <div class="mb-4">
            <span
              :class="[
                'rounded-full px-3 py-1 text-sm font-semibold',
                scriptStore.executionResult.success
                  ? 'bg-green-100 text-green-700'
                  : 'bg-red-100 text-red-700',
              ]"
            >
              {{ scriptStore.executionResult.success ? 'Success' : 'Failed' }}
            </span>
            <span class="ml-3 text-sm text-gray-500">
              Duration: {{ scriptStore.executionResult.duration }}ms
            </span>
          </div>

          <!-- Error -->
          <div
            v-if="scriptStore.executionResult.error"
            class="mb-4 rounded-lg bg-red-50 p-4 text-red-700"
          >
            {{ scriptStore.executionResult.error }}
          </div>

          <!-- Status Code -->
          <div v-if="scriptStore.executionResult.statusCode" class="mb-4">
            <span class="text-sm font-medium">Status Code:</span>
            <span class="ml-2">{{ scriptStore.executionResult.statusCode }}</span>
          </div>

          <!-- Response Data -->
          <div v-if="scriptStore.executionResult.responseData" class="mb-4">
            <h3 class="text-sm font-medium mb-2">Response Data:</h3>
            <pre
              class="rounded-lg bg-gray-50 p-4 text-xs overflow-auto max-h-64"
            >{{ JSON.stringify(scriptStore.executionResult.responseData, null, 2) }}</pre>
          </div>

          <!-- Extracted Variables -->
          <div v-if="scriptStore.executionResult.extractedVariables" class="mb-4">
            <h3 class="text-sm font-medium mb-2">Extracted Variables:</h3>
            <pre
              class="rounded-lg bg-gray-50 p-4 text-xs overflow-auto"
            >{{ JSON.stringify(scriptStore.executionResult.extractedVariables, null, 2) }}</pre>
          </div>

          <!-- Assertion Results -->
          <div v-if="scriptStore.executionResult.assertionResults" class="mb-4">
            <h3 class="text-sm font-medium mb-2">Assertion Results:</h3>
            <div class="space-y-2">
              <div
                v-for="(result, index) in scriptStore.executionResult.assertionResults"
                :key="index"
                :class="[
                  'rounded-lg p-3 text-sm',
                  result.passed ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700',
                ]"
              >
                <div class="font-medium">{{ result.assertion.type }}</div>
                <div v-if="result.message" class="text-xs mt-1">{{ result.message }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- No Results Yet -->
        <div v-else class="rounded-lg border bg-gray-50 p-12 text-center">
          <p class="text-gray-500">No execution results yet. Click "Execute Script" to run.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, onMounted, ref } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import { useScriptStore } from '@/stores/script';

  const route = useRoute();
  const router = useRouter();
  const scriptStore = useScriptStore();

  const scriptId = computed(() => Number(route.params.id));
  const script = computed(() => scriptStore.currentScript);

  const runtimeParamsInput = ref('{}');

  onMounted(async () => {
    if (scriptId.value) {
      try {
        await scriptStore.fetchScriptById(scriptId.value);
      } catch (error) {
        console.error('Failed to load script:', error);
      }
    }
  });

  async function handleExecute() {
    try {
      const runtimeParams = JSON.parse(runtimeParamsInput.value);
      await scriptStore.executeScriptById(scriptId.value, runtimeParams);
    } catch (error) {
      console.error('Failed to execute script:', error);
    }
  }

  async function handleDebug() {
    try {
      const runtimeParams = JSON.parse(runtimeParamsInput.value);
      await scriptStore.debugScriptById(scriptId.value, [], runtimeParams);
    } catch (error) {
      console.error('Failed to debug script:', error);
    }
  }

  function goBack() {
    router.push('/scripts');
  }
</script>
