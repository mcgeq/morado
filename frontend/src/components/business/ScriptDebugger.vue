<template>
  <div class="card bg-base-100 shadow-lg">
    <div class="card-body">
      <!-- Header -->
      <div class="flex items-center justify-between mb-4">
        <h3 class="card-title">
          Script Debugger
          <span v-if="isDebugging" class="loading loading-spinner loading-sm"></span>
        </h3>
        <button type="button" class="btn btn-sm btn-ghost btn-circle" @click="$emit('close')">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>

      <!-- Script Info -->
      <div class="alert alert-info mb-4">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <div>
          <div class="font-bold">{{ script?.name }}</div>
          <div class="text-xs">{{ script?.description }}</div>
        </div>
      </div>

      <!-- Runtime Parameters -->
      <div class="mb-4">
        <label class="label">
          <span class="label-text font-semibold">Runtime Parameters (JSON)</span>
        </label>
        <textarea
          v-model="runtimeParamsJson"
          class="textarea textarea-bordered w-full font-mono text-sm"
          rows="4"
          placeholder='{"key": "value"}'
          :disabled="isDebugging"
        ></textarea>
        <label v-if="paramsError" class="label">
          <span class="label-text-alt text-error">{{ paramsError }}</span>
        </label>
      </div>

      <!-- Breakpoints -->
      <div class="mb-4">
        <label class="label">
          <span class="label-text font-semibold">Breakpoints</span>
        </label>
        <div class="space-y-2">
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="breakpoints.beforeRequest"
              type="checkbox"
              class="checkbox checkbox-sm"
              :disabled="isDebugging"
            />
            <span class="text-sm">Before API Request</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="breakpoints.afterRequest"
              type="checkbox"
              class="checkbox checkbox-sm"
              :disabled="isDebugging"
            />
            <span class="text-sm">After API Request</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="breakpoints.beforeAssertions"
              type="checkbox"
              class="checkbox checkbox-sm"
              :disabled="isDebugging"
            />
            <span class="text-sm">Before Assertions</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="breakpoints.afterAssertions"
              type="checkbox"
              class="checkbox checkbox-sm"
              :disabled="isDebugging"
            />
            <span class="text-sm">After Assertions</span>
          </label>
        </div>
      </div>

      <!-- Debug Controls -->
      <div class="flex gap-2 mb-4">
        <button
          type="button"
          class="btn btn-primary flex-1"
          :disabled="isDebugging"
          @click="startDebug"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5 mr-2"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
            />
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          Start Debug
        </button>
        <button type="button" class="btn btn-outline" :disabled="!isDebugging" @click="stopDebug">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"
            />
          </svg>
        </button>
      </div>

      <!-- Debug Output -->
      <div v-if="debugResult" class="space-y-4">
        <div class="divider">Debug Results</div>

        <!-- Status -->
        <div class="alert" :class="debugResult.success ? 'alert-success' : 'alert-error'">
          <svg
            v-if="debugResult.success"
            xmlns="http://www.w3.org/2000/svg"
            class="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <svg
            v-else
            xmlns="http://www.w3.org/2000/svg"
            class="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <div>
            <div class="font-bold">{{ debugResult.success ? 'Success' : 'Failed' }}</div>
            <div class="text-sm">Duration: {{ debugResult.duration }}ms</div>
          </div>
        </div>

        <!-- Response -->
        <div v-if="debugResult.responseData">
          <label class="label">
            <span class="label-text font-semibold">Response Data</span>
            <span class="label-text-alt">Status: {{ debugResult.statusCode }}</span>
          </label>
          <div class="mockup-code text-xs max-h-64 overflow-auto">
            <pre><code>{{ formatJson(debugResult.responseData) }}</code></pre>
          </div>
        </div>

        <!-- Extracted Variables -->
        <div
          v-if="debugResult.extractedVariables && Object.keys(debugResult.extractedVariables).length > 0"
        >
          <label class="label">
            <span class="label-text font-semibold">Extracted Variables</span>
          </label>
          <div class="mockup-code text-xs max-h-48 overflow-auto">
            <pre><code>{{ formatJson(debugResult.extractedVariables) }}</code></pre>
          </div>
        </div>

        <!-- Assertions -->
        <div v-if="debugResult.assertionResults && debugResult.assertionResults.length > 0">
          <label class="label">
            <span class="label-text font-semibold">Assertion Results</span>
          </label>
          <div class="space-y-2">
            <div
              v-for="(result, index) in debugResult.assertionResults"
              :key="index"
              class="alert alert-sm"
              :class="result.passed ? 'alert-success' : 'alert-error'"
            >
              <svg
                v-if="result.passed"
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M5 13l4 4L19 7"
                />
              </svg>
              <svg
                v-else
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
              <div class="text-xs">
                <div class="font-semibold">{{ result.assertion.type }}</div>
                <div v-if="result.message">{{ result.message }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Error -->
        <div v-if="debugResult.error" class="alert alert-error">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <div>
            <div class="font-bold">Error</div>
            <div class="text-sm">{{ debugResult.error }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, ref } from 'vue';
  import type { ScriptExecutionResult, TestScript } from '@/api/script';

  interface Props {
    script: TestScript | null;
  }

  defineProps<Props>();

  const emit = defineEmits<{
    close: [];
    debug: [params: Record<string, unknown>, breakpoints: unknown[]];
  }>();

  const isDebugging = ref(false);
  const runtimeParamsJson = ref('{}');
  const paramsError = ref('');
  const debugResult = ref<ScriptExecutionResult | null>(null);

  const breakpoints = ref({
    beforeRequest: false,
    afterRequest: false,
    beforeAssertions: false,
    afterAssertions: false,
  });

  const runtimeParams = computed(() => {
    try {
      paramsError.value = '';
      return JSON.parse(runtimeParamsJson.value);
    } catch (error) {
      paramsError.value = 'Invalid JSON format';
      return {};
    }
  });

  function startDebug() {
    if (paramsError.value) return;

    isDebugging.value = true;
    debugResult.value = null;

    const activeBreakpoints = [];
    if (breakpoints.value.beforeRequest) activeBreakpoints.push('before_request');
    if (breakpoints.value.afterRequest) activeBreakpoints.push('after_request');
    if (breakpoints.value.beforeAssertions) activeBreakpoints.push('before_assertions');
    if (breakpoints.value.afterAssertions) activeBreakpoints.push('after_assertions');

    emit('debug', runtimeParams.value, activeBreakpoints);
  }

  function stopDebug() {
    isDebugging.value = false;
  }

  function setDebugResult(result: ScriptExecutionResult) {
    debugResult.value = result;
    isDebugging.value = false;
  }

  function formatJson(data: unknown): string {
    try {
      return JSON.stringify(data, null, 2);
    } catch {
      return String(data);
    }
  }

  defineExpose({
    setDebugResult,
    stopDebug,
  });
</script>
