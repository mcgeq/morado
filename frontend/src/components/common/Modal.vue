<template>
  <TransitionRoot :show="modelValue" as="template">
    <Dialog as="div" class="relative z-50" @close="handleClose">
      <TransitionChild
        as="template"
        enter="ease-out duration-300"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in duration-200"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black bg-opacity-25" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4 text-center">
          <TransitionChild
            as="template"
            enter="ease-out duration-300"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="ease-in duration-200"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel
              :class="[
                'w-full transform overflow-hidden rounded-2xl bg-white text-left align-middle shadow-xl transition-all',
                sizeClasses[size],
              ]"
            >
              <div
                v-if="showHeader"
                class="flex items-center justify-between px-6 py-4 border-b border-gray-200"
              >
                <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">
                  <slot name="title">{{ title }}</slot>
                </DialogTitle>
                <button
                  v-if="showClose"
                  type="button"
                  class="text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-lg p-1"
                  @click="handleClose"
                >
                  <span class="sr-only">关闭</span>
                  <svg
                    class="h-6 w-6"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>

              <div class="px-6 py-4">
                <slot />
              </div>

              <div
                v-if="showFooter"
                class="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-200"
              >
                <slot name="footer">
                  <button
                    type="button"
                    class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    @click="handleCancel"
                  >
                    {{ cancelText }}
                  </button>
                  <button
                    type="button"
                    class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    @click="handleConfirm"
                  >
                    {{ confirmText }}
                  </button>
                </slot>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
  import {
    Dialog,
    DialogPanel,
    DialogTitle,
    TransitionChild,
    TransitionRoot,
  } from '@headlessui/vue';

  interface Props {
    modelValue: boolean;
    title?: string;
    size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
    showHeader?: boolean;
    showFooter?: boolean;
    showClose?: boolean;
    closeOnClickOutside?: boolean;
    confirmText?: string;
    cancelText?: string;
  }

  const props = withDefaults(defineProps<Props>(), {
    title: '',
    size: 'md',
    showHeader: true,
    showFooter: true,
    showClose: true,
    closeOnClickOutside: true,
    confirmText: '确认',
    cancelText: '取消',
  });

  const emit = defineEmits<{
    'update:modelValue': [value: boolean];
    confirm: [];
    cancel: [];
    close: [];
  }>();

  const sizeClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    full: 'max-w-full mx-4',
  };

  const handleClose = () => {
    if (props.closeOnClickOutside) {
      emit('update:modelValue', false);
      emit('close');
    }
  };

  const handleConfirm = () => {
    emit('confirm');
    emit('update:modelValue', false);
  };

  const handleCancel = () => {
    emit('cancel');
    emit('update:modelValue', false);
  };
</script>
