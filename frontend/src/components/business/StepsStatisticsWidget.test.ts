import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';
import type { StepStatistics } from '@/types/dashboard';
import StepsStatisticsWidget from './StepsStatisticsWidget.vue';

describe('StepsStatisticsWidget', () => {
  const normalStatistics: StepStatistics = {
    completed: 150,
    sqlFailed: 30,
    apiRequest: 70,
  };

  const emptyStatistics: StepStatistics = {
    completed: 0,
    sqlFailed: 0,
    apiRequest: 0,
  };

  it('should render without errors', () => {
    const wrapper = mount(StepsStatisticsWidget, {
      props: {
        statistics: normalStatistics,
      },
    });
    expect(wrapper.exists()).toBe(true);
  });

  it('should display default title when no title prop provided', () => {
    const wrapper = mount(StepsStatisticsWidget, {
      props: {
        statistics: normalStatistics,
      },
    });
    expect(wrapper.text()).toContain('Steps统计');
  });

  it('should display custom title when provided', () => {
    const wrapper = mount(StepsStatisticsWidget, {
      props: {
        statistics: normalStatistics,
        title: '自定义标题',
      },
    });
    expect(wrapper.text()).toContain('自定义标题');
  });

  it('should calculate percentages correctly', () => {
    const statistics: StepStatistics = {
      completed: 50,
      sqlFailed: 30,
      apiRequest: 20,
    };
    const wrapper = mount(StepsStatisticsWidget, {
      props: { statistics },
    });

    // Total = 100, so percentages should be exact
    expect(wrapper.text()).toContain('50%'); // 50/100
    expect(wrapper.text()).toContain('30%'); // 30/100
    expect(wrapper.text()).toContain('20%'); // 20/100
  });

  it('should round percentages to whole numbers', () => {
    const statistics: StepStatistics = {
      completed: 33,
      sqlFailed: 33,
      apiRequest: 34,
    };
    const wrapper = mount(StepsStatisticsWidget, {
      props: { statistics },
    });

    // Total = 100, percentages should be rounded
    expect(wrapper.text()).toContain('33%');
    expect(wrapper.text()).toContain('34%');
  });

  it('should display empty state when total is zero', () => {
    const wrapper = mount(StepsStatisticsWidget, {
      props: {
        statistics: emptyStatistics,
      },
    });

    expect(wrapper.find('[data-testid="empty-state"]').exists()).toBe(true);
    expect(wrapper.text()).toContain('暂无数据');
  });

  it('should not display chart when data is empty', () => {
    const wrapper = mount(StepsStatisticsWidget, {
      props: {
        statistics: emptyStatistics,
      },
    });

    expect(wrapper.find('.chart-container').exists()).toBe(false);
  });

  it('should display chart when data is present', () => {
    const wrapper = mount(StepsStatisticsWidget, {
      props: {
        statistics: normalStatistics,
      },
    });

    expect(wrapper.find('.chart-container').exists()).toBe(true);
    expect(wrapper.find('[data-testid="empty-state"]').exists()).toBe(false);
  });

  it('should display all three legend items', () => {
    const wrapper = mount(StepsStatisticsWidget, {
      props: {
        statistics: normalStatistics,
      },
    });

    expect(wrapper.text()).toContain('已完成');
    expect(wrapper.text()).toContain('SQL执行失败');
    expect(wrapper.text()).toContain('API请求');
  });

  it('should display counts for each category', () => {
    const wrapper = mount(StepsStatisticsWidget, {
      props: {
        statistics: normalStatistics,
      },
    });

    expect(wrapper.text()).toContain('150');
    expect(wrapper.text()).toContain('30');
    expect(wrapper.text()).toContain('70');
  });

  it('should display total count', () => {
    const wrapper = mount(StepsStatisticsWidget, {
      props: {
        statistics: normalStatistics,
      },
    });

    const total = 150 + 30 + 70;
    expect(wrapper.text()).toContain('总计');
    expect(wrapper.text()).toContain(total.toString());
  });

  it('should handle large numbers correctly', () => {
    const largeStatistics: StepStatistics = {
      completed: 5420,
      sqlFailed: 1230,
      apiRequest: 3890,
    };
    const wrapper = mount(StepsStatisticsWidget, {
      props: {
        statistics: largeStatistics,
      },
    });

    expect(wrapper.text()).toContain('5420');
    expect(wrapper.text()).toContain('1230');
    expect(wrapper.text()).toContain('3890');
  });

  it('should calculate correct percentages for uneven distribution', () => {
    const statistics: StepStatistics = {
      completed: 100,
      sqlFailed: 50,
      apiRequest: 25,
    };
    const wrapper = mount(StepsStatisticsWidget, {
      props: { statistics },
    });

    // Total = 175
    // completed: 100/175 = 57.14% -> 57%
    // sqlFailed: 50/175 = 28.57% -> 29%
    // apiRequest: 25/175 = 14.29% -> 14%
    expect(wrapper.text()).toContain('57%');
    expect(wrapper.text()).toContain('29%');
    expect(wrapper.text()).toContain('14%');
  });

  it('should have proper styling classes', () => {
    const wrapper = mount(StepsStatisticsWidget, {
      props: {
        statistics: normalStatistics,
      },
    });

    expect(wrapper.classes()).toContain('steps-statistics-widget');
    expect(wrapper.classes()).toContain('bg-white');
    expect(wrapper.classes()).toContain('rounded-lg');
    expect(wrapper.classes()).toContain('shadow-md');
  });

  it('should display legend colors', () => {
    const wrapper = mount(StepsStatisticsWidget, {
      props: {
        statistics: normalStatistics,
      },
    });

    const legendColors = wrapper.findAll('.legend-color');
    expect(legendColors).toHaveLength(3);
  });
});
