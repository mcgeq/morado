<template>
  <section 
    class="widget widget-hoverable" 
    role="region" 
    aria-labelledby="steps-stats-title"
    aria-describedby="steps-stats-description"
  >
    <!-- Widget Header -->
    <div class="widget-header">
      <h3 id="steps-stats-title" class="widget-title">{{ title || 'Steps统计' }}</h3>
      <span id="steps-stats-description" class="sr-only">
        测试步骤执行统计，包括已完成、SQL执行失败和API请求的数量分布
      </span>
    </div>

    <!-- Empty State -->
    <div
      v-if="total === 0"
      class="empty-state flex flex-col items-center justify-center py-12"
      data-testid="empty-state"
      role="status"
      aria-live="polite"
    >
      <svg
        class="w-16 h-16 text-gray-300 mb-4"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
        />
      </svg>
      <p class="text-gray-500 text-sm">暂无数据</p>
    </div>

    <!-- Chart and Legend -->
    <div v-else class="chart-container flex flex-col md:flex-row items-center justify-between">
      <!-- Donut Chart -->
      <div class="chart-wrapper flex-shrink-0 mb-6 md:mb-0" role="img" :aria-label="chartAriaLabel">
        <DonutChart :datasets="chartDatasets" :show-legend="false" size="md" />
        <!-- Screen reader text for chart data -->
        <span class="sr-only">
          步骤统计图表：已完成 {{ statistics.completed }} 个（{{ calculatePercentage(statistics.completed) }}%），
          SQL执行失败 {{ statistics.sqlFailed }} 个（{{ calculatePercentage(statistics.sqlFailed) }}%），
          API请求 {{ statistics.apiRequest }} 个（{{ calculatePercentage(statistics.apiRequest) }}%），
          总计 {{ total }} 个步骤
        </span>
      </div>

      <!-- Legend with Counts -->
      <div class="legend-container flex-1 md:ml-8 w-full md:w-auto" role="list" aria-label="步骤统计详情">
        <div class="legend-items space-y-4">
          <div
            v-for="item in legendItems"
            :key="item.label"
            class="legend-item flex items-center justify-between"
            role="listitem"
          >
            <div class="flex items-center">
              <span
                class="legend-color w-3 h-3 rounded-full mr-3"
                :style="{ backgroundColor: item.color }"
                :aria-label="`${item.label}颜色指示器`"
                role="img"
              />
              <span class="legend-label text-sm text-gray-700"> {{ item.label }} </span>
            </div>
            <div class="legend-value flex items-center">
              <span class="text-sm font-semibold text-gray-900 mr-2" :aria-label="`${item.label}数量`"> 
                {{ item.value }} 
              </span>
              <span class="text-xs text-gray-500" :aria-label="`占比${item.percentage}百分比`"> 
                ({{ item.percentage }}%) 
              </span>
            </div>
          </div>
        </div>

        <!-- Total -->
        <div class="total-section mt-6 pt-4 border-t border-gray-200">
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium text-gray-700">总计</span>
            <span class="text-lg font-bold text-gray-900" aria-label="总步骤数">{{ total }}</span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
  import { computed } from 'vue';
  import { useI18n } from 'vue-i18n';
  import DonutChart from '@/components/common/DonutChart.vue';
  import type { ChartDataset, StepsStatisticsWidgetProps } from '@/types/dashboard';
  import { validateNonNegativeNumber } from '@/utils/propValidation';

  const props = withDefaults(defineProps<StepsStatisticsWidgetProps>(), {
    title: '',
  });
  
  const { t } = useI18n();

  // Runtime prop validation in development
  if (import.meta.env.DEV) {
    if (!props.statistics) {
      console.error('[StepsStatisticsWidget] statistics prop is required');
    } else {
      validateNonNegativeNumber(props.statistics.completed, 'statistics.completed');
      validateNonNegativeNumber(props.statistics.sqlFailed, 'statistics.sqlFailed');
      validateNonNegativeNumber(props.statistics.apiRequest, 'statistics.apiRequest');
    }
  }

  // Color scheme as per design document
  const COLORS = {
    completed: '#3B82F6', // Blue
    sqlFailed: '#F59E0B', // Orange
    apiRequest: '#8B5CF6', // Purple
  };

  // Validate statistics data
  const isValidData = computed(() => {
    if (!props.statistics) return false;

    const { completed, sqlFailed, apiRequest } = props.statistics;

    return (
      typeof completed === 'number' &&
      typeof sqlFailed === 'number' &&
      typeof apiRequest === 'number' &&
      !Number.isNaN(completed) &&
      !Number.isNaN(sqlFailed) &&
      !Number.isNaN(apiRequest) &&
      completed >= 0 &&
      sqlFailed >= 0 &&
      apiRequest >= 0
    );
  });

  // Calculate total
  const total = computed(() => {
    if (!isValidData.value) return 0;
    return props.statistics.completed + props.statistics.sqlFailed + props.statistics.apiRequest;
  });

  // Calculate percentage for each category
  const calculatePercentage = (value: number): number => {
    if (total.value === 0) return 0;
    return Math.round((value / total.value) * 100);
  };

  // Transform statistics to chart datasets
  const chartDatasets = computed<ChartDataset[]>(() => {
    if (!isValidData.value) return [];

    return [
      {
        label: '已完成',
        value: props.statistics.completed,
        color: COLORS.completed,
      },
      {
        label: 'SQL执行失败',
        value: props.statistics.sqlFailed,
        color: COLORS.sqlFailed,
      },
      {
        label: 'API请求',
        value: props.statistics.apiRequest,
        color: COLORS.apiRequest,
      },
    ];
  });

  // Legend items with percentages
  const legendItems = computed(() => {
    if (!isValidData.value) return [];

    return [
      {
        label: '已完成',
        value: props.statistics.completed,
        percentage: calculatePercentage(props.statistics.completed),
        color: COLORS.completed,
      },
      {
        label: 'SQL执行失败',
        value: props.statistics.sqlFailed,
        percentage: calculatePercentage(props.statistics.sqlFailed),
        color: COLORS.sqlFailed,
      },
      {
        label: 'API请求',
        value: props.statistics.apiRequest,
        percentage: calculatePercentage(props.statistics.apiRequest),
        color: COLORS.apiRequest,
      },
    ];
  });

  // Accessible chart description
  const chartAriaLabel = computed(() => {
    if (!isValidData.value || total.value === 0) return '步骤统计图表，暂无数据';
    
    return `步骤统计环形图：已完成${props.statistics.completed}个，占${calculatePercentage(props.statistics.completed)}%；SQL执行失败${props.statistics.sqlFailed}个，占${calculatePercentage(props.statistics.sqlFailed)}%；API请求${props.statistics.apiRequest}个，占${calculatePercentage(props.statistics.apiRequest)}%`;
  });
</script>

<style scoped>
  /* Widget-specific styles using design system */
  .widget {
    min-height: 300px;
  }

  .chart-container {
    min-height: 250px;
  }

  .chart-wrapper {
    width: 300px;
    height: 300px;
  }

  .legend-container {
    max-width: 100%;
  }

  .legend-color {
    flex-shrink: 0;
  }

  .empty-state {
    min-height: 250px;
  }

  /* Responsive adjustments for mobile */
  @media (max-width: 767px) {
    .chart-wrapper {
      width: 250px;
      height: 250px;
    }

    .chart-container {
      flex-direction: column;
    }

    .legend-container {
      width: 100%;
      margin-left: 0;
      margin-top: 1.5rem;
    }
  }

  /* Tablet adjustments */
  @media (min-width: 768px) and (max-width: 1023px) {
    .chart-wrapper {
      width: 200px;
      height: 200px;
    }
  }
</style>
