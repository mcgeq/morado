<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-6">
      <button @click="goBack" class="mb-4 text-blue-600 hover:text-blue-700">
        ← Back to API Definitions
      </button>
      <h1 class="text-3xl font-bold">
        {{ isEditMode ? 'Edit API Definition' : 'Create API Definition' }}
      </h1>
    </div>

    <!-- Loading State -->
    <div v-if="apiDefinitionStore.isLoading && isEditMode" class="text-center py-12">
      <p class="text-gray-500">Loading API definition...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="apiDefinitionStore.error" class="rounded-lg bg-red-50 p-4 text-red-700 mb-6">
      {{ apiDefinitionStore.error }}
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
          placeholder="e.g., Get User Profile"
        />
      </div>

      <!-- Description -->
      <div>
        <label class="block text-sm font-medium mb-2">Description</label>
        <textarea
          v-model="formData.description"
          rows="3"
          class="w-full rounded-lg border px-4 py-2"
          placeholder="Describe this API endpoint..."
        />
      </div>

      <!-- Method and URL -->
      <div class="grid grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium mb-2">Method *</label>
          <select v-model="formData.method" required class="w-full rounded-lg border px-4 py-2">
            <option value="GET">GET</option>
            <option value="POST">POST</option>
            <option value="PUT">PUT</option>
            <option value="PATCH">PATCH</option>
            <option value="DELETE">DELETE</option>
            <option value="HEAD">HEAD</option>
            <option value="OPTIONS">OPTIONS</option>
          </select>
        </div>
        <div class="col-span-3">
          <label class="block text-sm font-medium mb-2">URL *</label>
          <input
            v-model="formData.url"
            type="text"
            required
            class="w-full rounded-lg border px-4 py-2"
            placeholder="/api/users/${userId}"
          />
        </div>
      </div>

      <!-- Header Component -->
      <div>
        <label class="block text-sm font-medium mb-2">Header Component</label>
        <select v-model="formData.headerId" class="w-full rounded-lg border px-4 py-2">
          <option :value="undefined">None</option>
          <option v-for="header in headers" :key="header.id" :value="header.id">
            {{ header.name }}
          </option>
        </select>
      </div>

      <!-- Request Body -->
      <div>
        <label class="block text-sm font-medium mb-2">Request Body</label>
        <div class="space-y-3">
          <div class="flex items-center gap-2">
            <input
              v-model="requestBodyMode"
              type="radio"
              value="component"
              id="requestComponent"
            />
            <label for="requestComponent">Use Body Component</label>
          </div>
          <select
            v-if="requestBodyMode === 'component'"
            v-model="formData.requestBodyId"
            class="w-full rounded-lg border px-4 py-2"
          >
            <option :value="undefined">None</option>
            <option v-for="body in requestBodies" :key="body.id" :value="body.id">
              {{ body.name }}
            </option>
          </select>

          <div class="flex items-center gap-2">
            <input v-model="requestBodyMode" type="radio" value="inline" id="requestInline" />
            <label for="requestInline">Inline Request Body</label>
          </div>
          <textarea
            v-if="requestBodyMode === 'inline'"
            v-model="inlineRequestInput"
            rows="8"
            class="w-full rounded-lg border px-4 py-2 font-mono text-sm"
            placeholder='{"key": "value"}'
            @blur="updateInlineRequest"
          />
        </div>
      </div>

      <!-- Response Body -->
      <div>
        <label class="block text-sm font-medium mb-2">Response Body</label>
        <div class="space-y-3">
          <div class="flex items-center gap-2">
            <input
              v-model="responseBodyMode"
              type="radio"
              value="component"
              id="responseComponent"
            />
            <label for="responseComponent">Use Body Component</label>
          </div>
          <select
            v-if="responseBodyMode === 'component'"
            v-model="formData.responseBodyId"
            class="w-full rounded-lg border px-4 py-2"
          >
            <option :value="undefined">None</option>
            <option v-for="body in responseBodies" :key="body.id" :value="body.id">
              {{ body.name }}
            </option>
          </select>

          <div class="flex items-center gap-2">
            <input v-model="responseBodyMode" type="radio" value="inline" id="responseInline" />
            <label for="responseInline">Inline Response Body</label>
          </div>
          <textarea
            v-if="responseBodyMode === 'inline'"
            v-model="inlineResponseInput"
            rows="8"
            class="w-full rounded-lg border px-4 py-2 font-mono text-sm"
            placeholder='{"key": "value"}'
            @blur="updateInlineResponse"
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

      <!-- Active Status -->
      <div class="flex items-center gap-2">
        <input v-model="formData.isActive" type="checkbox" id="isActive" class="rounded" />
        <label for="isActive" class="text-sm font-medium">Active</label>
      </div>

      <!-- Actions -->
      <div class="flex gap-4">
        <button
          type="submit"
          :disabled="apiDefinitionStore.isSaving"
          class="rounded-lg bg-blue-600 px-6 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {{ apiDefinitionStore.isSaving ? 'Saving...' : isEditMode ? 'Update' : 'Create' }}
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
import { useApiDefinitionStore } from '@/stores/apiDefinition';
import { useHeaderStore } from '@/stores/header';
import { useBodyStore } from '@/stores/body';
import type { ApiDefinitionCreate, HttpMethod } from '@/api/api-definition';

const route = useRoute();
const router = useRouter();
const apiDefinitionStore = useApiDefinitionStore();
const headerStore = useHeaderStore();
const bodyStore = useBodyStore();

const isEditMode = computed(() => route.params.id !== 'new');
const apiDefinitionId = computed(() => (isEditMode.value ? Number(route.params.id) : null));

const formData = ref<ApiDefinitionCreate>({
  name: '',
  description: '',
  method: 'GET' as HttpMethod,
  url: '',
  isActive: true,
  tags: [],
});

const requestBodyMode = ref<'component' | 'inline'>('component');
const responseBodyMode = ref<'component' | 'inline'>('component');
const inlineRequestInput = ref('');
const inlineResponseInput = ref('');
const tagsInput = ref('');

const headers = computed(() => headerStore.activeHeaders);
const requestBodies = computed(() => bodyStore.requestBodies);
const responseBodies = computed(() => bodyStore.responseBodies);

onMounted(async () => {
  // Load headers and bodies for selection
  await Promise.all([headerStore.fetchHeaders(), bodyStore.fetchBodies()]);

  if (isEditMode.value && apiDefinitionId.value) {
    try {
      const api = await apiDefinitionStore.fetchApiDefinitionById(apiDefinitionId.value);
      formData.value = {
        name: api.name,
        description: api.description,
        method: api.method,
        url: api.url,
        headerId: api.headerId,
        requestBodyId: api.requestBodyId,
        responseBodyId: api.responseBodyId,
        inlineRequestBody: api.inlineRequestBody,
        inlineResponseBody: api.inlineResponseBody,
        isActive: api.isActive,
        tags: api.tags || [],
      };

      if (api.requestBodyId) {
        requestBodyMode.value = 'component';
      } else if (api.inlineRequestBody) {
        requestBodyMode.value = 'inline';
        inlineRequestInput.value = JSON.stringify(api.inlineRequestBody, null, 2);
      }

      if (api.responseBodyId) {
        responseBodyMode.value = 'component';
      } else if (api.inlineResponseBody) {
        responseBodyMode.value = 'inline';
        inlineResponseInput.value = JSON.stringify(api.inlineResponseBody, null, 2);
      }

      tagsInput.value = (api.tags || []).join(', ');
    } catch (error) {
      console.error('Failed to load API definition:', error);
    }
  }
});

function updateInlineRequest() {
  try {
    if (inlineRequestInput.value.trim()) {
      formData.value.inlineRequestBody = JSON.parse(inlineRequestInput.value);
      formData.value.requestBodyId = undefined;
    } else {
      formData.value.inlineRequestBody = undefined;
    }
  } catch (error) {
    console.error('Invalid JSON for inline request:', error);
  }
}

function updateInlineResponse() {
  try {
    if (inlineResponseInput.value.trim()) {
      formData.value.inlineResponseBody = JSON.parse(inlineResponseInput.value);
      formData.value.responseBodyId = undefined;
    } else {
      formData.value.inlineResponseBody = undefined;
    }
  } catch (error) {
    console.error('Invalid JSON for inline response:', error);
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
    // Clear unused fields based on mode
    if (requestBodyMode.value === 'component') {
      formData.value.inlineRequestBody = undefined;
    } else {
      formData.value.requestBodyId = undefined;
      updateInlineRequest();
    }

    if (responseBodyMode.value === 'component') {
      formData.value.inlineResponseBody = undefined;
    } else {
      formData.value.responseBodyId = undefined;
      updateInlineResponse();
    }

    updateTags();

    if (isEditMode.value && apiDefinitionId.value) {
      await apiDefinitionStore.updateExistingApiDefinition(apiDefinitionId.value, formData.value);
    } else {
      await apiDefinitionStore.createNewApiDefinition(formData.value);
    }

    router.push('/api-definitions');
  } catch (error) {
    console.error('Failed to save API definition:', error);
  }
}

function goBack() {
  router.push('/api-definitions');
}
</script>
