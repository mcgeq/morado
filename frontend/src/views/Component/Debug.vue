<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-6">
      <button @click="goBack" class="mb-4 text-blue-600 hover:text-blue-700">
        ← Back to Components
      </button>
      <h1 class="text-3xl font-bold">Execute Component: {{ component?.name }}</h1>
    </div>

    <div v-if="component" class="grid grid-cols-2 gap-6">
      <!-- Left Panel -->
      <div class="space-y-6">
        <div class="rounded-lg border bg-white p-6">
          <h2 class="text-xl font-semibold mb-4">Component Information</h2>
          <div class="space-y-2 text-sm">
            <div>
              <span class="font-medium">Type:</span>
              {{ component.componentType }}
            </div>
            <div>
              <span class="font-medium">Execution Mode:</span>
              {{ component.executionMode }}
            </div>
            <div>
              <span class="font-medium">Version:</span>
              {{ component.version }}
            </div>
          </div>
        </div>

        <div class="rounded-lg border bg-white p-6">
          <h2 class="text-xl font-semibold mb-4">Runtime Parameters</h2>
          <textarea
            v-model="runtimeParamsInput"
            rows="8"
            class="w-full rounded-lg border px-4 py-2 font-mono text-sm"
            placeholder='{"key": "value"}'
          />
        </div>

        <div class="rounded-lg border bg-white p-6">
          <button
            @click="handleExecute"
            :disabled="componentStore.isExecuting"
            class="w-full rounded-lg bg-green-600 px-4 py-3 text-white hover:bg-green-700 disabled:opacity-50"
          >
            {{ componentStore.isExecuting ? 'Executing...' : 'Execute Component' }}
          </button>
        </div>
      </div>

      <!-- Right Panel -->
      <div class="space-y-6">
        <div v-if="componentStore.executionResult" class="rounded-lg border bg-white p-6">
          <h2 class="text-xl font-semibold mb-4">Execution Result</h2>
          <div class="mb-4">
            <span
              :class="[
                'rounded-full px-3 py-1 text-sm font-semibold',
                componentStore.executionResult.success
                  ? 'bg-green-100 text-green-700'
                  : 'bg-red-100 text-red-700',
              ]"
            >
              {{ componentStore.executionResult.success ? 'Success' : 'Failed' }}
            </span>
          </div>
          <pre
            class="rounded-lg bg-gray-50 p-4 text-xs overflow-auto max-h-96"
          >{{ JSON.stringify(componentStore.executionResult, null, 2) }}</pre>
        </div>
        <div v-else class="rounded-lg border bg-gray-50 p-12 text-center">
          <p class="text-gray-500">No execution results yet.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, onMounted, ref } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import { useComponentStore } from '@/stores/component';

  const route = useRoute();
  const router = useRouter();
  const componentStore = useComponentStore();

  const componentId = computed(() => Number(route.params.id));
  const component = computed(() => componentStore.currentComponent);

  const runtimeParamsInput = ref('{}');

  onMounted(async () => {
    if (componentId.value) {
      await componentStore.fetchComponentById(componentId.value);
    }
  });

  async function handleExecute() {
    try {
      const runtimeParams = JSON.parse(runtimeParamsInput.value);
      await componentStore.executeComponentById(componentId.value, runtimeParams);
    } catch (error) {
      console.error('Failed to execute component:', error);
    }
  }

  function goBack() {
    router.push('/components');
  }
</script>
