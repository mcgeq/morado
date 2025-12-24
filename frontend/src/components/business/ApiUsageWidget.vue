<template>
  <section 
    class="widget widget-hoverable" 
    role="region" 
    aria-labelledby="api-usage-title"
    aria-describedby="api-usage-description"
  >
    <!-- Widget Header -->
    <div class="widget-header">
      <h3 id="api-usage-title" class="widget-title">{{ title || 'API使用情况' }}</h3>
      <span id="api-usage-description" class="sr-only">
        API和测试用例的完成度统计，包括总数、完成数和通过打标数量
      </span>
    </div>

    <!-- Error State -->
    <div
      v-if="!isValidData"
      class="error-state flex flex-col items-center justify-center py-12"
      role="alert"
      aria-live="assertive"
    >
      <svg
        class="w-16 h-16 text-red-300 mb-4"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <p class="text-gray-500 text-sm">数据格式无效</p>
    </div>

    <!-- Two-Column Layout - Responsive: stacked on mobile, side-by-side on tablet+ -->
    <div v-else class="usage-grid grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8">
      <!-- API Completion Section -->
      <section class="completion-section" aria-labelledby="api-completion-heading">
        <div class="section-header mb-4">
          <h4 id="api-completion-heading" class="text-sm font-medium text-gray-600 mb-2">API完成度</h4>
          <div class="percentage-display">
            <span
              class="text-3xl md:text-4xl font-bold text-blue-600"
              data-testid="api-completion-percentage"
              role="status"
              :aria-label="`API完成度${data.apiCompletion.percentage}百分比`"
            >
              {{ data.apiCompletion.percentage }}%
            </span>
          </div>
        </div>

        <!-- API Metrics List -->
        <dl class="metrics-list space-y-3 mt-6" aria-label="API指标详情">
          <div class="metric-item flex items-center justify-between">
            <dt class="metric-label text-sm text-gray-600">用例管理API总数</dt>
            <dd class="metric-value text-sm font-semibold text-gray-900" data-testid="total-apis">
              {{ data.apiCompletion.totalApis }}
            </dd>
          </div>
          <div class="metric-item flex items-center justify-between">
            <dt class="metric-label text-sm text-gray-600">API总数</dt>
            <dd
              class="metric-value text-sm font-semibold text-gray-900"
              data-testid="completed-apis"
            >
              {{ data.apiCompletion.completedApis }}
            </dd>
          </div>
          <div class="metric-item flex items-center justify-between">
            <dt class="metric-label text-sm text-gray-600">API通过打标数量</dt>
            <dd class="flex items-center">
              <span
                class="w-2 h-2 rounded-full mr-2"
                :class="getIndicatorColor(data.apiCompletion.taggedApis, data.apiCompletion.totalApis)"
                role="img"
                :aria-label="getIndicatorAriaLabel(data.apiCompletion.taggedApis, data.apiCompletion.totalApis)"
              />
              <span
                class="metric-value text-sm font-semibold text-gray-900"
                data-testid="tagged-apis"
              >
                {{ data.apiCompletion.taggedApis }}
              </span>
            </dd>
          </div>
        </dl>
      </section>

      <!-- Divider - Hidden on mobile, visible on tablet+ -->
      <div class="divider-line hidden md:block absolute left-1/2 top-0 bottom-0 w-px bg-gray-200" aria-hidden="true" />

      <!-- Test Case Completion Section -->
      <section class="completion-section" aria-labelledby="testcase-completion-heading">
        <div class="section-header mb-4">
          <h4 id="testcase-completion-heading" class="text-sm font-medium text-gray-600 mb-2">用例完成度</h4>
          <div class="percentage-display">
            <span
              class="text-3xl md:text-4xl font-bold text-green-600"
              data-testid="testcase-completion-percentage"
              role="status"
              :aria-label="`用例完成度${data.testCaseCompletion.percentage}百分比`"
            >
              {{ data.testCaseCompletion.percentage }}%
            </span>
          </div>
        </div>

        <!-- Test Case Metrics List -->
        <dl class="metrics-list space-y-3 mt-6" aria-label="测试用例指标详情">
          <div class="metric-item flex items-center justify-between">
            <dt class="metric-label text-sm text-gray-600">用例总数</dt>
            <dd
              class="metric-value text-sm font-semibold text-gray-900"
              data-testid="total-testcases"
            >
              {{ data.testCaseCompletion.totalTestCases }}
            </dd>
          </div>
          <div class="metric-item flex items-center justify-between">
            <dt class="metric-label text-sm text-gray-600">测试通过打标数量</dt>
            <dd class="flex items-center">
              <span
                class="w-2 h-2 rounded-full mr-2"
                :class="getIndicatorColor(data.testCaseCompletion.passedTestCases, data.testCaseCompletion.totalTestCases)"
                role="img"
                :aria-label="getIndicatorAriaLabel(data.testCaseCompletion.passedTestCases, data.testCaseCompletion.totalTestCases)"
              />
              <span
                class="metric-value text-sm font-semibold text-gray-900"
                data-testid="passed-testcases"
              >
                {{ data.testCaseCompletion.passedTestCases }}
              </span>
            </dd>
          </div>
          <div class="metric-item flex items-center justify-between">
            <dt class="metric-label text-sm text-gray-600">测试通过打标数量</dt>
            <dd class="flex items-center">
              <span
                class="w-2 h-2 rounded-full mr-2"
                :class="getIndicatorColor(data.testCaseCompletion.taggedTestCases, data.testCaseCompletion.totalTestCases)"
                role="img"
                :aria-label="getIndicatorAriaLabel(data.testCaseCompletion.taggedTestCases, data.testCaseCompletion.totalTestCases)"
              />
              <span
                class="metric-value text-sm font-semibold text-gray-900"
                data-testid="tagged-testcases"
              >
                {{ data.testCaseCompletion.taggedTestCases }}
              </span>
            </dd>
          </div>
        </dl>
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
  import { computed } from 'vue';
  import type { ApiUsageWidgetProps } from '@/types/dashboard';
  import {
    validateNonNegativeNumber,
    validatePercentage,
  } from '@/utils/propValidation';

  const props = withDefaults(defineProps<ApiUsageWidgetProps>(), {
    title: '',
  });

  // Runtime prop validation in development
  if (import.meta.env.DEV) {
    if (!props.data) {
      console.error('[ApiUsageWidget] data prop is required');
    } else {
      // Validate apiCompletion
      if (!props.data.apiCompletion) {
        console.error('[ApiUsageWidget] data.apiCompletion is required');
      } else {
        validatePercentage(props.data.apiCompletion.percentage, 'data.apiCompletion.percentage');
        validateNonNegativeNumber(props.data.apiCompletion.totalApis, 'data.apiCompletion.totalApis');
        validateNonNegativeNumber(props.data.apiCompletion.completedApis, 'data.apiCompletion.completedApis');
        validateNonNegativeNumber(props.data.apiCompletion.taggedApis, 'data.apiCompletion.taggedApis');
      }

      // Validate testCaseCompletion
      if (!props.data.testCaseCompletion) {
        console.error('[ApiUsageWidget] data.testCaseCompletion is required');
      } else {
        validatePercentage(props.data.testCaseCompletion.percentage, 'data.testCaseCompletion.percentage');
        validateNonNegativeNumber(props.data.testCaseCompletion.totalTestCases, 'data.testCaseCompletion.totalTestCases');
        validateNonNegativeNumber(props.data.testCaseCompletion.passedTestCases, 'data.testCaseCompletion.passedTestCases');
        validateNonNegativeNumber(props.data.testCaseCompletion.taggedTestCases, 'data.testCaseCompletion.taggedTestCases');
      }
    }
  }

  // Validate data
  const isValidData = computed(() => {
    if (!props.data) return false;

    const { apiCompletion, testCaseCompletion } = props.data;

    const isValidCompletion = (completion: any) =>
      completion &&
      typeof completion.percentage === 'number' &&
      typeof completion.totalApis === 'number' &&
      typeof completion.completedApis === 'number' &&
      typeof completion.taggedApis === 'number' &&
      !Number.isNaN(completion.percentage) &&
      !Number.isNaN(completion.totalApis) &&
      !Number.isNaN(completion.completedApis) &&
      !Number.isNaN(completion.taggedApis) &&
      completion.percentage >= 0 &&
      completion.percentage <= 100;

    const isValidTestCase = (testCase: any) =>
      testCase &&
      typeof testCase.percentage === 'number' &&
      typeof testCase.totalTestCases === 'number' &&
      typeof testCase.passedTestCases === 'number' &&
      typeof testCase.taggedTestCases === 'number' &&
      !Number.isNaN(testCase.percentage) &&
      !Number.isNaN(testCase.totalTestCases) &&
      !Number.isNaN(testCase.passedTestCases) &&
      !Number.isNaN(testCase.taggedTestCases) &&
      testCase.percentage >= 0 &&
      testCase.percentage <= 100;

    return isValidCompletion(apiCompletion) && isValidTestCase(testCaseCompletion);
  });

  /**
   * Get color indicator class based on value ratio
   * Green if value is high relative to total, red if low
   */
  function getIndicatorColor(value: number, total: number): string {
    if (!isValidData.value || total === 0) return 'bg-gray-400';

    const ratio = value / total;

    if (ratio >= 0.7) {
      return 'bg-green-500'; // Green for good performance (70%+)
    }
    if (ratio >= 0.4) {
      return 'bg-yellow-500'; // Yellow for moderate performance (40-70%)
    }
    return 'bg-red-500'; // Red for poor performance (<40%)
  }

  /**
   * Get accessible label for indicator color
   */
  function getIndicatorAriaLabel(value: number, total: number): string {
    if (!isValidData.value || total === 0) return '状态指示器：无数据';

    const ratio = value / total;
    const percentage = Math.round(ratio * 100);

    if (ratio >= 0.7) {
      return `状态指示器：良好，${percentage}%`;
    }
    if (ratio >= 0.4) {
      return `状态指示器：中等，${percentage}%`;
    }
    return `状态指示器：较低，${percentage}%`;
  }
</script>

<style scoped>
  /* Widget-specific styles using design system */
  .widget {
    min-height: 300px;
    position: relative;
  }

  .usage-grid {
    position: relative;
  }

  .completion-section {
    padding: 0 1rem;
  }

  .percentage-display {
    margin-top: 0.5rem;
  }

  .metric-item {
    padding: 0.5rem 0;
    border-bottom: 1px solid #f3f4f6;
  }

  .metric-item:last-child {
    border-bottom: none;
  }

  .divider-line {
    transform: translateX(-50%);
  }

  /* Mobile responsive adjustments */
  @media (max-width: 767px) {
    .completion-section {
      padding: 0;
    }

    .completion-section:first-child {
      padding-bottom: 1.5rem;
      margin-bottom: 1.5rem;
      border-bottom: 1px solid #e5e7eb;
    }

    .usage-grid {
      gap: 0;
    }
  }
</style>
