<template>
  <div class="p-8 bg-gray-50 min-h-screen">
    <h1 class="text-2xl font-bold mb-6">DashboardHeader Component Examples</h1>

    <!-- Example 1: Basic Usage -->
    <section class="mb-8">
      <h2 class="text-xl font-semibold mb-4">1. Basic Usage</h2>
      <DashboardHeader
        title="仪表盘"
        :last-updated="new Date()"
        :loading="false"
        @refresh="handleRefresh"
      />
    </section>

    <!-- Example 2: Loading State -->
    <section class="mb-8">
      <h2 class="text-xl font-semibold mb-4">2. Loading State</h2>
      <DashboardHeader
        title="仪表盘"
        :last-updated="new Date()"
        :loading="true"
        @refresh="handleRefresh"
      />
    </section>

    <!-- Example 3: No Last Updated -->
    <section class="mb-8">
      <h2 class="text-xl font-semibold mb-4">3. No Last Updated Time</h2>
      <DashboardHeader
        title="仪表盘"
        :last-updated="null"
        :loading="false"
        @refresh="handleRefresh"
      />
    </section>

    <!-- Example 4: Custom Title -->
    <section class="mb-8">
      <h2 class="text-xl font-semibold mb-4">4. Custom Title</h2>
      <DashboardHeader
        title="测试管理平台"
        :last-updated="lastUpdatedTime"
        :loading="isRefreshing"
        @refresh="handleRefresh"
      />
    </section>

    <!-- Example 5: With Dashboard Store Integration -->
    <section class="mb-8">
      <h2 class="text-xl font-semibold mb-4">5. With Dashboard Store Integration</h2>
      <DashboardHeader
        title="数据概览"
        :last-updated="dashboardStore.lastUpdated"
        :loading="dashboardStore.loading"
        @refresh="refreshDashboard"
      />
      <div class="mt-4 p-4 bg-white rounded-lg shadow">
        <p class="text-sm text-gray-600">Store State:</p>
        <pre class="mt-2 text-xs">{{ JSON.stringify({
          loading: dashboardStore.loading,
          lastUpdated: dashboardStore.lastUpdated,
          hasData: dashboardStore.hasData
        }, null, 2) }}</pre>
      </div>
    </section>

    <!-- Refresh Log -->
    <section class="mb-8">
      <h2 class="text-xl font-semibold mb-4">Refresh Log</h2>
      <div class="bg-white rounded-lg shadow p-4">
        <div v-if="refreshLog.length === 0" class="text-gray-500 text-sm">
          No refresh events yet. Click a refresh button above.
        </div>
        <ul v-else class="space-y-2">
          <li
            v-for="(log, index) in refreshLog"
            :key="index"
            class="text-sm text-gray-700 border-b border-gray-200 pb-2"
          >
            <span class="font-semibold">{{ log.time }}</span>- {{ log.message }}
          </li>
        </ul>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
  import { ref } from 'vue';
  import { useDashboardStore } from '@/stores/dashboard';
  import DashboardHeader from './DashboardHeader.vue';

  // ============================================================================
  // State
  // ============================================================================

  const dashboardStore = useDashboardStore();
  const isRefreshing = ref(false);
  const lastUpdatedTime = ref(new Date());
  const refreshLog = ref<Array<{ time: string; message: string }>>([]);

  // ============================================================================
  // Methods
  // ============================================================================

  function handleRefresh(): void {
    const now = new Date();
    const timeString = now.toLocaleTimeString('zh-CN');

    refreshLog.value.unshift({
      time: timeString,
      message: 'Refresh button clicked',
    });

    // Simulate loading
    isRefreshing.value = true;
    setTimeout(() => {
      isRefreshing.value = false;
      lastUpdatedTime.value = new Date();
      refreshLog.value.unshift({
        time: new Date().toLocaleTimeString('zh-CN'),
        message: 'Refresh completed',
      });
    }, 2000);
  }

  async function refreshDashboard(): Promise<void> {
    const now = new Date();
    const timeString = now.toLocaleTimeString('zh-CN');

    refreshLog.value.unshift({
      time: timeString,
      message: 'Dashboard store refresh triggered',
    });

    try {
      await dashboardStore.refreshDashboard(false);
      refreshLog.value.unshift({
        time: new Date().toLocaleTimeString('zh-CN'),
        message: 'Dashboard store refresh completed',
      });
    } catch (error) {
      refreshLog.value.unshift({
        time: new Date().toLocaleTimeString('zh-CN'),
        message: `Dashboard store refresh failed: ${error}`,
      });
    }
  }
</script>
