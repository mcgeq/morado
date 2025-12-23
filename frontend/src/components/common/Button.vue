<template>
  <button :type="type" :disabled="disabled || loading" :class="buttonClasses" @click="handleClick">
    <span v-if="loading" class="mr-2">
      <svg
        class="animate-spin h-4 w-4"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path
          class="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
    </span>
    <slot />
  </button>
</template>

<script setup lang="ts">
  import { computed } from 'vue';

  interface Props {
    variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
    size?: 'sm' | 'md' | 'lg';
    type?: 'button' | 'submit' | 'reset';
    disabled?: boolean;
    loading?: boolean;
    fullWidth?: boolean;
  }

  const props = withDefaults(defineProps<Props>(), {
    variant: 'primary',
    size: 'md',
    type: 'button',
    disabled: false,
    loading: false,
    fullWidth: false,
  });

  const emit = defineEmits<{
    click: [event: MouseEvent];
  }>();

  const handleClick = (event: MouseEvent) => {
    if (!(props.disabled || props.loading)) {
      emit('click', event);
    }
  };

  const buttonClasses = computed(() => {
    const baseClasses = [
      'inline-flex',
      'items-center',
      'justify-center',
      'font-medium',
      'rounded-lg',
      'transition-colors',
      'focus:outline-none',
      'focus:ring-2',
      'focus:ring-offset-2',
      'disabled:opacity-50',
      'disabled:cursor-not-allowed',
    ];

    // Variant styles
    const variantClasses = {
      primary: ['bg-blue-600', 'text-white', 'hover:bg-blue-700', 'focus:ring-blue-500'],
      secondary: ['bg-gray-200', 'text-gray-900', 'hover:bg-gray-300', 'focus:ring-gray-500'],
      danger: ['bg-red-600', 'text-white', 'hover:bg-red-700', 'focus:ring-red-500'],
      ghost: ['bg-transparent', 'text-gray-700', 'hover:bg-gray-100', 'focus:ring-gray-500'],
    };

    // Size styles
    const sizeClasses = {
      sm: ['px-3', 'py-1.5', 'text-sm'],
      md: ['px-4', 'py-2', 'text-base'],
      lg: ['px-6', 'py-3', 'text-lg'],
    };

    // Width styles
    const widthClasses = props.fullWidth ? ['w-full'] : [];

    return [
      ...baseClasses,
      ...variantClasses[props.variant],
      ...sizeClasses[props.size],
      ...widthClasses,
    ].join(' ');
  });
</script>
