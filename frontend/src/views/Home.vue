<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Skip to main content link for keyboard users -->
    <a 
      href="#main-content" 
      class="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-blue-600 focus:text-white focus:rounded-lg focus:shadow-lg"
    >
      {{ t('common.skipToMainContent') }}
    </a>

    <!-- Notification Container -->
    <NotificationContainer />

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8">
      <!-- Language Switcher (Top Right) -->
      <div class="flex justify-end mb-4">
        <LanguageSwitcher />
      </div>
      
      <!-- Dashboard Header -->
      <DashboardHeader
        :last-updated="dashboardStore.lastUpdated"
        :loading="dashboardStore.loading"
        @refresh="handleRefresh"
      />

      <!-- Loading State -->
      <LoadingState
        v-if="dashboardStore.loading && !dashboardStore.hasData"
        :full-dashboard="true"
        :show-loading-text="true"
        :loading-text="t('common.loadingData')"
      />

      <!-- Error State -->
      <ErrorState
        v-else-if="dashboardStore.isError && !dashboardStore.hasData"
        :title="t('error.loadFailed')"
        :message="dashboardStore.error || t('error.cannotLoadDashboard')"
        :show-retry="true"
        @retry="handleRetry"
      />

      <!-- Dashboard Content -->
      <main 
        v-else-if="dashboardStore.hasData" 
        id="main-content" 
        class="space-y-4 sm:space-y-6"
        role="main"
        :aria-label="t('dashboard.mainContent')"
      >
        <!-- User Profile Card -->
        <UserProfileCard
          v-if="dashboardStore.userData"
          :user="{
            id: dashboardStore.userData.id,
            username: dashboardStore.userData.username,
            avatar: dashboardStore.userData.avatar || undefined,
            registrationDate: dashboardStore.userData.registrationDate,
          }"
          :metrics="dashboardStore.userData.metrics"
        />

        <!-- Statistics Grid - Responsive: 1 col mobile, 2 cols tablet/desktop -->
        <div 
          class="statistics-grid grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6"
          role="group"
          :aria-label="t('dashboard.statisticsOverview')"
        >
          <!-- Steps Statistics Widget -->
          <StepsStatisticsWidget
            v-if="dashboardStore.statistics?.steps"
            :statistics="dashboardStore.statistics.steps"
            :title="t('steps.title')"
          />

          <!-- API Usage Widget -->
          <ApiUsageWidget
            v-if="dashboardStore.statistics?.apiUsage"
            :data="dashboardStore.statistics.apiUsage"
            :title="t('api.title')"
          />
        </div>

        <!-- Trend Analysis Widget (Full Width) -->
        <TrendAnalysisWidget
          v-if="dashboardStore.statistics?.trends"
          :data="dashboardStore.statistics.trends"
          :title="t('trend.title')"
        />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { onMounted, watch } from 'vue';
  import { useI18n } from 'vue-i18n';
  import {
    ApiUsageWidget,
    StepsStatisticsWidget,
    TrendAnalysisWidget,
  } from '@/components/business';
  // Import components
  import {
    DashboardHeader,
    ErrorState,
    LanguageSwitcher,
    LoadingState,
    NotificationContainer,
    UserProfileCard,
  } from '@/components/common';
  import { useNotification } from '@/composables/useNotification';
  import { usePerformanceMonitor } from '@/composables/usePerformanceMonitor';
  import { useWindowResize } from '@/composables/useWindowResize';
  import { useDashboardStore } from '@/stores/dashboard';

  // Setup i18n
  const { t } = useI18n();

  // Setup performance monitoring
  const { logMetrics } = usePerformanceMonitor('Home');

  // Setup window resize handling with debouncing
  useWindowResize({
    debounceDelay: 200,
    onResize: (size) => {
      if (import.meta.env.DEV) {
        console.log('[Dashboard] Window resized:', size);
      }
    },
  });

  // Initialize dashboard store
  const dashboardStore = useDashboardStore();
  const { error: notifyError, warning: notifyWarning, success: notifySuccess } = useNotification();

  /**
   * Handle dashboard refresh
   */
  async function handleRefresh(): Promise<void> {
    try {
      await dashboardStore.refreshDashboard(false); // Force fresh data
      notifySuccess(t('dashboard.dataRefreshed'));
    } catch (error) {
      console.error('Failed to refresh dashboard:', error);
      notifyError(dashboardStore.error || t('dashboard.refreshFailed'));
    }
  }

  /**
   * Handle retry after error
   */
  async function handleRetry(): Promise<void> {
    dashboardStore.clearError();
    dashboardStore.clearPartialErrors();
    await handleRefresh();
  }

  /**
   * Watch for partial errors and show warnings
   */
  watch(
    () => dashboardStore.partialErrors,
    newErrors => {
      if (Object.keys(newErrors).length > 0) {
        const errorMessages = Object.values(newErrors);
        notifyWarning(`${t('dashboard.partialLoadFailed')}: ${errorMessages.join(', ')}`);
      }
    },
    { deep: true },
  );

  /**
   * Load dashboard data on component mount
   * Check cache first, then fetch fresh data if needed
   */
  onMounted(async () => {
    try {
      // Try to use cached data first (will fetch if cache is invalid)
      await dashboardStore.refreshDashboard(true);

      // Show success message if data loaded from cache
      if (dashboardStore.lastUpdated) {
        const cacheAge = Date.now() - dashboardStore.lastUpdated.getTime();
        if (cacheAge < 1000) {
          // Fresh data
          notifySuccess(t('dashboard.dataLoaded'));
        }
      }

      // Log performance metrics in development
      if (import.meta.env.DEV) {
        logMetrics();
      }
    } catch (error) {
      console.error('Failed to load dashboard:', error);
      // Error is already set in the store and will be displayed
    }
  });
</script>

<style scoped>
  /* Responsive grid adjustments */
  .statistics-grid {
    display: grid;
    gap: 1.5rem;
  }

  /* Mobile: 1 column */
  @media (max-width: 767px) {
    .statistics-grid {
      grid-template-columns: 1fr;
      gap: 1rem;
    }
  }

  /* Tablet and Desktop: 2 columns */
  @media (min-width: 768px) {
    .statistics-grid {
      grid-template-columns: repeat(2, 1fr);
      gap: 1.5rem;
    }
  }
</style>
