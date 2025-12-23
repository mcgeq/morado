<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-6">
      <button @click="goBack" class="mb-4 text-blue-600 hover:text-blue-700">
        ← Back to Bodies
      </button>
      <h1 class="text-3xl font-bold">{{ isEditMode ? 'Edit Body' : 'Create Body' }}</h1>
    </div>

    <!-- Loading State -->
    <div v-if="bodyStore.isLoading && isEditMode" class="text-center py-12">
      <p class="text-gray-500">Loading body...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="bodyStore.error" class="rounded-lg bg-red-50 p-4 text-red-700 mb-6">
      {{ bodyStore.error }}
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
          placeholder="e.g., User Registration Body"
        />
      </div>

      <!-- Description -->
      <div>
        <label class="block text-sm font-medium mb-2">Description</label>
        <textarea
          v-model="formData.description"
          rows="3"
          class="w-full rounded-lg border px-4 py-2"
          placeholder="Describe this body template..."
        />
      </div>

      <!-- Body Type -->
      <div>
        <label class="block text-sm font-medium mb-2">Body Type *</label>
        <select v-model="formData.bodyType" required class="w-full rounded-lg border px-4 py-2">
          <option value="request">Request</option>
          <option value="response">Response</option>
          <option value="both">Both</option>
        </select>
      </div>

      <!-- Content Type -->
      <div>
        <label class="block text-sm font-medium mb-2">Content Type *</label>
        <input
          v-model="formData.contentType"
          type="text"
          required
          class="w-full rounded-lg border px-4 py-2"
          placeholder="e.g., application/json"
        />
      </div>

      <!-- Scope -->
      <div>
        <label class="block text-sm font-medium mb-2">Scope *</label>
        <select v-model="formData.scope" required class="w-full rounded-lg border px-4 py-2">
          <option value="global">Global</option>
          <option value="project">Project</option>
          <option value="private">Private</option>
        </select>
      </div>

      <!-- Body Schema -->
      <div>
        <label class="block text-sm font-medium mb-2">Body Schema (JSON)</label>
        <textarea
          v-model="schemaInput"
          rows="10"
          class="w-full rounded-lg border px-4 py-2 font-mono text-sm"
          placeholder='{"type": "object", "properties": {...}}'
          @blur="updateSchema"
        />
        <button
          type="button"
          @click="validateSchemaInput"
          :disabled="bodyStore.isValidating"
          class="mt-2 rounded-lg bg-gray-100 px-4 py-2 text-gray-700 hover:bg-gray-200 disabled:opacity-50"
        >
          {{ bodyStore.isValidating ? 'Validating...' : 'Validate Schema' }}
        </button>
        <div v-if="bodyStore.validationErrors.length > 0" class="mt-2 text-red-600 text-sm">
          <p v-for="(error, index) in bodyStore.validationErrors" :key="index">{{ error }}</p>
        </div>
      </div>

      <!-- Example Data -->
      <div>
        <label class="block text-sm font-medium mb-2">Example Data (JSON)</label>
        <textarea
          v-model="exampleInput"
          rows="10"
          class="w-full rounded-lg border px-4 py-2 font-mono text-sm"
          placeholder='{"name": "John Doe", "email": "john@example.com"}'
          @blur="updateExample"
        />
      </div>

      <!-- Version -->
      <div>
        <label class="block text-sm font-medium mb-2">Version</label>
        <input
          v-model="formData.version"
          type="text"
          class="w-full rounded-lg border px-4 py-2"
          placeholder="e.g., 1.0.0"
        />
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
          :disabled="bodyStore.isSaving"
          class="rounded-lg bg-blue-600 px-6 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {{ bodyStore.isSaving ? 'Saving...' : isEditMode ? 'Update' : 'Create' }}
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
import { useBodyStore } from '@/stores/body';
import type { BodyCreate, BodyScope, BodyType } from '@/api/body';

const route = useRoute();
const router = useRouter();
const bodyStore = useBodyStore();

const isEditMode = computed(() => route.params.id !== 'new');
const bodyId = computed(() => (isEditMode.value ? Number(route.params.id) : null));

const formData = ref<BodyCreate>({
  name: '',
  description: '',
  bodyType: 'request' as BodyType,
  contentType: 'application/json',
  scope: 'project' as BodyScope,
  isActive: true,
  version: '1.0.0',
  tags: [],
});

const schemaInput = ref('');
const exampleInput = ref('');
const tagsInput = ref('');

onMounted(async () => {
  if (isEditMode.value && bodyId.value) {
    try {
      const body = await bodyStore.fetchBodyById(bodyId.value);
      formData.value = {
        name: body.name,
        description: body.description,
        bodyType: body.bodyType,
        contentType: body.contentType,
        bodySchema: body.bodySchema,
        exampleData: body.exampleData,
        scope: body.scope,
        isActive: body.isActive,
        version: body.version,
        tags: body.tags || [],
      };
      schemaInput.value = body.bodySchema ? JSON.stringify(body.bodySchema, null, 2) : '';
      exampleInput.value = body.exampleData ? JSON.stringify(body.exampleData, null, 2) : '';
      tagsInput.value = (body.tags || []).join(', ');
    } catch (error) {
      console.error('Failed to load body:', error);
    }
  }
});

function updateSchema() {
  try {
    if (schemaInput.value.trim()) {
      formData.value.bodySchema = JSON.parse(schemaInput.value);
    } else {
      formData.value.bodySchema = undefined;
    }
  } catch (error) {
    console.error('Invalid JSON schema:', error);
  }
}

function updateExample() {
  try {
    if (exampleInput.value.trim()) {
      formData.value.exampleData = JSON.parse(exampleInput.value);
    } else {
      formData.value.exampleData = undefined;
    }
  } catch (error) {
    console.error('Invalid JSON example:', error);
  }
}

function updateTags() {
  formData.value.tags = tagsInput.value
    .split(',')
    .map(tag => tag.trim())
    .filter(tag => tag.length > 0);
}

async function validateSchemaInput() {
  try {
    updateSchema();
    if (formData.value.bodySchema) {
      await bodyStore.validateSchema(formData.value.bodySchema);
    }
  } catch (error) {
    console.error('Schema validation failed:', error);
  }
}

async function handleSubmit() {
  try {
    updateSchema();
    updateExample();
    updateTags();
    
    if (isEditMode.value && bodyId.value) {
      await bodyStore.updateExistingBody(bodyId.value, formData.value);
    } else {
      await bodyStore.createNewBody(formData.value);
    }
    
    router.push('/bodies');
  } catch (error) {
    console.error('Failed to save body:', error);
  }
}

function goBack() {
  router.push('/bodies');
}
</script>
