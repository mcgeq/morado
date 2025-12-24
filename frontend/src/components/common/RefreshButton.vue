<template>
  <button
    type="button"
    :disabled="loading"
    :class="buttonClasses"
    @click="handleClick"
    :aria-label="loading ? t('common.refreshing') : t('common.refreshData')"
  >
    <!-- Refresh Icon with Spin Animation -->
    <svg
      :class="['w-5 h-5', loading ? 'animate-spin' : '']"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
      />
    </svg>
    <span v-if="showLabel" class="ml-2">{{ loading ? t('common.refreshing') : t('common.refresh') }}</span>
  </button>
</template>

<script setup lang="ts">
  import { computed } from 'vue';
  import { useI18n } from 'vue-i18n';

  // ============================================================================
  // Props
  // ============================================================================

  interface Props {
    loading?: boolean;
    showLabel?: boolean;
    variant?: 'primary' | 'secondary' | 'ghost';
    size?: 'sm' | 'md' | 'lg';
  }

  const props = withDefaults(defineProps<Props>(), {
    loading: false,
    showLabel: true,
    variant: 'ghost',
    size: 'md',
  });
  
  const { t } = useI18n();

  // ============================================================================
  // Emits
  // ============================================================================

  const emit = defineEmits<{
    click: [event: MouseEvent];
  }>();

  // ============================================================================
  // Computed
  // ============================================================================

  const buttonClasses = computed(() => {
    const baseClasses = [
      'inline-flex',
      'items-center',
      'justify-center',
      'font-medium',
      'rounded-lg',
      'transition-all',
      'duration-200',
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
      ghost: [
        'bg-transparent',
        'text-gray-700',
        'hover:bg-gray-100',
        'focus:ring-gray-500',
        'border',
        'border-gray-300',
      ],
    };

    // Size styles
    const sizeClasses = {
      sm: ['px-2', 'py-1.5', 'text-sm'],
      md: ['px-3', 'py-2', 'text-base'],
      lg: ['px-4', 'py-2.5', 'text-lg'],
    };

    return [...baseClasses, ...variantClasses[props.variant], ...sizeClasses[props.size]].join(' ');
  });

  // ============================================================================
  // Methods
  // ============================================================================

  function handleClick(event: MouseEvent): void {
    if (!props.loading) {
      emit('click', event);
    }
  }
</script>
