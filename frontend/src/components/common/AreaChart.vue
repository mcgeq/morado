<template>
  <div class="area-chart-container" role="img" :aria-label="accessibleChartLabel">
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
    <table class="sr-only" role="table" aria-label="面积图数据表">
      <caption>时间序列数据详情</caption>
      <thead>
        <tr>
          <th scope="col">{{ xAxisLabel || '日期' }}</th>
          <th v-for="s in series" :key="s.name" scope="col">{{ s.name }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(label, index) in labels" :key="label">
          <th scope="row">{{ label }}</th>
          <td v-for="s in series" :key="s.name">{{ s.data[index] }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
  import type { EChartsOption } from 'echarts';
  import { computed, ref } from 'vue';
  import type { AreaChartProps } from '@/types/dashboard';
  import {
    validateNonEmptyArray,
    validateAreaChartSeries,
  } from '@/utils/propValidation';

  const props = withDefaults(defineProps<AreaChartProps>(), {
    yAxisLabel: '',
    xAxisLabel: '',
    showGrid: true,
  });

  // Runtime prop validation in development
  if (import.meta.env.DEV) {
    if (!props.series) {
      console.error('[AreaChart] series prop is required');
    } else {
      validateNonEmptyArray(props.series, 'series');
      props.series.forEach((s, index) => {
        validateAreaChartSeries(s, `series[${index}]`);
      });
    }

    if (!props.labels) {
      console.error('[AreaChart] labels prop is required');
    } else {
      validateNonEmptyArray(props.labels, 'labels');
    }

    // Validate that all series have the same length as labels
    if (props.series && props.labels) {
      props.series.forEach((s, index) => {
        if (s.data.length !== props.labels.length) {
          console.warn(
            `[AreaChart] series[${index}].data length (${s.data.length}) does not match labels length (${props.labels.length})`
          );
        }
      });
    }
  }

  const hasError = ref(false);
  const errorMessage = ref('');

  // Validate data
  const isValidData = computed(() => {
    if (!props.series || !Array.isArray(props.series) || props.series.length === 0) {
      return false;
    }

    if (!props.labels || !Array.isArray(props.labels) || props.labels.length === 0) {
      return false;
    }

    // Check that all series have valid data
    return props.series.every(
      s =>
        s &&
        typeof s.name === 'string' &&
        Array.isArray(s.data) &&
        s.data.length === props.labels.length &&
        s.data.every(v => typeof v === 'number' && !Number.isNaN(v)) &&
        typeof s.color === 'string',
    );
  });

  // Transform series data to ECharts format
  const seriesData = computed(() => {
    if (!isValidData.value) return [];

    return props.series.map(s => ({
      name: s.name,
      type: 'line' as const,
      data: s.data,
      smooth: true,
      areaStyle: {
        opacity: 0.3,
      },
      lineStyle: {
        width: 2,
        color: s.color,
      },
      itemStyle: {
        color: s.color,
      },
      emphasis: {
        focus: 'series' as const,
      },
    }));
  });

  // ECharts option configuration
  const chartOption = computed<EChartsOption>(() => {
    if (!isValidData.value) {
      hasError.value = true;
      errorMessage.value = '数据格式无效或数据为空';
      return {};
    }

    try {
      return {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross',
            label: {
              backgroundColor: '#6a7985',
            },
          },
          formatter: (params: any) => {
            if (!Array.isArray(params)) return '';

            let result = `${params[0].axisValue}<br/>`;
            params.forEach((param: any) => {
              result += `${param.marker} ${param.seriesName}: ${param.value}<br/>`;
            });
            return result;
          },
        },
        legend: {
          data: props.series.map(s => s.name),
          top: 10,
          textStyle: {
            fontSize: 12,
          },
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '10%',
          top: '15%',
          containLabel: true,
          show: props.showGrid,
          borderColor: '#e5e7eb',
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: props.labels,
          name: props.xAxisLabel,
          nameLocation: 'middle',
          nameGap: 30,
          nameTextStyle: {
            fontSize: 12,
            color: '#666',
          },
          axisLine: {
            lineStyle: {
              color: '#d1d5db',
            },
          },
          axisLabel: {
            color: '#6b7280',
            fontSize: 11,
          },
        },
        yAxis: {
          type: 'value',
          name: props.yAxisLabel,
          nameTextStyle: {
            fontSize: 12,
            color: '#666',
          },
          axisLine: {
            show: false,
          },
          axisTick: {
            show: false,
          },
          axisLabel: {
            color: '#6b7280',
            fontSize: 11,
          },
          splitLine: {
            lineStyle: {
              color: '#e5e7eb',
              type: 'dashed',
            },
          },
        },
        series: seriesData.value,
      };
    } catch (error) {
      hasError.value = true;
      errorMessage.value = error instanceof Error ? error.message : '未知错误';
      return {};
    }
  });

  function handleChartError(error: Error): void {
    hasError.value = true;
    errorMessage.value = error.message || '图表渲染失败';
    console.error('AreaChart error:', error);
  }

  // Accessible chart label
  const accessibleChartLabel = computed(() => {
    if (!isValidData.value) {
      return '面积图，数据无效或为空';
    }
    
    const seriesNames = props.series.map(s => s.name).join('、');
    const dateRange = props.labels.length > 0 
      ? `从${props.labels[0]}到${props.labels[props.labels.length - 1]}`
      : '';
    
    return `面积图显示${seriesNames}的趋势变化，${dateRange}`;
  });
</script>

<style scoped>
  .area-chart-container {
    width: 100%;
    height: 100%;
    min-height: 300px;
    position: relative;
  }

  .chart {
    width: 100%;
    height: 100%;
  }

  /* Responsive adjustments for smaller screens */
  @media (max-width: 767px) {
    .area-chart-container {
      min-height: 250px;
    }
  }

  @media (min-width: 768px) and (max-width: 1023px) {
    .area-chart-container {
      min-height: 280px;
    }
  }
</style>
