import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';
import RefreshButton from './RefreshButton.vue';

describe('RefreshButton', () => {
  describe('Rendering', () => {
    it('should render button element', () => {
      const wrapper = mount(RefreshButton);
      expect(wrapper.find('button').exists()).toBe(true);
    });

    it('should render refresh icon', () => {
      const wrapper = mount(RefreshButton);
      expect(wrapper.find('svg').exists()).toBe(true);
    });

    it('should show label by default', () => {
      const wrapper = mount(RefreshButton);
      expect(wrapper.text()).toContain('刷新');
    });

    it('should hide label when showLabel is false', () => {
      const wrapper = mount(RefreshButton, {
        props: {
          showLabel: false,
        },
      });
      expect(wrapper.text()).not.toContain('刷新');
    });

    it('should show loading text when loading', () => {
      const wrapper = mount(RefreshButton, {
        props: {
          loading: true,
        },
      });
      expect(wrapper.text()).toContain('刷新中...');
    });
  });

  describe('Loading State', () => {
    it('should disable button when loading', () => {
      const wrapper = mount(RefreshButton, {
        props: {
          loading: true,
        },
      });
      const button = wrapper.find('button');
      expect(button.attributes('disabled')).toBeDefined();
    });

    it('should add spin animation to icon when loading', () => {
      const wrapper = mount(RefreshButton, {
        props: {
          loading: true,
        },
      });
      const svg = wrapper.find('svg');
      expect(svg.classes()).toContain('animate-spin');
    });

    it('should not have spin animation when not loading', () => {
      const wrapper = mount(RefreshButton, {
        props: {
          loading: false,
        },
      });
      const svg = wrapper.find('svg');
      expect(svg.classes()).not.toContain('animate-spin');
    });
  });

  describe('Click Handling', () => {
    it('should emit click event when clicked', async () => {
      const wrapper = mount(RefreshButton);
      const button = wrapper.find('button');

      await button.trigger('click');

      expect(wrapper.emitted('click')).toBeTruthy();
      expect(wrapper.emitted('click')?.length).toBe(1);
    });

    it('should not emit click event when loading', async () => {
      const wrapper = mount(RefreshButton, {
        props: {
          loading: true,
        },
      });
      const button = wrapper.find('button');

      await button.trigger('click');

      expect(wrapper.emitted('click')).toBeFalsy();
    });

    it('should not emit click event when disabled', async () => {
      const wrapper = mount(RefreshButton, {
        props: {
          loading: true,
        },
      });
      const button = wrapper.find('button');

      await button.trigger('click');

      expect(wrapper.emitted('click')).toBeFalsy();
    });
  });

  describe('Variants', () => {
    it('should apply primary variant classes', () => {
      const wrapper = mount(RefreshButton, {
        props: {
          variant: 'primary',
        },
      });
      const button = wrapper.find('button');
      expect(button.classes()).toContain('bg-blue-600');
    });

    it('should apply secondary variant classes', () => {
      const wrapper = mount(RefreshButton, {
        props: {
          variant: 'secondary',
        },
      });
      const button = wrapper.find('button');
      expect(button.classes()).toContain('bg-gray-200');
    });

    it('should apply ghost variant classes by default', () => {
      const wrapper = mount(RefreshButton);
      const button = wrapper.find('button');
      expect(button.classes()).toContain('bg-transparent');
    });
  });

  describe('Sizes', () => {
    it('should apply small size classes', () => {
      const wrapper = mount(RefreshButton, {
        props: {
          size: 'sm',
        },
      });
      const button = wrapper.find('button');
      expect(button.classes()).toContain('px-2');
      expect(button.classes()).toContain('text-sm');
    });

    it('should apply medium size classes by default', () => {
      const wrapper = mount(RefreshButton);
      const button = wrapper.find('button');
      expect(button.classes()).toContain('px-3');
      expect(button.classes()).toContain('text-base');
    });

    it('should apply large size classes', () => {
      const wrapper = mount(RefreshButton, {
        props: {
          size: 'lg',
        },
      });
      const button = wrapper.find('button');
      expect(button.classes()).toContain('px-4');
      expect(button.classes()).toContain('text-lg');
    });
  });

  describe('Accessibility', () => {
    it('should have aria-label', () => {
      const wrapper = mount(RefreshButton);
      const button = wrapper.find('button');
      expect(button.attributes('aria-label')).toBe('刷新数据');
    });

    it('should update aria-label when loading', () => {
      const wrapper = mount(RefreshButton, {
        props: {
          loading: true,
        },
      });
      const button = wrapper.find('button');
      expect(button.attributes('aria-label')).toBe('刷新中...');
    });

    it('should have type="button"', () => {
      const wrapper = mount(RefreshButton);
      const button = wrapper.find('button');
      expect(button.attributes('type')).toBe('button');
    });
  });

  describe('Styling', () => {
    it('should have base button classes', () => {
      const wrapper = mount(RefreshButton);
      const button = wrapper.find('button');

      expect(button.classes()).toContain('inline-flex');
      expect(button.classes()).toContain('items-center');
      expect(button.classes()).toContain('justify-center');
      expect(button.classes()).toContain('rounded-lg');
    });

    it('should have focus ring classes', () => {
      const wrapper = mount(RefreshButton);
      const button = wrapper.find('button');

      expect(button.classes()).toContain('focus:outline-none');
      expect(button.classes()).toContain('focus:ring-2');
    });

    it('should have disabled opacity class', () => {
      const wrapper = mount(RefreshButton);
      const button = wrapper.find('button');

      expect(button.classes()).toContain('disabled:opacity-50');
      expect(button.classes()).toContain('disabled:cursor-not-allowed');
    });
  });
});
