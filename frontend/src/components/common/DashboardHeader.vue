<template>
  <header class="card widget-margin-bottom" role="banner">
    <div class="flex items-center justify-between">
      <!-- Title Section -->
      <div class="flex-1">
        <h1 class="text-3xl font-bold text-gray-900">{{ title || t('dashboard.title') }}</h1>
        <p v-if="lastUpdated" class="text-sm text-gray-500 mt-2" role="status" aria-live="polite">
          <span class="sr-only">{{ t('dashboard.title') }}</span>{{ t('dashboard.lastUpdated') }}: {{ formattedLastUpdated }}
        </p>
      </div>

      <!-- Refresh Button Section -->
      <div class="flex-shrink-0 ml-4">
        <RefreshButton
          :loading="loading"
          :show-label="true"
          variant="ghost"
          size="md"
          @click="handleRefresh"
          :aria-label="t('common.refreshData')"
        />
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
  import { computed } from 'vue';
  import { useLocale } from '@/composables/useLocale';
  import RefreshButton from './RefreshButton.vue';

  // ============================================================================
  // Props
  // ============================================================================

  interface Props {
    title?: string;
    lastUpdated?: Date | null;
    loading?: boolean;
  }

  const props = withDefaults(defineProps<Props>(), {
    title: '',
    lastUpdated: null,
    loading: false,
  });
  
  const { t, formatDate } = useLocale();

  // Runtime prop validation in development
  if (import.meta.env.DEV) {
    if (props.title !== undefined && typeof props.title !== 'string') {
      console.warn('[DashboardHeader] title must be a string');
    }

    if (props.lastUpdated !== null && props.lastUpdated !== undefined) {
      if (!(props.lastUpdated instanceof Date)) {
        console.warn('[DashboardHeader] lastUpdated must be a Date object or null');
      } else if (Number.isNaN(props.lastUpdated.getTime())) {
        console.warn('[DashboardHeader] lastUpdated is an invalid Date');
      }
    }

    if (typeof props.loading !== 'boolean') {
      console.warn('[DashboardHeader] loading must be a boolean');
    }
  }

  // ============================================================================
  // Emits
  // ============================================================================

  const emit = defineEmits<{
    refresh: [];
  }>();

  // ============================================================================
  // Computed
  // ============================================================================

  /**
   * Format last updated timestamp to readable format
   */
  const formattedLastUpdated = computed(() => {
    if (!props.lastUpdated) return '';

    try {
      return formatDate(props.lastUpdated, 'long');
    } catch {
      return '';
    }
  });

  // ============================================================================
  // Methods
  // ============================================================================

  /**
   * Handle refresh button click
   */
  function handleRefresh(): void {
    emit('refresh');
  }
</script>

<style scoped>
  /* Card-specific styles using design system */
  .card {
    transition: box-shadow 0.3s ease;
  }

  .card:hover {
    box-shadow:
      0 4px 6px -1px rgba(0, 0, 0, 0.1),
      0 2px 4px -1px rgba(0, 0, 0, 0.06);
  }
</style>
