import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';
import LoadingState from './LoadingState.vue';
import WidgetSkeleton from './WidgetSkeleton.vue';

describe('LoadingState', () => {
  it('should render full dashboard loading by default', () => {
    const wrapper = mount(LoadingState);

    expect(wrapper.find('.loading-state').exists()).toBe(true);
    expect(wrapper.find('.full-dashboard-skeleton').exists()).toBe(true);
  });

  it('should render header skeleton when showHeader is true', () => {
    const wrapper = mount(LoadingState, {
      props: {
        fullDashboard: false,
        showHeader: true,
      },
    });

    expect(wrapper.find('.header-skeleton').exists()).toBe(true);
  });

  it('should render profile skeleton when showProfile is true', () => {
    const wrapper = mount(LoadingState, {
      props: {
        fullDashboard: false,
        showProfile: true,
      },
    });

    expect(wrapper.find('.profile-skeleton').exists()).toBe(true);
  });

  it('should render quick actions skeleton when showQuickActions is true', () => {
    const wrapper = mount(LoadingState, {
      props: {
        fullDashboard: false,
        showQuickActions: true,
      },
    });

    expect(wrapper.find('.quick-actions-skeleton').exists()).toBe(true);
  });

  it('should render statistics grid when showStatistics is true', () => {
    const wrapper = mount(LoadingState, {
      props: {
        fullDashboard: false,
        showStatistics: true,
        showStepsStats: true,
        showApiUsage: true,
        showTrends: true,
      },
    });

    expect(wrapper.find('.statistics-grid-skeleton').exists()).toBe(true);
  });

  it('should render loading text when showLoadingText is true', () => {
    const wrapper = mount(LoadingState, {
      props: {
        showLoadingText: true,
        loadingText: '正在加载...',
      },
    });

    expect(wrapper.find('.loading-text').exists()).toBe(true);
    expect(wrapper.text()).toContain('正在加载...');
  });

  it('should use default loading text when not provided', () => {
    const wrapper = mount(LoadingState, {
      props: {
        showLoadingText: true,
      },
    });

    expect(wrapper.text()).toContain('加载中...');
  });

  it('should render multiple WidgetSkeleton components in full dashboard mode', () => {
    const wrapper = mount(LoadingState, {
      props: {
        fullDashboard: true,
      },
    });

    const skeletons = wrapper.findAllComponents(WidgetSkeleton);
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('should not render full dashboard when fullDashboard is false', () => {
    const wrapper = mount(LoadingState, {
      props: {
        fullDashboard: false,
      },
    });

    expect(wrapper.find('.full-dashboard-skeleton').exists()).toBe(false);
  });

  it('should render specific sections independently', () => {
    const wrapper = mount(LoadingState, {
      props: {
        fullDashboard: false,
        showProfile: true,
        showQuickActions: true,
      },
    });

    expect(wrapper.find('.profile-skeleton').exists()).toBe(true);
    expect(wrapper.find('.quick-actions-skeleton').exists()).toBe(true);
    expect(wrapper.find('.statistics-grid-skeleton').exists()).toBe(false);
  });

  it('should have spinning animation for loading icon', () => {
    const wrapper = mount(LoadingState, {
      props: {
        showLoadingText: true,
      },
    });

    const spinner = wrapper.find('.animate-spin');
    expect(spinner.exists()).toBe(true);
  });
});
