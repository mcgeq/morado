<template>
  <div class="examples-container p-8 space-y-8 bg-gray-50">
    <h1 class="text-3xl font-bold text-gray-900 mb-8">TrendAnalysisWidget Examples</h1>

    <!-- Example 1: Basic Usage -->
    <section class="example-section">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">1. Basic Usage</h2>
      <p class="text-gray-600 mb-4">
        Default trend analysis widget with sample data showing all four component types over a week.
      </p>
      <TrendAnalysisWidget :data="basicTrendData" />
    </section>

    <!-- Example 2: Custom Title -->
    <section class="example-section">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">2. Custom Title</h2>
      <p class="text-gray-600 mb-4">Widget with a custom title instead of the default.</p>
      <TrendAnalysisWidget :data="basicTrendData" title="组件趋势分析" />
    </section>

    <!-- Example 3: With Date Range -->
    <section class="example-section">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">3. With Date Range Display</h2>
      <p class="text-gray-600 mb-4">Widget displaying the date range of the data.</p>
      <TrendAnalysisWidget
        :data="basicTrendData"
        :date-range="{ start: '2024-01-01', end: '2024-01-07' }"
      />
    </section>

    <!-- Example 4: Empty State -->
    <section class="example-section">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">4. Empty State</h2>
      <p class="text-gray-600 mb-4">Widget with no data showing the empty state.</p>
      <TrendAnalysisWidget :data="[]" />
    </section>

    <!-- Example 5: Data with Zero Values -->
    <section class="example-section">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">5. Data with Zero Values</h2>
      <p class="text-gray-600 mb-4">
        Widget handling zero values without creating gaps in the chart.
      </p>
      <TrendAnalysisWidget :data="dataWithZeros" />
    </section>

    <!-- Example 6: Longer Time Period -->
    <section class="example-section">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">6. Longer Time Period (30 Days)</h2>
      <p class="text-gray-600 mb-4">
        Widget showing trends over a longer period with more data points.
      </p>
      <TrendAnalysisWidget
        :data="longPeriodData"
        :date-range="{ start: '2024-01-01', end: '2024-01-30' }"
      />
    </section>

    <!-- Example 7: Increasing Trend -->
    <section class="example-section">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">7. Increasing Trend</h2>
      <p class="text-gray-600 mb-4">Widget showing an upward trend in all components.</p>
      <TrendAnalysisWidget :data="increasingTrendData" />
    </section>

    <!-- Example 8: Mixed Trends -->
    <section class="example-section">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">8. Mixed Trends</h2>
      <p class="text-gray-600 mb-4">
        Widget showing different trends for different component types.
      </p>
      <TrendAnalysisWidget :data="mixedTrendData" />
    </section>
  </div>
</template>

<script setup lang="ts">
  import type { TrendDataPoint } from '@/types/dashboard';
  import TrendAnalysisWidget from './TrendAnalysisWidget.vue';

  // Example 1: Basic trend data
  const basicTrendData: TrendDataPoint[] = [
    {
      date: '2024-01-01',
      scheduledComponents: 10,
      testCaseComponents: 20,
      actualComponents: 15,
      detectionComponents: 5,
    },
    {
      date: '2024-01-02',
      scheduledComponents: 12,
      testCaseComponents: 22,
      actualComponents: 18,
      detectionComponents: 7,
    },
    {
      date: '2024-01-03',
      scheduledComponents: 8,
      testCaseComponents: 18,
      actualComponents: 12,
      detectionComponents: 4,
    },
    {
      date: '2024-01-04',
      scheduledComponents: 15,
      testCaseComponents: 25,
      actualComponents: 20,
      detectionComponents: 8,
    },
    {
      date: '2024-01-05',
      scheduledComponents: 11,
      testCaseComponents: 21,
      actualComponents: 16,
      detectionComponents: 6,
    },
    {
      date: '2024-01-06',
      scheduledComponents: 13,
      testCaseComponents: 23,
      actualComponents: 19,
      detectionComponents: 7,
    },
    {
      date: '2024-01-07',
      scheduledComponents: 14,
      testCaseComponents: 24,
      actualComponents: 21,
      detectionComponents: 9,
    },
  ];

  // Example 5: Data with zero values
  const dataWithZeros: TrendDataPoint[] = [
    {
      date: '2024-01-01',
      scheduledComponents: 10,
      testCaseComponents: 0,
      actualComponents: 15,
      detectionComponents: 0,
    },
    {
      date: '2024-01-02',
      scheduledComponents: 0,
      testCaseComponents: 22,
      actualComponents: 0,
      detectionComponents: 7,
    },
    {
      date: '2024-01-03',
      scheduledComponents: 8,
      testCaseComponents: 0,
      actualComponents: 12,
      detectionComponents: 0,
    },
    {
      date: '2024-01-04',
      scheduledComponents: 0,
      testCaseComponents: 25,
      actualComponents: 0,
      detectionComponents: 8,
    },
    {
      date: '2024-01-05',
      scheduledComponents: 11,
      testCaseComponents: 21,
      actualComponents: 16,
      detectionComponents: 6,
    },
  ];

  // Example 6: Longer period data (30 days)
  const longPeriodData: TrendDataPoint[] = Array.from({ length: 30 }, (_, i) => ({
    date: `2024-01-${String(i + 1).padStart(2, '0')}`,
    scheduledComponents: Math.floor(Math.random() * 20) + 5,
    testCaseComponents: Math.floor(Math.random() * 30) + 10,
    actualComponents: Math.floor(Math.random() * 25) + 8,
    detectionComponents: Math.floor(Math.random() * 15) + 2,
  }));

  // Example 7: Increasing trend
  const increasingTrendData: TrendDataPoint[] = Array.from({ length: 7 }, (_, i) => ({
    date: `2024-01-${String(i + 1).padStart(2, '0')}`,
    scheduledComponents: 5 + i * 2,
    testCaseComponents: 10 + i * 3,
    actualComponents: 8 + i * 2,
    detectionComponents: 3 + i,
  }));

  // Example 8: Mixed trends
  const mixedTrendData: TrendDataPoint[] = [
    {
      date: '2024-01-01',
      scheduledComponents: 10,
      testCaseComponents: 20,
      actualComponents: 15,
      detectionComponents: 5,
    },
    {
      date: '2024-01-02',
      scheduledComponents: 12,
      testCaseComponents: 18,
      actualComponents: 17,
      detectionComponents: 7,
    },
    {
      date: '2024-01-03',
      scheduledComponents: 8,
      testCaseComponents: 22,
      actualComponents: 14,
      detectionComponents: 9,
    },
    {
      date: '2024-01-04',
      scheduledComponents: 15,
      testCaseComponents: 19,
      actualComponents: 20,
      detectionComponents: 6,
    },
    {
      date: '2024-01-05',
      scheduledComponents: 11,
      testCaseComponents: 25,
      actualComponents: 16,
      detectionComponents: 8,
    },
    {
      date: '2024-01-06',
      scheduledComponents: 13,
      testCaseComponents: 21,
      actualComponents: 19,
      detectionComponents: 5,
    },
    {
      date: '2024-01-07',
      scheduledComponents: 14,
      testCaseComponents: 23,
      actualComponents: 21,
      detectionComponents: 10,
    },
  ];
</script>

<style scoped>
  .examples-container {
    max-width: 1200px;
    margin: 0 auto;
  }

  .example-section {
    background: white;
    padding: 1.5rem;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
</style>
