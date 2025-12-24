<template>
  <div class="loading-state" role="status" aria-live="polite" aria-busy="true">
    <span class="sr-only">{{ t('common.loadingDashboard') }}</span>
    
    <!-- Dashboard Header Skeleton -->
    <div v-if="showHeader" class="header-skeleton mb-6" aria-hidden="true">
      <div
        class="flex items-center justify-between bg-white rounded-lg shadow-md p-4 animate-pulse"
      >
        <div class="h-8 bg-gray-200 rounded w-48"></div>
        <div class="h-10 bg-gray-200 rounded w-32"></div>
      </div>
    </div>

    <!-- User Profile Card Skeleton -->
    <div v-if="showProfile" class="profile-skeleton mb-6" aria-hidden="true">
      <WidgetSkeleton type="profile" />
    </div>

    <!-- Statistics Grid Skeleton -->
    <div v-if="showStatistics" class="statistics-grid-skeleton" aria-hidden="true">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- Steps Statistics Widget Skeleton -->
        <div v-if="showStepsStats">
          <WidgetSkeleton type="chart" />
        </div>

        <!-- API Usage Widget Skeleton -->
        <div v-if="showApiUsage">
          <WidgetSkeleton type="stats" />
        </div>

        <!-- Trend Analysis Widget Skeleton -->
        <div v-if="showTrends" class="lg:col-span-3">
          <WidgetSkeleton type="trend" />
        </div>
      </div>
    </div>

    <!-- Full Dashboard Loading (all widgets) -->
    <div v-if="fullDashboard" class="full-dashboard-skeleton" aria-hidden="true">
      <!-- Header -->
      <div class="header-skeleton mb-6">
        <div
          class="flex items-center justify-between bg-white rounded-lg shadow-md p-4 animate-pulse"
        >
          <div class="h-8 bg-gray-200 rounded w-48"></div>
          <div class="h-10 bg-gray-200 rounded w-32"></div>
        </div>
      </div>

      <!-- Profile Card -->
      <div class="mb-6">
        <WidgetSkeleton type="profile" />
      </div>

      <!-- Statistics Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <WidgetSkeleton type="chart" />
        <WidgetSkeleton type="stats" />
        <div class="lg:col-span-3">
          <WidgetSkeleton type="trend" />
        </div>
      </div>
    </div>

    <!-- Loading Text (optional) -->
    <div v-if="showLoadingText" class="loading-text text-center mt-8">
      <div class="flex items-center justify-center">
        <svg class="animate-spin h-5 w-5 text-blue-600 mr-3" fill="none" viewBox="0 0 24 24" aria-hidden="true">
          <circle
            class="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            stroke-width="4"
          />
          <path
            class="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
        <span class="text-sm text-gray-600">{{ loadingText || t('common.loading') }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { useI18n } from 'vue-i18n';
  import WidgetSkeleton from './WidgetSkeleton.vue';

  export interface LoadingStateProps {
    // Show specific sections
    showHeader?: boolean;
    showProfile?: boolean;
    showStatistics?: boolean;
    showStepsStats?: boolean;
    showApiUsage?: boolean;
    showTrends?: boolean;

    // Show full dashboard loading
    fullDashboard?: boolean;

    // Loading text
    showLoadingText?: boolean;
    loadingText?: string;
  }

  withDefaults(defineProps<LoadingStateProps>(), {
    showHeader: false,
    showProfile: false,
    showStatistics: false,
    showStepsStats: false,
    showApiUsage: false,
    showTrends: false,
    fullDashboard: true,
    showLoadingText: false,
    loadingText: '',
  });
  
  const { t } = useI18n();
</script>

<style scoped>
  .loading-state {
    width: 100%;
  }

  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }

  .animate-spin {
    animation: spin 1s linear infinite;
  }

  @keyframes pulse {
    0%,
    100% {
      opacity: 1;
    }
    50% {
      opacity: 0.5;
    }
  }

  .animate-pulse {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }
</style>
