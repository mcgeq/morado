<template>
  <section 
    class="widget widget-hoverable" 
    role="region" 
    aria-labelledby="trend-analysis-title"
    aria-describedby="trend-analysis-description"
  >
    <!-- Widget Header -->
    <div class="widget-header">
      <h3 id="trend-analysis-title" class="widget-title">{{ title || '定时参数测试统计' }}</h3>
      <p v-if="dateRange" class="widget-subtitle">{{ dateRange.start }}至 {{ dateRange.end }}</p>
      <span id="trend-analysis-description" class="sr-only">
        测试组件趋势分析图表，显示定时元件、用例元件、实际元件和检测元件随时间的变化趋势
      </span>
    </div>

    <!-- Empty State -->
    <div
      v-if="!isValidData || data.length === 0"
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
          d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"
        />
      </svg>
      <p class="text-gray-500 text-sm">
        {{ !isValidData ? '数据格式无效' : '暂无趋势数据' }}
      </p>
    </div>

    <!-- Chart -->
    <div v-else class="chart-container">
      <div role="img" :aria-label="chartAriaLabel">
        <AreaChart
          :series="chartSeries"
          :labels="chartLabels"
          :y-axis-label="'数量'"
          :x-axis-label="'日期'"
          :show-grid="true"
        />
      </div>
      <!-- Screen reader text for chart data -->
      <div class="sr-only" role="status">
        <p>趋势分析图表数据：</p>
        <ul>
          <li v-for="(point, index) in data" :key="index">
            {{ point.date }}：
            定时元件{{ point.scheduledComponents }}个，
            用例元件{{ point.testCaseComponents }}个，
            实际元件{{ point.actualComponents }}个，
            检测元件{{ point.detectionComponents }}个
          </li>
        </ul>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
  import { computed } from 'vue';
  import AreaChart from '@/components/common/AreaChart.vue';
  import type { AreaChartSeries, TrendAnalysisWidgetProps } from '@/types/dashboard';
  import {
    validateNonEmptyArray,
    validateNonEmptyString,
    validateNonNegativeNumber,
  } from '@/utils/propValidation';

  const props = withDefaults(defineProps<TrendAnalysisWidgetProps>(), {
    title: '',
  });

  // Runtime prop validation in development
  if (import.meta.env.DEV) {
    if (!props.data) {
      console.error('[TrendAnalysisWidget] data prop is required');
    } else if (Array.isArray(props.data) && props.data.length > 0) {
      validateNonEmptyArray(props.data, 'data');
      
      props.data.forEach((point, index) => {
        validateNonEmptyString(point.date, `data[${index}].date`);
        validateNonNegativeNumber(point.scheduledComponents, `data[${index}].scheduledComponents`);
        validateNonNegativeNumber(point.testCaseComponents, `data[${index}].testCaseComponents`);
        validateNonNegativeNumber(point.actualComponents, `data[${index}].actualComponents`);
        validateNonNegativeNumber(point.detectionComponents, `data[${index}].detectionComponents`);
      });
    }

    if (props.dateRange) {
      if (!props.dateRange.start || !props.dateRange.end) {
        console.warn('[TrendAnalysisWidget] dateRange must have both start and end properties');
      } else {
        validateNonEmptyString(props.dateRange.start, 'dateRange.start');
        validateNonEmptyString(props.dateRange.end, 'dateRange.end');
      }
    }
  }

  // Color scheme as per design document
  const COLORS = {
    scheduledComponents: '#3B82F6', // Blue
    testCaseComponents: '#10B981', // Green
    actualComponents: '#F59E0B', // Orange
    detectionComponents: '#EF4444', // Red
  };

  // Validate data
  const isValidData = computed(() => {
    if (!props.data || !Array.isArray(props.data)) return false;

    return props.data.every(
      point =>
        point &&
        typeof point.date === 'string' &&
        typeof point.scheduledComponents === 'number' &&
        typeof point.testCaseComponents === 'number' &&
        typeof point.actualComponents === 'number' &&
        typeof point.detectionComponents === 'number' &&
        !Number.isNaN(point.scheduledComponents) &&
        !Number.isNaN(point.testCaseComponents) &&
        !Number.isNaN(point.actualComponents) &&
        !Number.isNaN(point.detectionComponents) &&
        point.scheduledComponents >= 0 &&
        point.testCaseComponents >= 0 &&
        point.actualComponents >= 0 &&
        point.detectionComponents >= 0,
    );
  });

  // Extract labels (dates) from data
  // Format dates in YYYY-MM-DD format (already in this format from API)
  const chartLabels = computed<string[]>(() => {
    if (!isValidData.value) return [];
    return props.data.map(point => point.date);
  });

  // Transform data to chart series format
  const chartSeries = computed<AreaChartSeries[]>(() => {
    if (!isValidData.value) return [];

    return [
      {
        name: '定时元件',
        data: props.data.map(point => point.scheduledComponents),
        color: COLORS.scheduledComponents,
      },
      {
        name: '用例元件',
        data: props.data.map(point => point.testCaseComponents),
        color: COLORS.testCaseComponents,
      },
      {
        name: '实际元件',
        data: props.data.map(point => point.actualComponents),
        color: COLORS.actualComponents,
      },
      {
        name: '检测元件',
        data: props.data.map(point => point.detectionComponents),
        color: COLORS.detectionComponents,
      },
    ];
  });

  // Accessible chart description
  const chartAriaLabel = computed(() => {
    if (!isValidData.value || props.data.length === 0) {
      return '趋势分析图表，暂无数据';
    }
    
    const firstDate = props.data[0]?.date || '';
    const lastDate = props.data[props.data.length - 1]?.date || '';
    const dateRange = firstDate && lastDate ? `${firstDate}至${lastDate}` : '';
    return `趋势分析面积图，显示${dateRange}期间四种组件类型的数量变化趋势`;
  });
</script>

<style scoped>
  /* Widget-specific styles using design system */
  .widget {
    min-height: 400px;
  }

  .chart-container {
    min-height: 350px;
    height: 350px;
  }

  .empty-state {
    min-height: 350px;
  }

  /* Responsive adjustments */
  @media (max-width: 767px) {
    .widget {
      min-height: 350px;
    }

    .chart-container {
      min-height: 300px;
      height: 300px;
    }

    .empty-state {
      min-height: 300px;
    }
  }

  @media (min-width: 768px) and (max-width: 1023px) {
    .chart-container {
      min-height: 320px;
      height: 320px;
    }
  }
</style>
