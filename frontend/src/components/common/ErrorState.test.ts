import { mount } from '@vue/test-utils';
import { describe, expect, it, vi } from 'vitest';
import ErrorState from './ErrorState.vue';

describe('ErrorState', () => {
  it('should render with default props', () => {
    const wrapper = mount(ErrorState);

    expect(wrapper.find('.error-state').exists()).toBe(true);
    expect(wrapper.text()).toContain('加载失败');
    expect(wrapper.text()).toContain('无法加载数据，请检查网络连接后重试');
  });

  it('should render with custom title and message', () => {
    const wrapper = mount(ErrorState, {
      props: {
        title: '自定义标题',
        message: '自定义错误消息',
      },
    });

    expect(wrapper.text()).toContain('自定义标题');
    expect(wrapper.text()).toContain('自定义错误消息');
  });

  it('should show retry button by default', () => {
    const wrapper = mount(ErrorState);

    const retryButton = wrapper.find('[data-testid="retry-button"]');
    expect(retryButton.exists()).toBe(true);
    expect(retryButton.text()).toContain('重试');
  });

  it('should hide retry button when showRetry is false', () => {
    const wrapper = mount(ErrorState, {
      props: {
        showRetry: false,
      },
    });

    const retryButton = wrapper.find('[data-testid="retry-button"]');
    expect(retryButton.exists()).toBe(false);
  });

  it('should emit retry event when retry button is clicked', async () => {
    const wrapper = mount(ErrorState);

    const retryButton = wrapper.find('[data-testid="retry-button"]');
    await retryButton.trigger('click');

    expect(wrapper.emitted('retry')).toBeTruthy();
    expect(wrapper.emitted('retry')?.length).toBe(1);
  });

  it('should show contact support link when showContactSupport is true', () => {
    const wrapper = mount(ErrorState, {
      props: {
        showContactSupport: true,
      },
    });

    expect(wrapper.text()).toContain('联系技术支持');
  });

  it('should emit contactSupport event when support link is clicked', async () => {
    const wrapper = mount(ErrorState, {
      props: {
        showContactSupport: true,
      },
    });

    const supportLink = wrapper.find('a');
    await supportLink.trigger('click');

    expect(wrapper.emitted('contactSupport')).toBeTruthy();
  });

  it('should disable retry button and show loading state during retry', async () => {
    const wrapper = mount(ErrorState);

    const retryButton = wrapper.find('[data-testid="retry-button"]');
    await retryButton.trigger('click');

    // Button should be disabled
    expect(retryButton.attributes('disabled')).toBeDefined();

    // Should show "重试中..." text
    await wrapper.vm.$nextTick();
    expect(retryButton.text()).toContain('重试中');
  });

  it('should render error icon', () => {
    const wrapper = mount(ErrorState);

    const icon = wrapper.find('.error-icon svg');
    expect(icon.exists()).toBe(true);
  });
});
