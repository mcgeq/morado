<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-6">
      <button @click="goBack" class="mb-4 text-blue-600 hover:text-blue-700">
        ← Back to Components
      </button>
      <h1 class="text-3xl font-bold">
        {{ isEditMode ? 'Edit Component' : 'Create Component' }}
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
        />
      </div>

      <div>
        <label class="block text-sm font-medium mb-2">Description</label>
        <textarea
          v-model="formData.description"
          rows="3"
          class="w-full rounded-lg border px-4 py-2"
        />
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium mb-2">Component Type *</label>
          <select v-model="formData.componentType" required class="w-full rounded-lg border px-4 py-2">
            <option value="simple">Simple</option>
            <option value="composite">Composite</option>
            <option value="template">Template</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">Execution Mode *</label>
          <select v-model="formData.executionMode" required class="w-full rounded-lg border px-4 py-2">
            <option value="sequential">Sequential</option>
            <option value="parallel">Parallel</option>
            <option value="conditional">Conditional</option>
          </select>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium mb-2">Parent Component</label>
        <select v-model="formData.parentComponentId" class="w-full rounded-lg border px-4 py-2">
          <option :value="undefined">None (Root Component)</option>
          <option v-for="comp in components" :key="comp.id" :value="comp.id">
            {{ comp.name }}
          </option>
        </select>
      </div>

      <div class="flex items-center gap-2">
        <input v-model="formData.isActive" type="checkbox" id="isActive" class="rounded" />
        <label for="isActive" class="text-sm font-medium">Active</label>
      </div>

      <div class="flex gap-4">
        <button
          type="submit"
          :disabled="componentStore.isSaving"
          class="rounded-lg bg-blue-600 px-6 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {{ componentStore.isSaving ? 'Saving...' : isEditMode ? 'Update' : 'Create' }}
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
import { useComponentStore } from '@/stores/component';
import type { TestComponentCreate, ComponentType, ExecutionMode } from '@/api/component';

const route = useRoute();
const router = useRouter();
const componentStore = useComponentStore();

const isEditMode = computed(() => route.params.id !== 'new');
const componentId = computed(() => (isEditMode.value ? Number(route.params.id) : null));

const formData = ref<TestComponentCreate>({
  name: '',
  description: '',
  componentType: 'simple' as ComponentType,
  executionMode: 'sequential' as ExecutionMode,
  isActive: true,
  version: '1.0.0',
});

const components = computed(() => componentStore.rootComponents);

onMounted(async () => {
  await componentStore.fetchComponents();

  if (isEditMode.value && componentId.value) {
    try {
      const component = await componentStore.fetchComponentById(componentId.value);
      formData.value = {
        name: component.name,
        description: component.description,
        componentType: component.componentType,
        executionMode: component.executionMode,
        parentComponentId: component.parentComponentId,
        isActive: component.isActive,
        version: component.version,
      };
    } catch (error) {
      console.error('Failed to load component:', error);
    }
  }
});

async function handleSubmit() {
  try {
    if (isEditMode.value && componentId.value) {
      await componentStore.updateExistingComponent(componentId.value, formData.value);
    } else {
      await componentStore.createNewComponent(formData.value);
    }
    router.push('/components');
  } catch (error) {
    console.error('Failed to save component:', error);
  }
}

function goBack() {
  router.push('/components');
}
</script>
