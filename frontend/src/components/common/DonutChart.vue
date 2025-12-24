<template>
  <div class="donut-chart-container" :class="sizeClass" role="img" :aria-label="accessibleChartLabel">
    <!-- Error State -->
    <div
      v-if="hasError"
      class="chart-error flex flex-col items-center justify-center h-full text-center p-4"
      role="alert"
      aria-live="assertive"
    >
      <svg class="w-12 h-12 text-red-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <p class="text-sm text-gray-600">图表加载失败</p>
      <p class="text-xs text-gray-500 mt-1">{{ errorMessage }}</p>
    </div>

    <!-- Chart -->
    <v-chart
      v-else
      :option="chartOption"
      :autoresize="true"
      class="chart"
      @error="handleChartError"
      aria-hidden="true"
    />
    
    <!-- Screen reader accessible data table -->
    <table class="sr-only" role="table" aria-label="环形图数据表">
      <caption>数据分布详情</caption>
      <thead>
        <tr>
          <th scope="col">类别</th>
          <th scope="col">数值</th>
          <th scope="col">百分比</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="dataset in datasets" :key="dataset.label">
          <th scope="row">{{ dataset.label }}</th>
          <td>{{ dataset.value }}</td>
          <td>{{ calculatePercentage(dataset.value) }}%</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
  import type { EChartsOption } from 'echarts';
  import { computed, ref } from 'vue';
  import type { DonutChartProps } from '@/types/dashboard';
  import { memoize } from '@/utils/performance';
  import {
    validateNonEmptyArray,
    validateChartDataset,
  } from '@/utils/propValidation';

  const props = withDefaults(defineProps<DonutChartProps>(), {
    centerText: '',
    showLegend: true,
    size: 'md',
  });

  // Memoize percentage calculation for performance
  const memoizedPercentageCalc = memoize((value: number, total: number): number => {
    if (total === 0) return 0;
    return Math.round((value / total) * 100);
  });

  // Runtime prop validation in development
  if (import.meta.env.DEV) {
    if (!props.datasets) {
      console.error('[DonutChart] datasets prop is required');
    } else {
      validateNonEmptyArray(props.datasets, 'datasets');
      props.datasets.forEach((dataset, index) => {
        validateChartDataset(dataset, `datasets[${index}]`);
      });
    }

    if (props.size && !['sm', 'md', 'lg'].includes(props.size)) {
      console.warn(`[DonutChart] size must be 'sm', 'md', or 'lg', received '${props.size}'`);
    }
  }

  const hasError = ref(false);
  const errorMessage = ref('');

  // Size class for responsive sizing
  const sizeClass = computed(() => {
    return `chart-size-${props.size}`;
  });

  // Validate datasets
  const isValidData = computed(() => {
    if (!props.datasets || !Array.isArray(props.datasets)) {
      return false;
    }

    return props.datasets.every(
      dataset =>
        dataset &&
        typeof dataset.label === 'string' &&
        typeof dataset.value === 'number' &&
        !Number.isNaN(dataset.value) &&
        dataset.value >= 0 &&
        typeof dataset.color === 'string',
    );
  });

  // Calculate total for percentage display
  const total = computed(() => {
    if (!isValidData.value) return 0;
    return props.datasets.reduce((sum, item) => sum + item.value, 0);
  });

  // Transform datasets to ECharts format
  const chartData = computed(() => {
    if (!isValidData.value) return [];

    return props.datasets.map(dataset => ({
      name: dataset.label,
      value: dataset.value,
      itemStyle: {
        color: dataset.color,
      },
    }));
  });

  // ECharts option configuration
  const chartOption = computed<EChartsOption>(() => {
    if (!isValidData.value) {
      hasError.value = true;
      errorMessage.value = '数据格式无效';
      return {};
    }

    try {
      const option: EChartsOption = {
        tooltip: {
          trigger: 'item',
          formatter: (params: any) => {
            const percentage = total.value > 0 ? Math.round((params.value / total.value) * 100) : 0;
            return `${params.name}: ${params.value} (${percentage}%)`;
          },
        },
        legend: props.showLegend
          ? {
              orient: 'vertical',
              right: '10%',
              top: 'center',
              textStyle: {
                fontSize: 12,
              },
            }
          : undefined,
        series: [
          {
            type: 'pie',
            radius: ['50%', '70%'], // Donut shape
            center: props.showLegend ? ['40%', '50%'] : ['50%', '50%'],
            avoidLabelOverlap: false,
            label: {
              show: false,
              position: 'center',
            },
            emphasis: {
              label: {
                show: !!props.centerText,
                fontSize: 16,
                fontWeight: 'bold',
                formatter: props.centerText,
              },
            },
            labelLine: {
              show: false,
            },
            data: chartData.value,
          },
        ],
      };

      // Add center text if provided
      if (props.centerText && !props.showLegend) {
        option.graphic = {
          type: 'text',
          left: 'center',
          top: 'center',
          style: {
            text: props.centerText,
            fontSize: 16,
            fontWeight: 'bold',
            fill: '#333',
          },
        };
      }

      return option;
    } catch (error) {
      hasError.value = true;
      errorMessage.value = error instanceof Error ? error.message : '未知错误';
      return {};
    }
  });

  function handleChartError(error: Error): void {
    hasError.value = true;
    errorMessage.value = error.message || '图表渲染失败';
    console.error('DonutChart error:', error);
  }

  // Calculate percentage for accessibility
  const calculatePercentage = (value: number): number => {
    return memoizedPercentageCalc(value, total.value);
  };

  // Accessible chart label
  const accessibleChartLabel = computed(() => {
    if (!isValidData.value || total.value === 0) {
      return '环形图，暂无数据';
    }
    
    const descriptions = props.datasets.map(d => 
      `${d.label}${d.value}个，占${calculatePercentage(d.value)}%`
    ).join('；');
    
    return `环形图显示数据分布：${descriptions}`;
  });
</script>

<style scoped>
  .donut-chart-container {
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    width: 100%;
    aspect-ratio: 1 / 1; /* Maintain square aspect ratio */
  }

  .chart {
    width: 100%;
    height: 100%;
  }

  /* Size variants with max dimensions */
  .chart-size-sm {
    max-width: 200px;
    max-height: 200px;
  }

  .chart-size-md {
    max-width: 300px;
    max-height: 300px;
  }

  .chart-size-lg {
    max-width: 400px;
    max-height: 400px;
  }

  /* Responsive adjustments */
  @media (max-width: 767px) {
    .chart-size-sm {
      max-width: 150px;
      max-height: 150px;
    }

    .chart-size-md {
      max-width: 250px;
      max-height: 250px;
    }

    .chart-size-lg {
      max-width: 300px;
      max-height: 300px;
    }
  }
</style>
