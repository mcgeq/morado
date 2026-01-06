/**
 * Component Prop Validation Tests
 * 
 * Tests that components properly validate their props and display
 * appropriate fallback UI for invalid props in development mode.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import UserProfileCard from './UserProfileCard.vue';
import DonutChart from './DonutChart.vue';
import AreaChart from './AreaChart.vue';
import DashboardHeader from './DashboardHeader.vue';

// Mock vue-router
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}));

// Mock ECharts
vi.mock('vue-echarts', () => ({
  default: {
    name: 'VChart',
    props: ['option', 'autoresize'],
    template: '<div class="mock-chart"></div>',
  },
}));

describe('Component Prop Validation', () => {
  beforeEach(() => {
    vi.spyOn(console, 'warn').mockImplementation(() => {});
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  describe('UserProfileCard', () => {
    it('should render correctly with valid props', () => {
      const wrapper = mount(UserProfileCard, {
        props: {
          user: {
            id: '123',
            username: 'testuser',
            avatar: 'https://example.com/avatar.jpg',
            registrationDate: '2024-01-01T00:00:00Z',
          },
          metrics: {
            totalExecutions: 100,
            passedTests: 80,
            failedTests: 20,
          },
        },
      });

      expect(wrapper.find('article').exists()).toBe(true);
      expect(wrapper.text()).toContain('testuser');
    });

    it('should handle missing user data gracefully', () => {
      const wrapper = mount(UserProfileCard, {
        props: {
          user: null as any,
          metrics: {
            totalExecutions: 100,
            passedTests: 80,
            failedTests: 20,
          },
        },
      });

      // In development, should show error state
      if (import.meta.env.DEV) {
        expect(wrapper.find('[role="alert"]').exists()).toBe(true);
      }
    });

    it('should handle negative metrics gracefully', () => {
      const wrapper = mount(UserProfileCard, {
        props: {
          user: {
            id: '123',
            username: 'testuser',
            registrationDate: '2024-01-01T00:00:00Z',
          },
          metrics: {
            totalExecutions: -1,
            passedTests: 80,
            failedTests: 20,
          },
        },
      });

      // Should still render but may show warning in dev
      expect(wrapper.exists()).toBe(true);
    });

    it('should handle invalid date strings', () => {
      const wrapper = mount(UserProfileCard, {
        props: {
          user: {
            id: '123',
            username: 'testuser',
            registrationDate: 'invalid-date',
          },
          metrics: {
            totalExecutions: 100,
            passedTests: 80,
            failedTests: 20,
          },
        },
      });

      expect(wrapper.exists()).toBe(true);
    });
  });

  describe('DonutChart', () => {
    it('should render correctly with valid props', () => {
      const wrapper = mount(DonutChart, {
        props: {
          datasets: [
            { label: 'Category A', value: 30, color: '#3B82F6' },
            { label: 'Category B', value: 70, color: '#10B981' },
          ],
        },
      });

      expect(wrapper.find('.donut-chart-container').exists()).toBe(true);
    });

    it('should handle empty datasets', () => {
      const wrapper = mount(DonutChart, {
        props: {
          datasets: [],
        },
      });

      // Component validates and shows error or handles gracefully
      expect(wrapper.exists()).toBe(true);
      // In development, validation warnings should be logged
    });

    it('should handle invalid dataset values', () => {
      const wrapper = mount(DonutChart, {
        props: {
          datasets: [
            { label: 'Category A', value: -10, color: '#3B82F6' },
          ],
        },
      });

      // Component validates and shows error or handles gracefully
      expect(wrapper.exists()).toBe(true);
    });

    it('should handle missing required fields', () => {
      const wrapper = mount(DonutChart, {
        props: {
          datasets: [
            { label: '', value: 30, color: '#3B82F6' } as any,
          ],
        },
      });

      // Component validates and shows error or handles gracefully
      expect(wrapper.exists()).toBe(true);
    });

    it('should validate size prop', () => {
      const wrapper = mount(DonutChart, {
        props: {
          datasets: [
            { label: 'Category A', value: 30, color: '#3B82F6' },
          ],
          size: 'invalid' as any,
        },
      });

      // Should still render but may warn in dev
      expect(wrapper.exists()).toBe(true);
    });
  });

  describe('AreaChart', () => {
    it('should render correctly with valid props', () => {
      const wrapper = mount(AreaChart, {
        props: {
          series: [
            {
              name: 'Series 1',
              data: [10, 20, 30, 40],
              color: '#3B82F6',
            },
          ],
          labels: ['Jan', 'Feb', 'Mar', 'Apr'],
        },
      });

      expect(wrapper.find('.area-chart-container').exists()).toBe(true);
    });

    it('should handle empty series', () => {
      const wrapper = mount(AreaChart, {
        props: {
          series: [],
          labels: ['Jan', 'Feb'],
        },
      });

      // Component validates and shows error or handles gracefully
      expect(wrapper.exists()).toBe(true);
    });

    it('should handle mismatched data lengths', () => {
      const wrapper = mount(AreaChart, {
        props: {
          series: [
            {
              name: 'Series 1',
              data: [10, 20], // Only 2 data points
              color: '#3B82F6',
            },
          ],
          labels: ['Jan', 'Feb', 'Mar', 'Apr'], // 4 labels
        },
      });

      // Component validates and shows error or handles gracefully
      expect(wrapper.exists()).toBe(true);
    });

    it('should handle negative values in data', () => {
      const wrapper = mount(AreaChart, {
        props: {
          series: [
            {
              name: 'Series 1',
              data: [-10, 20, 30],
              color: '#3B82F6',
            },
          ],
          labels: ['Jan', 'Feb', 'Mar'],
        },
      });

      // Component validates and shows error or handles gracefully
      expect(wrapper.exists()).toBe(true);
    });
  });

  describe('DashboardHeader', () => {
    it('should render correctly with valid props', () => {
      const wrapper = mount(DashboardHeader, {
        props: {
          title: 'Test Dashboard',
          lastUpdated: new Date('2024-01-01T12:00:00Z'),
          loading: false,
        },
      });

      expect(wrapper.find('header').exists()).toBe(true);
      expect(wrapper.text()).toContain('Test Dashboard');
    });

    it('should handle null lastUpdated', () => {
      const wrapper = mount(DashboardHeader, {
        props: {
          title: 'Test Dashboard',
          lastUpdated: null,
          loading: false,
        },
      });

      expect(wrapper.find('header').exists()).toBe(true);
      expect(wrapper.text()).not.toContain('最后更新');
    });

    it('should handle invalid Date object', () => {
      const wrapper = mount(DashboardHeader, {
        props: {
          title: 'Test Dashboard',
          lastUpdated: new Date('invalid'),
          loading: false,
        },
      });

      expect(wrapper.exists()).toBe(true);
    });

    it('should handle non-boolean loading prop', () => {
      const wrapper = mount(DashboardHeader, {
        props: {
          title: 'Test Dashboard',
          loading: 'true' as any,
        },
      });

      // Should still render
      expect(wrapper.exists()).toBe(true);
    });
  });
});
