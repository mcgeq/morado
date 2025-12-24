<template>
  <div class="card bg-base-100 shadow-md hover:shadow-lg transition-shadow">
    <div class="card-body">
      <!-- Header -->
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <h3 class="card-title text-lg">
            {{ body.name }}
            <span v-if="!body.isActive" class="badge badge-ghost badge-sm">Inactive</span>
            <span class="badge badge-sm" :class="typeBadgeClass">{{ body.bodyType }}</span>
            <span class="badge badge-sm" :class="scopeBadgeClass">{{ body.scope }}</span>
          </h3>
          <p v-if="body.description" class="text-sm text-base-content/70 mt-1">
            {{ body.description }}
          </p>
        </div>

        <div class="dropdown dropdown-end">
          <button type="button" tabindex="0" class="btn btn-ghost btn-sm btn-circle">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              class="w-5 h-5 stroke-current"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"
              />
            </svg>
          </button>
          <ul
            tabindex="0"
            class="dropdown-content menu p-2 shadow bg-base-100 rounded-box w-52 z-10"
          >
            <li>
              <a @click="$emit('edit', body)">Edit</a>
            </li>
            <li>
              <a @click="$emit('duplicate', body)">Duplicate</a>
            </li>
            <li>
              <a @click="$emit('view', body)">View Details</a>
            </li>
            <li>
              <a @click="$emit('validate', body)">Validate Schema</a>
            </li>
            <li class="divider"></li>
            <li>
              <a @click="$emit('delete', body)" class="text-error">Delete</a>
            </li>
          </ul>
        </div>
      </div>

      <!-- Content Type -->
      <div class="mt-3">
        <div class="flex items-center gap-2">
          <span class="text-xs font-semibold text-base-content/60">Content-Type:</span>
          <code class="text-xs bg-base-200 px-2 py-1 rounded">{{ body.contentType }}</code>
        </div>
      </div>

      <!-- Schema Preview -->
      <div v-if="body.bodySchema" class="mt-3">
        <div class="text-xs font-semibold text-base-content/60 mb-2">Schema</div>
        <div class="mockup-code text-xs max-h-32 overflow-auto">
          <pre><code>{{ formatSchema(body.bodySchema) }}</code></pre>
        </div>
      </div>

      <!-- Example Data Preview -->
      <div v-if="body.exampleData" class="mt-3">
        <div class="text-xs font-semibold text-base-content/60 mb-2">Example Data</div>
        <div class="mockup-code text-xs max-h-32 overflow-auto">
          <pre><code>{{ formatSchema(body.exampleData) }}</code></pre>
        </div>
      </div>

      <!-- Tags -->
      <div v-if="body.tags && body.tags.length > 0" class="mt-3 flex flex-wrap gap-1">
        <span v-for="tag in body.tags" :key="tag" class="badge badge-sm badge-outline">
          {{ tag }}
        </span>
      </div>

      <!-- Footer -->
      <div class="card-actions justify-between items-center mt-4 pt-3 border-t border-base-300">
        <div class="text-xs text-base-content/50">
          v{{ body.version }}• {{ formatDate(body.updatedAt) }}
        </div>
        <button type="button" class="btn btn-primary btn-sm" @click="$emit('use', body)">
          Use Body
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed } from 'vue';
  import type { Body } from '@/api/body';

  interface Props {
    body: Body;
  }

  defineProps<Props>();

  defineEmits<{
    edit: [body: Body];
    duplicate: [body: Body];
    delete: [body: Body];
    view: [body: Body];
    validate: [body: Body];
    use: [body: Body];
  }>();

  const typeBadgeClass = computed(() => {
    const props = defineProps<Props>();
    switch (props.body.bodyType) {
      case 'request':
        return 'badge-primary';
      case 'response':
        return 'badge-secondary';
      case 'both':
        return 'badge-accent';
      default:
        return 'badge-ghost';
    }
  });

  const scopeBadgeClass = computed(() => {
    const props = defineProps<Props>();
    switch (props.body.scope) {
      case 'global':
        return 'badge-info';
      case 'project':
        return 'badge-success';
      case 'private':
        return 'badge-warning';
      default:
        return 'badge-ghost';
    }
  });

  function formatSchema(schema: Record<string, unknown>): string {
    try {
      return JSON.stringify(schema, null, 2);
    } catch {
      return String(schema);
    }
  }

  function formatDate(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
    return date.toLocaleDateString();
  }
</script>
