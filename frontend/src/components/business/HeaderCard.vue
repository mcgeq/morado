<template>
  <div class="card bg-base-100 shadow-md hover:shadow-lg transition-shadow">
    <div class="card-body">
      <!-- Header -->
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <h3 class="card-title text-lg">
            {{ header.name }}
            <span v-if="!header.isActive" class="badge badge-ghost badge-sm">Inactive</span>
            <span class="badge badge-sm" :class="scopeBadgeClass">{{ header.scope }}</span>
          </h3>
          <p v-if="header.description" class="text-sm text-base-content/70 mt-1">
            {{ header.description }}
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
              <a @click="$emit('edit', header)">Edit</a>
            </li>
            <li>
              <a @click="$emit('duplicate', header)">Duplicate</a>
            </li>
            <li>
              <a @click="$emit('view', header)">View Details</a>
            </li>
            <li class="divider"></li>
            <li>
              <a @click="$emit('delete', header)" class="text-error">Delete</a>
            </li>
          </ul>
        </div>
      </div>

      <!-- Headers Preview -->
      <div class="mt-4">
        <div class="text-xs font-semibold text-base-content/60 mb-2">
          Headers ({{ headerCount }})
        </div>
        <div class="space-y-1">
          <div
            v-for="(value, key) in previewHeaders"
            :key="key"
            class="flex items-center gap-2 text-sm"
          >
            <code class="text-xs bg-base-200 px-2 py-1 rounded">{{ key }}</code>
            <span class="text-base-content/70 truncate">{{ value }}</span>
          </div>
          <div v-if="hasMoreHeaders" class="text-xs text-base-content/50 italic">
            +{{ remainingHeaderCount }}more...
          </div>
        </div>
      </div>

      <!-- Tags -->
      <div v-if="header.tags && header.tags.length > 0" class="mt-3 flex flex-wrap gap-1">
        <span v-for="tag in header.tags" :key="tag" class="badge badge-sm badge-outline">
          {{ tag }}
        </span>
      </div>

      <!-- Footer -->
      <div class="card-actions justify-between items-center mt-4 pt-3 border-t border-base-300">
        <div class="text-xs text-base-content/50">
          v{{ header.version }}• {{ formatDate(header.updatedAt) }}
        </div>
        <button type="button" class="btn btn-primary btn-sm" @click="$emit('use', header)">
          Use Header
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed } from 'vue';
  import type { Header } from '@/api/header';

  interface Props {
    header: Header;
    maxPreview?: number;
  }

  const props = withDefaults(defineProps<Props>(), {
    maxPreview: 3,
  });

  defineEmits<{
    edit: [header: Header];
    duplicate: [header: Header];
    delete: [header: Header];
    view: [header: Header];
    use: [header: Header];
  }>();

  const scopeBadgeClass = computed(() => {
    switch (props.header.scope) {
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

  const headerCount = computed(() => Object.keys(props.header.headers).length);

  const previewHeaders = computed(() => {
    const entries = Object.entries(props.header.headers);
    return Object.fromEntries(entries.slice(0, props.maxPreview));
  });

  const hasMoreHeaders = computed(() => headerCount.value > props.maxPreview);

  const remainingHeaderCount = computed(() => headerCount.value - props.maxPreview);

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
