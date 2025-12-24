/**
 * Tests for useNotification composable
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { useNotification } from './useNotification';

describe('useNotification', () => {
  beforeEach(() => {
    const { clear } = useNotification();
    clear();
  });

  it('should add a notification', () => {
    const { notifications, notify } = useNotification();

    notify('Test message', 'info', 0);

    expect(notifications.value).toHaveLength(1);
    expect(notifications.value[0]?.message).toBe('Test message');
    expect(notifications.value[0]?.type).toBe('info');
  });

  it('should add success notification', () => {
    const { notifications, success } = useNotification();

    success('Success message', 0);

    expect(notifications.value).toHaveLength(1);
    expect(notifications.value[0]?.type).toBe('success');
    expect(notifications.value[0]?.message).toBe('Success message');
  });

  it('should add error notification', () => {
    const { notifications, error } = useNotification();

    error('Error message', 0);

    expect(notifications.value).toHaveLength(1);
    expect(notifications.value[0]?.type).toBe('error');
    expect(notifications.value[0]?.message).toBe('Error message');
  });

  it('should add warning notification', () => {
    const { notifications, warning } = useNotification();

    warning('Warning message', 0);

    expect(notifications.value).toHaveLength(1);
    expect(notifications.value[0]?.type).toBe('warning');
    expect(notifications.value[0]?.message).toBe('Warning message');
  });

  it('should add info notification', () => {
    const { notifications, info } = useNotification();

    info('Info message', 0);

    expect(notifications.value).toHaveLength(1);
    expect(notifications.value[0]?.type).toBe('info');
    expect(notifications.value[0]?.message).toBe('Info message');
  });

  it('should manually remove notification', () => {
    const { notifications, notify, remove } = useNotification();

    const id = notify('Test message', 'info', 0); // No auto-dismiss

    expect(notifications.value).toHaveLength(1);

    remove(id);

    expect(notifications.value).toHaveLength(0);
  });

  it('should clear all notifications', () => {
    const { notifications, notify, clear } = useNotification();

    notify('Message 1', 'info', 0);
    notify('Message 2', 'error', 0);
    notify('Message 3', 'success', 0);

    expect(notifications.value).toHaveLength(3);

    clear();

    expect(notifications.value).toHaveLength(0);
  });

  it('should handle multiple notifications', () => {
    const { notifications, success, error, warning } = useNotification();

    success('Success', 0);
    error('Error', 0);
    warning('Warning', 0);

    expect(notifications.value).toHaveLength(3);
    expect(notifications.value[0]?.type).toBe('success');
    expect(notifications.value[1]?.type).toBe('error');
    expect(notifications.value[2]?.type).toBe('warning');
  });

  it('should return unique ids for each notification', () => {
    const { notify } = useNotification();

    const id1 = notify('Message 1', 'info', 0);
    const id2 = notify('Message 2', 'info', 0);
    const id3 = notify('Message 3', 'info', 0);

    expect(id1).not.toBe(id2);
    expect(id2).not.toBe(id3);
    expect(id1).not.toBe(id3);
  });
});
