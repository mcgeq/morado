/**
 * TrendAnalysisWidget Component Tests
 *
 * Unit tests for the TrendAnalysisWidget component.
 */

import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';
import type { TrendDataPoint } from '@/types/dashboard';
import TrendAnalysisWidget from './TrendAnalysisWidget.vue';

// Mock AreaChart component
const mockAreaChart = {
  name: 'AreaChart',
  template: '<div class="mock-area-chart"><slot /></div>',
  props: ['series', 'labels', 'yAxisLabel', 'xAxisLabel', 'showGrid'],
};

describe('TrendAnalysisWidget', () => {
  const mockTrendData: TrendDataPoint[] = [
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
  ];

  it('should render with default title', () => {
    const wrapper = mount(TrendAnalysisWidget, {
      props: {
        data: mockTrendData,
      },
      global: {
        stubs: {
          AreaChart: mockAreaChart,
        },
      },
    });

    expect(wrapper.text()).toContain('定时参数测试统计');
  });

  it('should render with custom title', () => {
    const customTitle = '自定义趋势分析';
    const wrapper = mount(TrendAnalysisWidget, {
      props: {
        data: mockTrendData,
        title: customTitle,
      },
      global: {
        stubs: {
          AreaChart: mockAreaChart,
        },
      },
    });

    expect(wrapper.text()).toContain(customTitle);
  });

  it('should display date range when provided', () => {
    const dateRange = { start: '2024-01-01', end: '2024-01-31' };
    const wrapper = mount(TrendAnalysisWidget, {
      props: {
        data: mockTrendData,
        dateRange,
      },
      global: {
        stubs: {
          AreaChart: mockAreaChart,
        },
      },
    });

    expect(wrapper.text()).toContain('2024-01-01 至 2024-01-31');
  });

  it('should display empty state when data is empty', () => {
    const wrapper = mount(TrendAnalysisWidget, {
      props: {
        data: [],
      },
      global: {
        stubs: {
          AreaChart: mockAreaChart,
        },
      },
    });

    expect(wrapper.find('[data-testid="empty-state"]').exists()).toBe(true);
    expect(wrapper.text()).toContain('暂无趋势数据');
  });

  it('should not render chart when data is empty', () => {
    const wrapper = mount(TrendAnalysisWidget, {
      props: {
        data: [],
      },
      global: {
        stubs: {
          AreaChart: mockAreaChart,
        },
      },
    });

    expect(wrapper.findComponent(mockAreaChart).exists()).toBe(false);
  });

  it('should render chart when data is provided', () => {
    const wrapper = mount(TrendAnalysisWidget, {
      props: {
        data: mockTrendData,
      },
      global: {
        stubs: {
          AreaChart: mockAreaChart,
        },
      },
    });

    expect(wrapper.findComponent(mockAreaChart).exists()).toBe(true);
  });

  it('should transform data to correct chart labels', () => {
    const wrapper = mount(TrendAnalysisWidget, {
      props: {
        data: mockTrendData,
      },
      global: {
        stubs: {
          AreaChart: mockAreaChart,
        },
      },
    });

    const areaChart = wrapper.findComponent(mockAreaChart);
    expect(areaChart.props('labels')).toEqual(['2024-01-01', '2024-01-02', '2024-01-03']);
  });

  it('should transform data to correct chart series with four series', () => {
    const wrapper = mount(TrendAnalysisWidget, {
      props: {
        data: mockTrendData,
      },
      global: {
        stubs: {
          AreaChart: mockAreaChart,
        },
      },
    });

    const areaChart = wrapper.findComponent(mockAreaChart);
    const series = areaChart.props('series');

    expect(series).toHaveLength(4);
    expect(series[0].name).toBe('定时元件');
    expect(series[1].name).toBe('用例元件');
    expect(series[2].name).toBe('实际元件');
    expect(series[3].name).toBe('检测元件');
  });

  it('should use correct color scheme for series', () => {
    const wrapper = mount(TrendAnalysisWidget, {
      props: {
        data: mockTrendData,
      },
      global: {
        stubs: {
          AreaChart: mockAreaChart,
        },
      },
    });

    const areaChart = wrapper.findComponent(mockAreaChart);
    const series = areaChart.props('series');

    expect(series[0].color).toBe('#3B82F6'); // Blue for scheduled
    expect(series[1].color).toBe('#10B981'); // Green for test case
    expect(series[2].color).toBe('#F59E0B'); // Orange for actual
    expect(series[3].color).toBe('#EF4444'); // Red for detection
  });

  it('should map data values correctly to series', () => {
    const wrapper = mount(TrendAnalysisWidget, {
      props: {
        data: mockTrendData,
      },
      global: {
        stubs: {
          AreaChart: mockAreaChart,
        },
      },
    });

    const areaChart = wrapper.findComponent(mockAreaChart);
    const series = areaChart.props('series');

    expect(series[0].data).toEqual([10, 12, 8]); // scheduledComponents
    expect(series[1].data).toEqual([20, 22, 18]); // testCaseComponents
    expect(series[2].data).toEqual([15, 18, 12]); // actualComponents
    expect(series[3].data).toEqual([5, 7, 4]); // detectionComponents
  });

  it('should handle zero values without gaps', () => {
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
    ];

    const wrapper = mount(TrendAnalysisWidget, {
      props: {
        data: dataWithZeros,
      },
      global: {
        stubs: {
          AreaChart: mockAreaChart,
        },
      },
    });

    const areaChart = wrapper.findComponent(mockAreaChart);
    const series = areaChart.props('series');

    // Verify zero values are included (not gaps)
    expect(series[0].data).toEqual([10, 0]);
    expect(series[1].data).toEqual([0, 22]);
    expect(series[2].data).toEqual([15, 0]);
    expect(series[3].data).toEqual([0, 7]);
  });

  it('should pass correct axis labels to chart', () => {
    const wrapper = mount(TrendAnalysisWidget, {
      props: {
        data: mockTrendData,
      },
      global: {
        stubs: {
          AreaChart: mockAreaChart,
        },
      },
    });

    const areaChart = wrapper.findComponent(mockAreaChart);
    expect(areaChart.props('yAxisLabel')).toBe('数量');
    expect(areaChart.props('xAxisLabel')).toBe('日期');
  });

  it('should enable grid display', () => {
    const wrapper = mount(TrendAnalysisWidget, {
      props: {
        data: mockTrendData,
      },
      global: {
        stubs: {
          AreaChart: mockAreaChart,
        },
      },
    });

    const areaChart = wrapper.findComponent(mockAreaChart);
    expect(areaChart.props('showGrid')).toBe(true);
  });

  it('should maintain date format as YYYY-MM-DD', () => {
    const wrapper = mount(TrendAnalysisWidget, {
      props: {
        data: mockTrendData,
      },
      global: {
        stubs: {
          AreaChart: mockAreaChart,
        },
      },
    });

    const areaChart = wrapper.findComponent(mockAreaChart);
    const labels = areaChart.props('labels');

    // Verify all labels match YYYY-MM-DD format
    labels.forEach((label: string) => {
      expect(label).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    });
  });
});
