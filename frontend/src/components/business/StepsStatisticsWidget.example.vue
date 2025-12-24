<template>
  <div class="example-container p-8 bg-gray-50 min-h-screen">
    <h1 class="text-3xl font-bold mb-8 text-gray-900">StepsStatisticsWidget Examples</h1>

    <div class="examples-grid grid grid-cols-1 lg:grid-cols-2 gap-8">
      <!-- Example 1: Normal Data -->
      <div class="example-card">
        <h2 class="text-xl font-semibold mb-4 text-gray-800">Normal Data</h2>
        <StepsStatisticsWidget :statistics="normalStatistics" />
      </div>

      <!-- Example 2: Mostly Completed -->
      <div class="example-card">
        <h2 class="text-xl font-semibold mb-4 text-gray-800">Mostly Completed</h2>
        <StepsStatisticsWidget :statistics="mostlyCompletedStatistics" title="高完成率统计" />
      </div>

      <!-- Example 3: High Failure Rate -->
      <div class="example-card">
        <h2 class="text-xl font-semibold mb-4 text-gray-800">High Failure Rate</h2>
        <StepsStatisticsWidget :statistics="highFailureStatistics" title="高失败率统计" />
      </div>

      <!-- Example 4: Empty State -->
      <div class="example-card">
        <h2 class="text-xl font-semibold mb-4 text-gray-800">Empty State</h2>
        <StepsStatisticsWidget :statistics="emptyStatistics" />
      </div>

      <!-- Example 5: Equal Distribution -->
      <div class="example-card">
        <h2 class="text-xl font-semibold mb-4 text-gray-800">Equal Distribution</h2>
        <StepsStatisticsWidget :statistics="equalStatistics" title="均衡分布统计" />
      </div>

      <!-- Example 6: Large Numbers -->
      <div class="example-card">
        <h2 class="text-xl font-semibold mb-4 text-gray-800">Large Numbers</h2>
        <StepsStatisticsWidget :statistics="largeNumbersStatistics" title="大数据量统计" />
      </div>
    </div>

    <!-- Interactive Example -->
    <div class="interactive-example mt-12 bg-white rounded-lg shadow-lg p-8">
      <h2 class="text-2xl font-semibold mb-6 text-gray-800">Interactive Example</h2>

      <div class="controls grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            已完成: {{ interactiveStats.completed }}
          </label>
          <input
            v-model.number="interactiveStats.completed"
            type="range"
            min="0"
            max="1000"
            class="w-full"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            SQL执行失败: {{ interactiveStats.sqlFailed }}
          </label>
          <input
            v-model.number="interactiveStats.sqlFailed"
            type="range"
            min="0"
            max="1000"
            class="w-full"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            API请求: {{ interactiveStats.apiRequest }}
          </label>
          <input
            v-model.number="interactiveStats.apiRequest"
            type="range"
            min="0"
            max="1000"
            class="w-full"
          />
        </div>
      </div>

      <StepsStatisticsWidget :statistics="interactiveStats" title="交互式统计" />
    </div>
  </div>
</template>

<script setup lang="ts">
  import { reactive } from 'vue';
  import type { StepStatistics } from '@/types/dashboard';
  import StepsStatisticsWidget from './StepsStatisticsWidget.vue';

  // Example 1: Normal data with mixed values
  const normalStatistics: StepStatistics = {
    completed: 150,
    sqlFailed: 30,
    apiRequest: 70,
  };

  // Example 2: Mostly completed
  const mostlyCompletedStatistics: StepStatistics = {
    completed: 450,
    sqlFailed: 25,
    apiRequest: 25,
  };

  // Example 3: High failure rate
  const highFailureStatistics: StepStatistics = {
    completed: 50,
    sqlFailed: 200,
    apiRequest: 100,
  };

  // Example 4: Empty state
  const emptyStatistics: StepStatistics = {
    completed: 0,
    sqlFailed: 0,
    apiRequest: 0,
  };

  // Example 5: Equal distribution
  const equalStatistics: StepStatistics = {
    completed: 100,
    sqlFailed: 100,
    apiRequest: 100,
  };

  // Example 6: Large numbers
  const largeNumbersStatistics: StepStatistics = {
    completed: 5420,
    sqlFailed: 1230,
    apiRequest: 3890,
  };

  // Interactive example
  const interactiveStats = reactive<StepStatistics>({
    completed: 200,
    sqlFailed: 50,
    apiRequest: 100,
  });
</script>

<style scoped>
  .example-card {
    background: white;
    border-radius: 0.5rem;
    padding: 1.5rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  }

  input[type="range"] {
    accent-color: #3b82f6;
  }
</style>
