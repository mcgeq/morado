import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';
import DashboardHeader from './DashboardHeader.vue';
import RefreshButton from './RefreshButton.vue';

describe('DashboardHeader', () => {
  describe('Rendering', () => {
    it('should render with default title', () => {
      const wrapper = mount(DashboardHeader);
      expect(wrapper.text()).toContain('仪表盘');
    });

    it('should render with custom title', () => {
      const wrapper = mount(DashboardHeader, {
        props: {
          title: '测试管理平台',
        },
      });
      expect(wrapper.text()).toContain('测试管理平台');
    });

    it('should render RefreshButton component', () => {
      const wrapper = mount(DashboardHeader);
      expect(wrapper.findComponent(RefreshButton).exists()).toBe(true);
    });

    it('should display last updated time when provided', () => {
      const lastUpdated = new Date('2024-01-15T10:30:00');
      const wrapper = mount(DashboardHeader, {
        props: {
          lastUpdated,
        },
      });
      expect(wrapper.text()).toContain('最后更新:');
    });

    it('should not display last updated time when null', () => {
      const wrapper = mount(DashboardHeader, {
        props: {
          lastUpdated: null,
        },
      });
      expect(wrapper.text()).not.toContain('最后更新:');
    });
  });

  describe('Loading State', () => {
    it('should pass loading prop to RefreshButton', () => {
      const wrapper = mount(DashboardHeader, {
        props: {
          loading: true,
        },
      });
      const refreshButton = wrapper.findComponent(RefreshButton);
      expect(refreshButton.props('loading')).toBe(true);
    });

    it('should not show loading by default', () => {
      const wrapper = mount(DashboardHeader);
      const refreshButton = wrapper.findComponent(RefreshButton);
      expect(refreshButton.props('loading')).toBe(false);
    });
  });

  describe('Refresh Functionality', () => {
    it('should emit refresh event when refresh button is clicked', async () => {
      const wrapper = mount(DashboardHeader);
      const refreshButton = wrapper.findComponent(RefreshButton);

      await refreshButton.vm.$emit('click');

      expect(wrapper.emitted('refresh')).toBeTruthy();
      expect(wrapper.emitted('refresh')?.length).toBe(1);
    });

    it('should not emit refresh when loading', async () => {
      const wrapper = mount(DashboardHeader, {
        props: {
          loading: true,
        },
      });
      const refreshButton = wrapper.findComponent(RefreshButton);

      // Try to click the button (should be disabled)
      const button = refreshButton.find('button');
      await button.trigger('click');

      // The RefreshButton component should prevent the click when loading
      expect(wrapper.emitted('refresh')).toBeFalsy();
    });
  });

  describe('Date Formatting', () => {
    it('should format date correctly', () => {
      const lastUpdated = new Date('2024-01-15T10:30:45');
      const wrapper = mount(DashboardHeader, {
        props: {
          lastUpdated,
        },
      });

      // Check that the formatted date is displayed
      const text = wrapper.text();
      expect(text).toContain('2024');
      expect(text).toContain('01');
      expect(text).toContain('15');
    });

    it('should handle invalid date gracefully', () => {
      const wrapper = mount(DashboardHeader, {
        props: {
          lastUpdated: new Date('invalid'),
        },
      });

      // Should not crash and should not display invalid date
      expect(wrapper.text()).toContain('仪表盘');
    });
  });

  describe('Accessibility', () => {
    it('should have proper heading structure', () => {
      const wrapper = mount(DashboardHeader);
      const heading = wrapper.find('h1');
      expect(heading.exists()).toBe(true);
      expect(heading.classes()).toContain('text-3xl');
    });

    it('should pass accessibility props to RefreshButton', () => {
      const wrapper = mount(DashboardHeader);
      const refreshButton = wrapper.findComponent(RefreshButton);
      const button = refreshButton.find('button');

      expect(button.attributes('aria-label')).toBeDefined();
    });
  });

  describe('Styling', () => {
    it('should have proper container classes', () => {
      const wrapper = mount(DashboardHeader);
      const container = wrapper.find('.dashboard-header');

      expect(container.exists()).toBe(true);
      expect(container.classes()).toContain('bg-white');
      expect(container.classes()).toContain('rounded-lg');
      expect(container.classes()).toContain('shadow-md');
    });

    it('should have flex layout for title and button', () => {
      const wrapper = mount(DashboardHeader);
      const flexContainer = wrapper.find('.flex.items-center.justify-between');

      expect(flexContainer.exists()).toBe(true);
    });
  });
});
