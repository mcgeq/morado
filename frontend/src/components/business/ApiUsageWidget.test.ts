import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';
import type { ApiUsageData } from '@/types/dashboard';
import ApiUsageWidget from './ApiUsageWidget.vue';

describe('ApiUsageWidget', () => {
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

  it('should render without errors', () => {
    const wrapper = mount(ApiUsageWidget, {
      props: {
        data: normalData,
      },
    });
    expect(wrapper.exists()).toBe(true);
  });

  it('should display default title when no title prop provided', () => {
    const wrapper = mount(ApiUsageWidget, {
      props: {
        data: normalData,
      },
    });
    expect(wrapper.text()).toContain('API使用情况');
  });

  it('should display custom title when provided', () => {
    const wrapper = mount(ApiUsageWidget, {
      props: {
        data: normalData,
        title: '自定义标题',
      },
    });
    expect(wrapper.text()).toContain('自定义标题');
  });

  it('should display API completion percentage', () => {
    const wrapper = mount(ApiUsageWidget, {
      props: {
        data: normalData,
      },
    });
    const apiPercentage = wrapper.find('[data-testid="api-completion-percentage"]');
    expect(apiPercentage.text()).toBe('65%');
  });

  it('should display test case completion percentage', () => {
    const wrapper = mount(ApiUsageWidget, {
      props: {
        data: normalData,
      },
    });
    const testCasePercentage = wrapper.find('[data-testid="testcase-completion-percentage"]');
    expect(testCasePercentage.text()).toBe('72%');
  });

  it('should display API metrics correctly', () => {
    const wrapper = mount(ApiUsageWidget, {
      props: {
        data: normalData,
      },
    });

    expect(wrapper.find('[data-testid="total-apis"]').text()).toBe('150');
    expect(wrapper.find('[data-testid="completed-apis"]').text()).toBe('98');
    expect(wrapper.find('[data-testid="tagged-apis"]').text()).toBe('85');
  });

  it('should display test case metrics correctly', () => {
    const wrapper = mount(ApiUsageWidget, {
      props: {
        data: normalData,
      },
    });

    expect(wrapper.find('[data-testid="total-testcases"]').text()).toBe('250');
    expect(wrapper.find('[data-testid="passed-testcases"]').text()).toBe('180');
    expect(wrapper.find('[data-testid="tagged-testcases"]').text()).toBe('165');
  });

  it('should display section headers', () => {
    const wrapper = mount(ApiUsageWidget, {
      props: {
        data: normalData,
      },
    });

    expect(wrapper.text()).toContain('API完成度');
    expect(wrapper.text()).toContain('用例完成度');
  });

  it('should display metric labels', () => {
    const wrapper = mount(ApiUsageWidget, {
      props: {
        data: normalData,
      },
    });

    expect(wrapper.text()).toContain('用例管理API总数');
    expect(wrapper.text()).toContain('API总数');
    expect(wrapper.text()).toContain('API通过打标数量');
    expect(wrapper.text()).toContain('用例总数');
    expect(wrapper.text()).toContain('测试通过打标数量');
  });

  it('should handle zero data correctly', () => {
    const wrapper = mount(ApiUsageWidget, {
      props: {
        data: zeroData,
      },
    });

    expect(wrapper.find('[data-testid="api-completion-percentage"]').text()).toBe('0%');
    expect(wrapper.find('[data-testid="testcase-completion-percentage"]').text()).toBe('0%');
    expect(wrapper.find('[data-testid="total-apis"]').text()).toBe('0');
    expect(wrapper.find('[data-testid="total-testcases"]').text()).toBe('0');
  });

  it('should display green indicator for high performance (>=70%)', () => {
    const highPerformanceData: ApiUsageData = {
      apiCompletion: {
        percentage: 90,
        totalApis: 100,
        completedApis: 90,
        taggedApis: 85,
      },
      testCaseCompletion: {
        percentage: 85,
        totalTestCases: 100,
        passedTestCases: 85,
        taggedTestCases: 80,
      },
    };

    const wrapper = mount(ApiUsageWidget, {
      props: {
        data: highPerformanceData,
      },
    });

    const indicators = wrapper.findAll('.bg-green-500');
    expect(indicators.length).toBeGreaterThan(0);
  });

  it('should display red indicator for low performance (<40%)', () => {
    const lowPerformanceData: ApiUsageData = {
      apiCompletion: {
        percentage: 30,
        totalApis: 100,
        completedApis: 30,
        taggedApis: 20,
      },
      testCaseCompletion: {
        percentage: 25,
        totalTestCases: 100,
        passedTestCases: 25,
        taggedTestCases: 15,
      },
    };

    const wrapper = mount(ApiUsageWidget, {
      props: {
        data: lowPerformanceData,
      },
    });

    const indicators = wrapper.findAll('.bg-red-500');
    expect(indicators.length).toBeGreaterThan(0);
  });

  it('should display yellow indicator for moderate performance (40-69%)', () => {
    const moderatePerformanceData: ApiUsageData = {
      apiCompletion: {
        percentage: 55,
        totalApis: 100,
        completedApis: 55,
        taggedApis: 50,
      },
      testCaseCompletion: {
        percentage: 60,
        totalTestCases: 100,
        passedTestCases: 60,
        taggedTestCases: 55,
      },
    };

    const wrapper = mount(ApiUsageWidget, {
      props: {
        data: moderatePerformanceData,
      },
    });

    const indicators = wrapper.findAll('.bg-yellow-500');
    expect(indicators.length).toBeGreaterThan(0);
  });

  it('should display gray indicator when total is zero', () => {
    const wrapper = mount(ApiUsageWidget, {
      props: {
        data: zeroData,
      },
    });

    const indicators = wrapper.findAll('.bg-gray-400');
    expect(indicators.length).toBeGreaterThan(0);
  });

  it('should have proper styling classes', () => {
    const wrapper = mount(ApiUsageWidget, {
      props: {
        data: normalData,
      },
    });

    expect(wrapper.classes()).toContain('api-usage-widget');
    expect(wrapper.classes()).toContain('bg-white');
    expect(wrapper.classes()).toContain('rounded-lg');
    expect(wrapper.classes()).toContain('shadow-md');
  });

  it('should have two-column grid layout', () => {
    const wrapper = mount(ApiUsageWidget, {
      props: {
        data: normalData,
      },
    });

    const grid = wrapper.find('.usage-grid');
    expect(grid.exists()).toBe(true);
    expect(grid.classes()).toContain('grid');
    expect(grid.classes()).toContain('grid-cols-2');
  });

  it('should display divider between sections', () => {
    const wrapper = mount(ApiUsageWidget, {
      props: {
        data: normalData,
      },
    });

    const divider = wrapper.find('.divider-line');
    expect(divider.exists()).toBe(true);
  });

  it('should handle large numbers correctly', () => {
    const largeData: ApiUsageData = {
      apiCompletion: {
        percentage: 85,
        totalApis: 9999,
        completedApis: 8499,
        taggedApis: 7500,
      },
      testCaseCompletion: {
        percentage: 92,
        totalTestCases: 15000,
        passedTestCases: 13800,
        taggedTestCases: 12500,
      },
    };

    const wrapper = mount(ApiUsageWidget, {
      props: {
        data: largeData,
      },
    });

    expect(wrapper.find('[data-testid="total-apis"]').text()).toBe('9999');
    expect(wrapper.find('[data-testid="total-testcases"]').text()).toBe('15000');
  });

  it('should display percentage with % symbol', () => {
    const wrapper = mount(ApiUsageWidget, {
      props: {
        data: normalData,
      },
    });

    const apiPercentage = wrapper.find('[data-testid="api-completion-percentage"]');
    const testCasePercentage = wrapper.find('[data-testid="testcase-completion-percentage"]');

    expect(apiPercentage.text()).toMatch(/%$/);
    expect(testCasePercentage.text()).toMatch(/%$/);
  });

  it('should have color-coded percentage displays', () => {
    const wrapper = mount(ApiUsageWidget, {
      props: {
        data: normalData,
      },
    });

    const apiPercentage = wrapper.find('[data-testid="api-completion-percentage"]');
    const testCasePercentage = wrapper.find('[data-testid="testcase-completion-percentage"]');

    expect(apiPercentage.classes()).toContain('text-blue-600');
    expect(testCasePercentage.classes()).toContain('text-green-600');
  });

  it('should display all completion sections', () => {
    const wrapper = mount(ApiUsageWidget, {
      props: {
        data: normalData,
      },
    });

    const sections = wrapper.findAll('.completion-section');
    expect(sections).toHaveLength(2);
  });

  it('should display metrics lists', () => {
    const wrapper = mount(ApiUsageWidget, {
      props: {
        data: normalData,
      },
    });

    const metricsLists = wrapper.findAll('.metrics-list');
    expect(metricsLists).toHaveLength(2);
  });
});
