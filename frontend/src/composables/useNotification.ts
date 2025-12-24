/**
 * Notification Composable
 *
 * Provides a simple notification system for displaying success, error, warning, and info messages.
 */

import { ref } from 'vue';

export type NotificationType = 'success' | 'error' | 'warning' | 'info';

export interface Notification {
  id: string;
  type: NotificationType;
  message: string;
  duration?: number;
}

const notifications = ref<Notification[]>([]);
let notificationId = 0;

export function useNotification() {
  /**
   * Show a notification
   */
  function notify(message: string, type: NotificationType = 'info', duration = 5000): string {
    const id = `notification-${++notificationId}`;
    const notification: Notification = {
      id,
      type,
      message,
      duration,
    };

    notifications.value.push(notification);

    // Auto-remove after duration
    if (duration > 0) {
      setTimeout(() => {
        remove(id);
      }, duration);
    }

    return id;
  }

  /**
   * Show success notification
   */
  function success(message: string, duration = 5000): string {
    return notify(message, 'success', duration);
  }

  /**
   * Show error notification
   */
  function error(message: string, duration = 7000): string {
    return notify(message, 'error', duration);
  }

  /**
   * Show warning notification
   */
  function warning(message: string, duration = 6000): string {
    return notify(message, 'warning', duration);
  }

  /**
   * Show info notification
   */
  function info(message: string, duration = 5000): string {
    return notify(message, 'info', duration);
  }

  /**
   * Remove a notification by id
   */
  function remove(id: string): void {
    const index = notifications.value.findIndex(n => n.id === id);
    if (index !== -1) {
      notifications.value.splice(index, 1);
    }
  }

  /**
   * Clear all notifications
   */
  function clear(): void {
    notifications.value = [];
  }

  return {
    notifications,
    notify,
    success,
    error,
    warning,
    info,
    remove,
    clear,
  };
}
