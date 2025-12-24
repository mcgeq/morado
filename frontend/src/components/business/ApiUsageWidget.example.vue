<template>
  <div class="example-container p-8 bg-gray-50 min-h-screen">
    <h1 class="text-3xl font-bold mb-8 text-gray-900">ApiUsageWidget Examples</h1>

    <!-- Example 1: Normal Usage -->
    <section class="example-section mb-8">
      <h2 class="text-xl font-semibold mb-4 text-gray-800">Example 1: Normal Usage</h2>
      <div class="max-w-4xl">
        <ApiUsageWidget :data="normalData" />
      </div>
    </section>

    <!-- Example 2: High Completion Rates -->
    <section class="example-section mb-8">
      <h2 class="text-xl font-semibold mb-4 text-gray-800">Example 2: High Completion Rates</h2>
      <div class="max-w-4xl">
        <ApiUsageWidget :data="highCompletionData" title="高完成度示例" />
      </div>
    </section>

    <!-- Example 3: Low Completion Rates -->
    <section class="example-section mb-8">
      <h2 class="text-xl font-semibold mb-4 text-gray-800">Example 3: Low Completion Rates</h2>
      <div class="max-w-4xl">
        <ApiUsageWidget :data="lowCompletionData" title="低完成度示例" />
      </div>
    </section>

    <!-- Example 4: Zero Data -->
    <section class="example-section mb-8">
      <h2 class="text-xl font-semibold mb-4 text-gray-800">Example 4: Zero Data</h2>
      <div class="max-w-4xl">
        <ApiUsageWidget :data="zeroData" title="无数据示例" />
      </div>
    </section>

    <!-- Example 5: Mixed Performance -->
    <section class="example-section mb-8">
      <h2 class="text-xl font-semibold mb-4 text-gray-800">Example 5: Mixed Performance</h2>
      <div class="max-w-4xl">
        <ApiUsageWidget :data="mixedData" title="混合性能示例" />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
  import type { ApiUsageData } from '@/types/dashboard';
  import ApiUsageWidget from './ApiUsageWidget.vue';

  // Example 1: Normal usage with moderate completion rates
  const normalData: ApiUsageData = {
    apiCompletion: {
      percentage: 65,
      totalApis: 150,
      completedApis: 98,
      taggedApis: 85,
    },
    testCaseCompletion: {
      percentage: 72,
      totalTestCases: 250,
      passedTestCases: 180,
      taggedTestCases: 165,
    },
  };

  // Example 2: High completion rates (green indicators)
  const highCompletionData: ApiUsageData = {
    apiCompletion: {
      percentage: 92,
      totalApis: 200,
      completedApis: 184,
      taggedApis: 175,
    },
    testCaseCompletion: {
      percentage: 88,
      totalTestCases: 300,
      passedTestCases: 264,
      taggedTestCases: 250,
    },
  };

  // Example 3: Low completion rates (red indicators)
  const lowCompletionData: ApiUsageData = {
    apiCompletion: {
      percentage: 25,
      totalApis: 100,
      completedApis: 25,
      taggedApis: 15,
    },
    testCaseCompletion: {
      percentage: 30,
      totalTestCases: 150,
      passedTestCases: 45,
      taggedTestCases: 30,
    },
  };

  // Example 4: Zero data
  const zeroData: ApiUsageData = {
    apiCompletion: {
      percentage: 0,
      totalApis: 0,
      completedApis: 0,
      taggedApis: 0,
    },
    testCaseCompletion: {
      percentage: 0,
      totalTestCases: 0,
      passedTestCases: 0,
      taggedTestCases: 0,
    },
  };

  // Example 5: Mixed performance (yellow indicators)
  const mixedData: ApiUsageData = {
    apiCompletion: {
      percentage: 55,
      totalApis: 180,
      completedApis: 99,
      taggedApis: 75,
    },
    testCaseCompletion: {
      percentage: 48,
      totalTestCases: 220,
      passedTestCases: 106,
      taggedTestCases: 88,
    },
  };
</script>

<style scoped>
  .example-container {
    font-family:
      -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  }

  .example-section {
    background: white;
    padding: 2rem;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
</style>
