import { mount } from '@vue/test-utils';
import { describe, expect, it, vi } from 'vitest';
import { createMemoryHistory, createRouter } from 'vue-router';
import UserProfileCard from '@/components/common/UserProfileCard.vue';
import type { UserProfileCardProps } from '@/types/dashboard';

describe('UserProfileCard', () => {
  const mockUser: UserProfileCardProps['user'] = {
    id: '123',
    username: 'TestUser',
    avatar: 'https://example.com/avatar.jpg',
    registrationDate: '2024-01-15T10:30:00Z',
  };

  const mockMetrics: UserProfileCardProps['metrics'] = {
    totalExecutions: 1234,
    passedTests: 890,
    failedTests: 344,
  };

  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div>Home</div>' } },
      { path: '/profile', component: { template: '<div>Profile</div>' } },
    ],
  });

  it('should render without errors', () => {
    const wrapper = mount(UserProfileCard, {
      props: {
        user: mockUser,
        metrics: mockMetrics,
      },
      global: {
        plugins: [router],
      },
    });
    expect(wrapper.exists()).toBe(true);
  });

  it('should display username', () => {
    const wrapper = mount(UserProfileCard, {
      props: {
        user: mockUser,
        metrics: mockMetrics,
      },
      global: {
        plugins: [router],
      },
    });
    expect(wrapper.text()).toContain('TestUser');
  });

  it('should display formatted metrics with thousand separators', () => {
    const wrapper = mount(UserProfileCard, {
      props: {
        user: mockUser,
        metrics: mockMetrics,
      },
      global: {
        plugins: [router],
      },
    });
    expect(wrapper.text()).toContain('1,234'); // totalExecutions
    expect(wrapper.text()).toContain('890'); // passedTests
    expect(wrapper.text()).toContain('344'); // failedTests
  });

  it('should display avatar when provided', () => {
    const wrapper = mount(UserProfileCard, {
      props: {
        user: mockUser,
        metrics: mockMetrics,
      },
      global: {
        plugins: [router],
      },
    });
    const img = wrapper.find('img');
    expect(img.exists()).toBe(true);
    expect(img.attributes('src')).toBe('https://example.com/avatar.jpg');
  });

  it('should display fallback avatar when no avatar provided', () => {
    const userWithoutAvatar = { ...mockUser, avatar: undefined };
    const wrapper = mount(UserProfileCard, {
      props: {
        user: userWithoutAvatar,
        metrics: mockMetrics,
      },
      global: {
        plugins: [router],
      },
    });
    const img = wrapper.find('img');
    expect(img.exists()).toBe(false);
    // Should show initial letter
    expect(wrapper.text()).toContain('T'); // First letter of TestUser
  });

  it('should navigate to profile page on click', async () => {
    const wrapper = mount(UserProfileCard, {
      props: {
        user: mockUser,
        metrics: mockMetrics,
      },
      global: {
        plugins: [router],
      },
    });

    const pushSpy = vi.spyOn(router, 'push');
    await wrapper.trigger('click');
    expect(pushSpy).toHaveBeenCalledWith('/profile');
  });

  it('should have hover effect class', () => {
    const wrapper = mount(UserProfileCard, {
      props: {
        user: mockUser,
        metrics: mockMetrics,
      },
      global: {
        plugins: [router],
      },
    });
    expect(wrapper.classes()).toContain('hover:shadow-lg');
  });

  it('should display all three metric badges', () => {
    const wrapper = mount(UserProfileCard, {
      props: {
        user: mockUser,
        metrics: mockMetrics,
      },
      global: {
        plugins: [router],
      },
    });
    const badges = wrapper.findAll('.metric-badge');
    expect(badges).toHaveLength(3);
  });

  it('should have correct data-testid attributes', () => {
    const wrapper = mount(UserProfileCard, {
      props: {
        user: mockUser,
        metrics: mockMetrics,
      },
      global: {
        plugins: [router],
      },
    });
    expect(wrapper.find('[data-testid="total-executions"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="passed-tests"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="failed-tests"]').exists()).toBe(true);
  });

  it('should handle keyboard navigation with Enter key', async () => {
    const wrapper = mount(UserProfileCard, {
      props: {
        user: mockUser,
        metrics: mockMetrics,
      },
      global: {
        plugins: [router],
      },
    });

    const pushSpy = vi.spyOn(router, 'push');
    await wrapper.trigger('keydown.enter');
    expect(pushSpy).toHaveBeenCalledWith('/profile');
  });

  it('should handle keyboard navigation with Space key', async () => {
    const wrapper = mount(UserProfileCard, {
      props: {
        user: mockUser,
        metrics: mockMetrics,
      },
      global: {
        plugins: [router],
      },
    });

    const pushSpy = vi.spyOn(router, 'push');
    await wrapper.trigger('keydown.space');
    expect(pushSpy).toHaveBeenCalledWith('/profile');
  });
});
