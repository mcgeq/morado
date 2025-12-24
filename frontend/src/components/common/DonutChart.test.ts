import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';
import ECharts from 'vue-echarts';
import DonutChart from '@/components/common/DonutChart.vue';
import type { ChartDataset } from '@/types/dashboard';

describe('DonutChart', () => {
  const mockDatasets: ChartDataset[] = [
    { label: 'Completed', value: 50, color: '#3B82F6' },
    { label: 'Failed', value: 30, color: '#F59E0B' },
    { label: 'Pending', value: 20, color: '#8B5CF6' },
  ];

  const globalComponents = {
    'v-chart': ECharts,
  };

  it('should render without errors', () => {
    const wrapper = mount(DonutChart, {
      props: {
        datasets: mockDatasets,
      },
      global: {
        components: globalComponents,
      },
    });
    expect(wrapper.exists()).toBe(true);
  });

  it('should accept size prop', () => {
    const wrapper = mount(DonutChart, {
      props: {
        datasets: mockDatasets,
        size: 'lg',
      },
      global: {
        components: globalComponents,
      },
    });
    expect(wrapper.exists()).toBe(true);
  });

  it('should accept centerText prop', () => {
    const wrapper = mount(DonutChart, {
      props: {
        datasets: mockDatasets,
        centerText: 'Total: 100',
      },
      global: {
        components: globalComponents,
      },
    });
    expect(wrapper.exists()).toBe(true);
  });

  it('should accept showLegend prop', () => {
    const wrapper = mount(DonutChart, {
      props: {
        datasets: mockDatasets,
        showLegend: false,
      },
      global: {
        components: globalComponents,
      },
    });
    expect(wrapper.exists()).toBe(true);
  });

  it('should handle empty datasets', () => {
    const wrapper = mount(DonutChart, {
      props: {
        datasets: [],
      },
      global: {
        components: globalComponents,
      },
    });
    expect(wrapper.exists()).toBe(true);
  });
});
