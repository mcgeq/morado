<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-6">Test Reports Dashboard</h1>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <div class="rounded-lg border bg-white p-6 shadow-sm">
        <div class="text-sm text-gray-500 mb-1">Total Tests</div>
        <div class="text-3xl font-bold">{{ stats.totalTests }}</div>
      </div>
      <div class="rounded-lg border bg-white p-6 shadow-sm">
        <div class="text-sm text-gray-500 mb-1">Passed</div>
        <div class="text-3xl font-bold text-green-600">{{ stats.passed }}</div>
      </div>
      <div class="rounded-lg border bg-white p-6 shadow-sm">
        <div class="text-sm text-gray-500 mb-1">Failed</div>
        <div class="text-3xl font-bold text-red-600">{{ stats.failed }}</div>
      </div>
      <div class="rounded-lg border bg-white p-6 shadow-sm">
        <div class="text-sm text-gray-500 mb-1">Success Rate</div>
        <div class="text-3xl font-bold text-blue-600">{{ stats.successRate }}%</div>
      </div>
    </div>

    <!-- Recent Executions -->
    <div class="rounded-lg border bg-white p-6 shadow-sm mb-8">
      <h2 class="text-xl font-semibold mb-4">Recent Test Executions</h2>

      <div v-if="recentExecutions.length === 0" class="text-center py-8 text-gray-500">
        No test executions yet
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="execution in recentExecutions"
          :key="execution.id"
          class="flex items-center justify-between p-4 rounded-lg border"
        >
          <div class="flex-1">
            <div class="font-medium">{{ execution.name }}</div>
            <div class="text-sm text-gray-500">
              {{ new Date(execution.executedAt).toLocaleString() }}
            </div>
          </div>
          <div class="flex items-center gap-4">
            <span class="text-sm text-gray-500">{{ execution.duration }}ms</span>
            <span
              :class="[
                'rounded-full px-3 py-1 text-sm font-semibold',
                execution.status === 'passed'
                  ? 'bg-green-100 text-green-700'
                  : execution.status === 'failed'
                  ? 'bg-red-100 text-red-700'
                  : 'bg-yellow-100 text-yellow-700',
              ]"
            >
              {{ execution.status }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Test Trends Chart Placeholder -->
    <div class="rounded-lg border bg-white p-6 shadow-sm">
      <h2 class="text-xl font-semibold mb-4">Test Execution Trends</h2>
      <div class="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
        <p class="text-gray-500">Chart visualization would go here</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { onMounted, ref } from 'vue';

  const stats = ref({
    totalTests: 0,
    passed: 0,
    failed: 0,
    successRate: 0,
  });

  const recentExecutions = ref<any[]>([]);

  onMounted(async () => {
    // Placeholder - would fetch from API
    stats.value = {
      totalTests: 150,
      passed: 135,
      failed: 15,
      successRate: 90,
    };

    recentExecutions.value = [
      {
        id: 1,
        name: 'User Login Test',
        status: 'passed',
        duration: 1250,
        executedAt: new Date().toISOString(),
      },
      {
        id: 2,
        name: 'API Integration Test',
        status: 'failed',
        duration: 3400,
        executedAt: new Date(Date.now() - 3600000).toISOString(),
      },
      {
        id: 3,
        name: 'Database Connection Test',
        status: 'passed',
        duration: 850,
        executedAt: new Date(Date.now() - 7200000).toISOString(),
      },
    ];
  });
</script>
