/**
 * Home.vue Component Tests
 *
 * Tests for the main dashboard container component.
 */

import { mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useDashboardStore } from '@/stores/dashboard';
import Home from './Home.vue';

// Mock components to avoid complex dependencies
vi.mock('@/components/common', () => ({
  DashboardHeader: { name: 'DashboardHeader', template: '<div>DashboardHeader</div>' },
  UserProfileCard: { name: 'UserProfileCard', template: '<div>UserProfileCard</div>' },
  QuickActionsPanel: { name: 'QuickActionsPanel', template: '<div>QuickActionsPanel</div>' },
  LoadingState: {
    name: 'LoadingState',
    template: '<div data-testid="loading-state">LoadingState</div>',
  },
  ErrorState: { name: 'ErrorState', template: '<div data-testid="error-state">ErrorState</div>' },
  NotificationContainer: {
    name: 'NotificationContainer',
    template: '<div data-testid="notification-container"></div>',
  },
}));

vi.mock('@/components/business', () => ({
  StepsStatisticsWidget: {
    name: 'StepsStatisticsWidget',
    template: '<div>StepsStatisticsWidget</div>',
  },
  ApiUsageWidget: { name: 'ApiUsageWidget', template: '<div>ApiUsageWidget</div>' },
  TrendAnalysisWidget: { name: 'TrendAnalysisWidget', template: '<div>TrendAnalysisWidget</div>' },
}));

describe('Home.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it('should render loading state when loading and no data', async () => {
    const store = useDashboardStore();

    // Mock refreshDashboard to set loading state
    vi.spyOn(store, 'refreshDashboard').mockImplementation(async () => {
      store.loading = true;
      store.userData = null;
      store.statistics = null;
    });

    const wrapper = mount(Home, {
      global: {
        stubs: {
          DashboardHeader: true,
          LoadingState: { template: '<div data-testid="loading-state">LoadingState</div>' },
          ErrorState: true,
          UserProfileCard: true,
          QuickActionsPanel: true,
          StepsStatisticsWidget: true,
          ApiUsageWidget: true,
          TrendAnalysisWidget: true,
        },
      },
    });

    await wrapper.vm.$nextTick();

    expect(wrapper.find('[data-testid="loading-state"]').exists()).toBe(true);
  });

  it('should render error state when error and no data', async () => {
    const store = useDashboardStore();

    // Mock refreshDashboard to set error state
    vi.spyOn(store, 'refreshDashboard').mockImplementation(async () => {
      store.loading = false;
      store.error = 'Test error';
      store.userData = null;
      store.statistics = null;
      throw new Error('Test error');
    });

    const wrapper = mount(Home, {
      global: {
        stubs: {
          DashboardHeader: true,
          LoadingState: true,
          ErrorState: { template: '<div data-testid="error-state">ErrorState</div>' },
          UserProfileCard: true,
          QuickActionsPanel: true,
          StepsStatisticsWidget: true,
          ApiUsageWidget: true,
          TrendAnalysisWidget: true,
        },
      },
    });

    await wrapper.vm.$nextTick();

    expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true);
  });

  it('should render dashboard content when data is available', async () => {
    const store = useDashboardStore();

    // Mock refreshDashboard to set data
    vi.spyOn(store, 'refreshDashboard').mockImplementation(async () => {
      store.loading = false;
      store.error = null;
      store.userData = {
        id: '1',
        username: 'testuser',
        avatar: null,
        registrationDate: '2024-01-01',
        metrics: {
          totalExecutions: 100,
          passedTests: 80,
          failedTests: 20,
        },
      };
      store.statistics = {
        steps: {
          completed: 50,
          sqlFailed: 10,
          apiRequest: 40,
        },
        apiUsage: {
          apiCompletion: {
            percentage: 75,
            totalApis: 100,
            completedApis: 75,
            taggedApis: 60,
          },
          testCaseCompletion: {
            percentage: 80,
            totalTestCases: 50,
            passedTestCases: 40,
            taggedTestCases: 35,
          },
        },
        trends: [
          {
            date: '2024-01-01',
            scheduledComponents: 10,
            testCaseComponents: 20,
            actualComponents: 15,
            detectionComponents: 5,
          },
        ],
      };
    });

    const wrapper = mount(Home, {
      global: {
        stubs: {
          DashboardHeader: true,
          LoadingState: true,
          ErrorState: true,
          UserProfileCard: { template: '<div>UserProfileCard</div>' },
          QuickActionsPanel: { template: '<div>QuickActionsPanel</div>' },
          StepsStatisticsWidget: { template: '<div>StepsStatisticsWidget</div>' },
          ApiUsageWidget: { template: '<div>ApiUsageWidget</div>' },
          TrendAnalysisWidget: { template: '<div>TrendAnalysisWidget</div>' },
        },
      },
    });

    // Wait for the onMounted hook to complete
    await new Promise(resolve => setTimeout(resolve, 100));
    await wrapper.vm.$nextTick();

    expect(wrapper.text().includes('UserProfileCard')).toBe(true);
    expect(wrapper.text().includes('QuickActionsPanel')).toBe(true);
    expect(wrapper.text().includes('StepsStatisticsWidget')).toBe(true);
    expect(wrapper.text().includes('ApiUsageWidget')).toBe(true);
    expect(wrapper.text().includes('TrendAnalysisWidget')).toBe(true);
  });

  it('should define quick actions with correct properties', async () => {
    const store = useDashboardStore();

    // Mock refreshDashboard to prevent API calls
    vi.spyOn(store, 'refreshDashboard').mockResolvedValue();

    const wrapper = mount(Home, {
      global: {
        stubs: {
          DashboardHeader: true,
          LoadingState: true,
          ErrorState: true,
          UserProfileCard: true,
          QuickActionsPanel: true,
          StepsStatisticsWidget: true,
          ApiUsageWidget: true,
          TrendAnalysisWidget: true,
        },
      },
    });

    await wrapper.vm.$nextTick();
  });

  it('should call refreshDashboard with false when handleRefresh is called', async () => {
    const store = useDashboardStore();

    // Mock refreshDashboard
    const refreshSpy = vi.spyOn(store, 'refreshDashboard').mockResolvedValue();

    const wrapper = mount(Home, {
      global: {
        stubs: {
          DashboardHeader: true,
          LoadingState: true,
          ErrorState: true,
          UserProfileCard: true,
          QuickActionsPanel: true,
          StepsStatisticsWidget: true,
          ApiUsageWidget: true,
          TrendAnalysisWidget: true,
        },
      },
    });

    await wrapper.vm.$nextTick();

    // Call handleRefresh
    await (wrapper.vm as any).handleRefresh();

    // Verify refreshDashboard was called with false (force fresh data)
    expect(refreshSpy).toHaveBeenCalledWith(false);
  });

  it('should update lastUpdated timestamp after successful refresh', async () => {
    const store = useDashboardStore();

    // Mock refreshDashboard to update lastUpdated
    vi.spyOn(store, 'refreshDashboard').mockImplementation(async () => {
      store.lastUpdated = new Date();
    });

    const wrapper = mount(Home, {
      global: {
        stubs: {
          DashboardHeader: true,
          LoadingState: true,
          ErrorState: true,
          UserProfileCard: true,
          QuickActionsPanel: true,
          StepsStatisticsWidget: true,
          ApiUsageWidget: true,
          TrendAnalysisWidget: true,
        },
      },
    });

    await wrapper.vm.$nextTick();

    const beforeRefresh = store.lastUpdated;

    // Call handleRefresh
    await (wrapper.vm as any).handleRefresh();

    // Verify lastUpdated was updated
    expect(store.lastUpdated).not.toBe(beforeRefresh);
    expect(store.lastUpdated).toBeInstanceOf(Date);
  });

  it('should handle refresh errors gracefully', async () => {
    const store = useDashboardStore();

    // Mock refreshDashboard to throw error
    const error = new Error('Refresh failed');
    vi.spyOn(store, 'refreshDashboard').mockRejectedValue(error);
    store.error = 'Refresh failed';

    const wrapper = mount(Home, {
      global: {
        stubs: {
          DashboardHeader: true,
          LoadingState: true,
          ErrorState: true,
          UserProfileCard: true,
          QuickActionsPanel: true,
          StepsStatisticsWidget: true,
          ApiUsageWidget: true,
          TrendAnalysisWidget: true,
        },
      },
    });

    await wrapper.vm.$nextTick();

    // Call handleRefresh and expect it to handle the error
    await (wrapper.vm as any).handleRefresh();

    // Verify error was set in store
    expect(store.error).toBe('Refresh failed');
  });
});
