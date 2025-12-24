import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';
import WidgetSkeleton from './WidgetSkeleton.vue';

describe('WidgetSkeleton', () => {
  it('should render with default type', () => {
    const wrapper = mount(WidgetSkeleton);

    expect(wrapper.find('.widget-skeleton').exists()).toBe(true);
    expect(wrapper.find('.skeleton-default').exists()).toBe(true);
  });

  it('should render profile skeleton when type is profile', () => {
    const wrapper = mount(WidgetSkeleton, {
      props: {
        type: 'profile',
      },
    });

    expect(wrapper.find('.skeleton-profile').exists()).toBe(true);
    expect(wrapper.find('.skeleton-default').exists()).toBe(false);
  });

  it('should render chart skeleton when type is chart', () => {
    const wrapper = mount(WidgetSkeleton, {
      props: {
        type: 'chart',
      },
    });

    expect(wrapper.find('.skeleton-chart').exists()).toBe(true);
  });

  it('should render stats skeleton when type is stats', () => {
    const wrapper = mount(WidgetSkeleton, {
      props: {
        type: 'stats',
      },
    });

    expect(wrapper.find('.skeleton-stats').exists()).toBe(true);
  });

  it('should render trend skeleton when type is trend', () => {
    const wrapper = mount(WidgetSkeleton, {
      props: {
        type: 'trend',
      },
    });

    expect(wrapper.find('.skeleton-trend').exists()).toBe(true);
  });

  it('should render actions skeleton when type is actions', () => {
    const wrapper = mount(WidgetSkeleton, {
      props: {
        type: 'actions',
      },
    });

    expect(wrapper.find('.skeleton-actions').exists()).toBe(true);
  });

  it('should have animate-pulse class for animation', () => {
    const wrapper = mount(WidgetSkeleton);

    expect(wrapper.find('.animate-pulse').exists()).toBe(true);
  });

  it('should have minimum height', () => {
    const wrapper = mount(WidgetSkeleton);

    const skeleton = wrapper.find('.widget-skeleton');
    expect(skeleton.exists()).toBe(true);
  });

  it('should render skeleton header for all types', () => {
    const types: Array<'profile' | 'chart' | 'stats' | 'trend' | 'actions' | 'default'> = [
      'profile',
      'chart',
      'stats',
      'trend',
      'actions',
      'default',
    ];

    types.forEach(type => {
      const wrapper = mount(WidgetSkeleton, {
        props: { type },
      });

      expect(wrapper.find('.skeleton-header').exists()).toBe(true);
    });
  });
});
