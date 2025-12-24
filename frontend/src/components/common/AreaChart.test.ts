import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';
import ECharts from 'vue-echarts';
import AreaChart from '@/components/common/AreaChart.vue';
import type { AreaChartSeries } from '@/types/dashboard';

describe('AreaChart', () => {
  const mockSeries: AreaChartSeries[] = [
    { name: 'Series 1', data: [10, 20, 30, 40, 50], color: '#3B82F6' },
    { name: 'Series 2', data: [15, 25, 35, 45, 55], color: '#10B981' },
  ];

  const mockLabels = ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'];

  const globalComponents = {
    'v-chart': ECharts,
  };

  it('should render without errors', () => {
    const wrapper = mount(AreaChart, {
      props: {
        series: mockSeries,
        labels: mockLabels,
      },
      global: {
        components: globalComponents,
      },
    });
    expect(wrapper.exists()).toBe(true);
  });

  it('should accept axis labels', () => {
    const wrapper = mount(AreaChart, {
      props: {
        series: mockSeries,
        labels: mockLabels,
        xAxisLabel: 'Date',
        yAxisLabel: 'Count',
      },
      global: {
        components: globalComponents,
      },
    });
    expect(wrapper.exists()).toBe(true);
  });

  it('should accept showGrid prop', () => {
    const wrapper = mount(AreaChart, {
      props: {
        series: mockSeries,
        labels: mockLabels,
        showGrid: false,
      },
      global: {
        components: globalComponents,
      },
    });
    expect(wrapper.exists()).toBe(true);
  });

  it('should handle empty series', () => {
    const wrapper = mount(AreaChart, {
      props: {
        series: [],
        labels: mockLabels,
      },
      global: {
        components: globalComponents,
      },
    });
    expect(wrapper.exists()).toBe(true);
  });

  it('should handle multiple series', () => {
    const multipleSeries: AreaChartSeries[] = [
      { name: 'Series 1', data: [10, 20, 30], color: '#3B82F6' },
      { name: 'Series 2', data: [15, 25, 35], color: '#10B981' },
      { name: 'Series 3', data: [20, 30, 40], color: '#F59E0B' },
      { name: 'Series 4', data: [25, 35, 45], color: '#EF4444' },
    ];
    const wrapper = mount(AreaChart, {
      props: {
        series: multipleSeries,
        labels: ['Day 1', 'Day 2', 'Day 3'],
      },
      global: {
        components: globalComponents,
      },
    });
    expect(wrapper.exists()).toBe(true);
  });
});
