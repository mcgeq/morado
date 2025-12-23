<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-6">
      <button @click="goBack" class="mb-4 text-blue-600 hover:text-blue-700">
        ← Back to Headers
      </button>
      <h1 class="text-3xl font-bold">{{ isEditMode ? 'Edit Header' : 'Create Header' }}</h1>
    </div>

    <!-- Loading State -->
    <div v-if="headerStore.isLoading && isEditMode" class="text-center py-12">
      <p class="text-gray-500">Loading header...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="headerStore.error" class="rounded-lg bg-red-50 p-4 text-red-700 mb-6">
      {{ headerStore.error }}
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
          placeholder="e.g., Authentication Headers"
        />
      </div>

      <!-- Description -->
      <div>
        <label class="block text-sm font-medium mb-2">Description</label>
        <textarea
          v-model="formData.description"
          rows="3"
          class="w-full rounded-lg border px-4 py-2"
          placeholder="Describe this header component..."
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

      <!-- Headers -->
      <div>
        <label class="block text-sm font-medium mb-2">Headers *</label>
        <div class="space-y-3">
          <div
            v-for="(value, key, index) in formData.headers"
            :key="index"
            class="flex gap-2"
          >
            <input
              v-model="headerKeys[index]"
              type="text"
              placeholder="Header name"
              class="flex-1 rounded-lg border px-4 py-2"
              @blur="updateHeaderKey(index, key as string)"
            />
            <input
              v-model="formData.headers[key as string]"
              type="text"
              placeholder="Header value"
              class="flex-1 rounded-lg border px-4 py-2"
            />
            <button
              type="button"
              @click="removeHeader(key as string)"
              class="rounded-lg bg-red-100 px-3 py-2 text-red-700 hover:bg-red-200"
            >
              Remove
            </button>
          </div>
        </div>
        <button
          type="button"
          @click="addHeader"
          class="mt-3 rounded-lg bg-gray-100 px-4 py-2 text-gray-700 hover:bg-gray-200"
        >
          Add Header
        </button>
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
          :disabled="headerStore.isSaving"
          class="rounded-lg bg-blue-600 px-6 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {{ headerStore.isSaving ? 'Saving...' : isEditMode ? 'Update' : 'Create' }}
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
import { useHeaderStore } from '@/stores/header';
import type { HeaderCreate, HeaderScope } from '@/api/header';

const route = useRoute();
const router = useRouter();
const headerStore = useHeaderStore();

const isEditMode = computed(() => route.params.id !== 'new');
const headerId = computed(() => (isEditMode.value ? Number(route.params.id) : null));

const formData = ref<HeaderCreate>({
  name: '',
  description: '',
  headers: {},
  scope: 'project' as HeaderScope,
  isActive: true,
  version: '1.0.0',
  tags: [],
});

const headerKeys = ref<string[]>([]);
const tagsInput = ref('');

onMounted(async () => {
  if (isEditMode.value && headerId.value) {
    try {
      const header = await headerStore.fetchHeaderById(headerId.value);
      formData.value = {
        name: header.name,
        description: header.description,
        headers: { ...header.headers },
        scope: header.scope,
        isActive: header.isActive,
        version: header.version,
        tags: header.tags || [],
      };
      headerKeys.value = Object.keys(header.headers);
      tagsInput.value = (header.tags || []).join(', ');
    } catch (error) {
      console.error('Failed to load header:', error);
    }
  }
});

function addHeader() {
  const newKey = `Header-${Object.keys(formData.value.headers).length + 1}`;
  formData.value.headers[newKey] = '';
  headerKeys.value.push(newKey);
}

function removeHeader(key: string) {
  delete formData.value.headers[key];
  headerKeys.value = headerKeys.value.filter(k => k !== key);
}

function updateHeaderKey(index: number, oldKey: string) {
  const newKey = headerKeys.value[index];
  if (newKey !== oldKey && newKey) {
    const headerValue = formData.value.headers[oldKey];
    delete formData.value.headers[oldKey];
    formData.value.headers[newKey] = headerValue || '';
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
    updateTags();
    
    if (isEditMode.value && headerId.value) {
      await headerStore.updateExistingHeader(headerId.value, formData.value);
    } else {
      await headerStore.createNewHeader(formData.value);
    }
    
    router.push('/headers');
  } catch (error) {
    console.error('Failed to save header:', error);
  }
}

function goBack() {
  router.push('/headers');
}
</script>
