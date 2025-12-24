<template>
  <div class="widget-skeleton bg-white rounded-lg shadow-md p-6 animate-pulse">
    <!-- Widget Header Skeleton -->
    <div class="skeleton-header mb-4">
      <div class="h-6 bg-gray-200 rounded w-1/3"></div>
    </div>

    <!-- Widget Content Skeleton - varies by type -->
    <div v-if="type === 'profile'" class="skeleton-profile">
      <!-- Avatar and info -->
      <div class="flex items-center mb-4">
        <div class="w-16 h-16 bg-gray-200 rounded-full mr-4"></div>
        <div class="flex-1">
          <div class="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
          <div class="h-3 bg-gray-200 rounded w-1/3"></div>
        </div>
      </div>
      <!-- Metrics -->
      <div class="grid grid-cols-3 gap-4">
        <div class="h-16 bg-gray-200 rounded"></div>
        <div class="h-16 bg-gray-200 rounded"></div>
        <div class="h-16 bg-gray-200 rounded"></div>
      </div>
    </div>

    <div v-else-if="type === 'chart'" class="skeleton-chart">
      <!-- Chart area -->
      <div class="flex items-center justify-center">
        <div class="w-48 h-48 bg-gray-200 rounded-full"></div>
        <div class="ml-8 flex-1 space-y-3">
          <div class="h-4 bg-gray-200 rounded w-3/4"></div>
          <div class="h-4 bg-gray-200 rounded w-2/3"></div>
          <div class="h-4 bg-gray-200 rounded w-3/4"></div>
        </div>
      </div>
    </div>

    <div v-else-if="type === 'stats'" class="skeleton-stats">
      <!-- Stats grid -->
      <div class="grid grid-cols-2 gap-6">
        <div class="space-y-3">
          <div class="h-12 bg-gray-200 rounded w-1/2"></div>
          <div class="h-4 bg-gray-200 rounded w-full"></div>
          <div class="h-4 bg-gray-200 rounded w-full"></div>
          <div class="h-4 bg-gray-200 rounded w-3/4"></div>
        </div>
        <div class="space-y-3">
          <div class="h-12 bg-gray-200 rounded w-1/2"></div>
          <div class="h-4 bg-gray-200 rounded w-full"></div>
          <div class="h-4 bg-gray-200 rounded w-full"></div>
          <div class="h-4 bg-gray-200 rounded w-3/4"></div>
        </div>
      </div>
    </div>

    <div v-else-if="type === 'trend'" class="skeleton-trend">
      <!-- Trend chart area -->
      <div class="h-64 bg-gray-200 rounded"></div>
      <div class="flex justify-center mt-4 space-x-4">
        <div class="h-3 bg-gray-200 rounded w-20"></div>
        <div class="h-3 bg-gray-200 rounded w-20"></div>
        <div class="h-3 bg-gray-200 rounded w-20"></div>
        <div class="h-3 bg-gray-200 rounded w-20"></div>
      </div>
    </div>

    <div v-else-if="type === 'actions'" class="skeleton-actions">
      <!-- Quick actions grid -->
      <div class="grid grid-cols-3 gap-4">
        <div class="h-24 bg-gray-200 rounded"></div>
        <div class="h-24 bg-gray-200 rounded"></div>
        <div class="h-24 bg-gray-200 rounded"></div>
      </div>
    </div>

    <div v-else class="skeleton-default">
      <!-- Default skeleton -->
      <div class="space-y-4">
        <div class="h-4 bg-gray-200 rounded w-full"></div>
        <div class="h-4 bg-gray-200 rounded w-5/6"></div>
        <div class="h-4 bg-gray-200 rounded w-4/6"></div>
        <div class="h-32 bg-gray-200 rounded mt-6"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  export interface WidgetSkeletonProps {
    type?: 'profile' | 'chart' | 'stats' | 'trend' | 'actions' | 'default';
  }

  withDefaults(defineProps<WidgetSkeletonProps>(), {
    type: 'default',
  });
</script>

<style scoped>
  .widget-skeleton {
    min-height: 200px;
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
