<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-6">
      <button @click="goBack" class="mb-4 text-blue-600 hover:text-blue-700">
        ← Back to Scripts
      </button>
      <h1 class="text-3xl font-bold">{{ isEditMode ? 'Edit Script' : 'Create Script' }}</h1>
    </div>

    <!-- Loading State -->
    <div v-if="scriptStore.isLoading && isEditMode" class="text-center py-12">
      <p class="text-gray-500">Loading script...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="scriptStore.error" class="rounded-lg bg-red-50 p-4 text-red-700 mb-6">
      {{ scriptStore.error }}
    </div>

    <!-- Form -->
    <form v-else @submit.prevent="handleSubmit" class="max-w-3xl space-y-6">
      <!-- Name -->
      <div>
        <label class="block text-sm font-medium mb-2">Name *</label>
        <input
          v-model="formData.name"
          type="text"
          required
          class="w-full rounded-lg border px-4 py-2"
          placeholder="e.g., Login Test Script"
        />
      </div>

      <!-- Description -->
      <div>
        <label class="block text-sm font-medium mb-2">Description</label>
        <textarea
          v-model="formData.description"
          rows="3"
          class="w-full rounded-lg border px-4 py-2"
          placeholder="Describe this script..."
        />
      </div>

      <!-- API Definition -->
      <div>
        <label class="block text-sm font-medium mb-2">API Definition *</label>
        <select
          v-model="formData.apiDefinitionId"
          required
          class="w-full rounded-lg border px-4 py-2"
        >
          <option :value="undefined">Select an API definition</option>
          <option v-for="api in apiDefinitions" :key="api.id" :value="api.id">
            {{ api.method }}- {{ api.name }}
          </option>
        </select>
      </div>

      <!-- Script Type and Execution Order -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium mb-2">Script Type *</label>
          <select v-model="formData.scriptType" required class="w-full rounded-lg border px-4 py-2">
            <option value="setup">Setup</option>
            <option value="main">Main</option>
            <option value="teardown">Teardown</option>
            <option value="utility">Utility</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">Execution Order</label>
          <input
            v-model.number="formData.executionOrder"
            type="number"
            class="w-full rounded-lg border px-4 py-2"
          />
        </div>
      </div>

      <!-- Variables -->
      <div>
        <label class="block text-sm font-medium mb-2">Variables (JSON)</label>
        <textarea
          v-model="variablesInput"
          rows="6"
          class="w-full rounded-lg border px-4 py-2 font-mono text-sm"
          placeholder='{"key": "value"}'
          @blur="updateVariables"
        />
      </div>

      <!-- Pre/Post Scripts -->
      <div>
        <label class="block text-sm font-medium mb-2">Pre-Script</label>
        <textarea
          v-model="formData.preScript"
          rows="4"
          class="w-full rounded-lg border px-4 py-2 font-mono text-sm"
          placeholder="JavaScript code to run before the request..."
        />
      </div>

      <div>
        <label class="block text-sm font-medium mb-2">Post-Script</label>
        <textarea
          v-model="formData.postScript"
          rows="4"
          class="w-full rounded-lg border px-4 py-2 font-mono text-sm"
          placeholder="JavaScript code to run after the request..."
        />
      </div>

      <!-- Retry Settings -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium mb-2">Retry Count</label>
          <input
            v-model.number="formData.retryCount"
            type="number"
            min="0"
            class="w-full rounded-lg border px-4 py-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">Retry Interval (ms)</label>
          <input
            v-model.number="formData.retryInterval"
            type="number"
            min="0"
            class="w-full rounded-lg border px-4 py-2"
          />
        </div>
      </div>

      <!-- Tags -->
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

      <!-- Checkboxes -->
      <div class="space-y-2">
        <div class="flex items-center gap-2">
          <input v-model="formData.isActive" type="checkbox" id="isActive" class="rounded" />
          <label for="isActive" class="text-sm font-medium">Active</label>
        </div>
        <div class="flex items-center gap-2">
          <input v-model="formData.debugMode" type="checkbox" id="debugMode" class="rounded" />
          <label for="debugMode" class="text-sm font-medium">Debug Mode</label>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex gap-4">
        <button
          type="submit"
          :disabled="scriptStore.isSaving"
          class="rounded-lg bg-blue-600 px-6 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {{ scriptStore.isSaving ? 'Saving...' : isEditMode ? 'Update' : 'Create' }}
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
  import { computed, onMounted, ref } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import type { ScriptType, TestScriptCreate } from '@/api/script';
  import { useApiDefinitionStore } from '@/stores/apiDefinition';
  import { useScriptStore } from '@/stores/script';

  const route = useRoute();
  const router = useRouter();
  const scriptStore = useScriptStore();
  const apiDefinitionStore = useApiDefinitionStore();

  const isEditMode = computed(() => route.params.id !== 'new');
  const scriptId = computed(() => (isEditMode.value ? Number(route.params.id) : null));

  const formData = ref<TestScriptCreate>({
    name: '',
    description: '',
    apiDefinitionId: 0,
    scriptType: 'main' as ScriptType,
    executionOrder: 1,
    retryCount: 0,
    retryInterval: 1000,
    isActive: true,
    debugMode: false,
    tags: [],
  });

  const variablesInput = ref('');
  const tagsInput = ref('');

  const apiDefinitions = computed(() => apiDefinitionStore.activeApiDefinitions);

  onMounted(async () => {
    await apiDefinitionStore.fetchApiDefinitions();

    if (isEditMode.value && scriptId.value) {
      try {
        const script = await scriptStore.fetchScriptById(scriptId.value);
        formData.value = {
          name: script.name,
          description: script.description,
          apiDefinitionId: script.apiDefinitionId,
          scriptType: script.scriptType,
          executionOrder: script.executionOrder,
          variables: script.variables,
          preScript: script.preScript,
          postScript: script.postScript,
          retryCount: script.retryCount,
          retryInterval: script.retryInterval,
          isActive: script.isActive,
          debugMode: script.debugMode,
          tags: script.tags || [],
        };
        variablesInput.value = script.variables ? JSON.stringify(script.variables, null, 2) : '';
        tagsInput.value = (script.tags || []).join(', ');
      } catch (error) {
        console.error('Failed to load script:', error);
      }
    }
  });

  function updateVariables() {
    try {
      if (variablesInput.value.trim()) {
        formData.value.variables = JSON.parse(variablesInput.value);
      } else {
        formData.value.variables = undefined;
      }
    } catch (error) {
      console.error('Invalid JSON for variables:', error);
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
      updateVariables();
      updateTags();

      if (isEditMode.value && scriptId.value) {
        await scriptStore.updateExistingScript(scriptId.value, formData.value);
      } else {
        await scriptStore.createNewScript(formData.value);
      }

      router.push('/scripts');
    } catch (error) {
      console.error('Failed to save script:', error);
    }
  }

  function goBack() {
    router.push('/scripts');
  }
</script>
