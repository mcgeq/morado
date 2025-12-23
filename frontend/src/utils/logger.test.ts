/**
 * Logger 单元测试
 *
 * 测试日志工具的基本功能
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';
import { createLogger, Logger, LogLevel, log } from './logger';

describe('Logger', () => {
  beforeEach(() => {
    // 清除所有 console mock
    vi.clearAllMocks();
  });

  describe('基本功能', () => {
    it('应该创建 Logger 实例', () => {
      const logger = new Logger('Test');
      expect(logger).toBeInstanceOf(Logger);
    });

    it('应该使用 createLogger 创建实例', () => {
      const logger = createLogger('Test');
      expect(logger).toBeInstanceOf(Logger);
    });

    it('应该支持子 Logger', () => {
      const parent = createLogger('Parent');
      const child = parent.child('Child');
      expect(child).toBeInstanceOf(Logger);
    });
  });

  describe('日志级别', () => {
    it('应该根据日志级别过滤日志', () => {
      const consoleSpy = vi.spyOn(console, 'groupCollapsed');

      // 创建只显示 WARN 及以上级别的 logger
      const logger = createLogger('Test', { level: LogLevel.WARN });

      logger.debug('debug message'); // 不应该显示
      logger.info('info message'); // 不应该显示
      logger.warn('warn message'); // 应该显示
      logger.error('error message'); // 应该显示

      // 只有 warn 和 error 应该被调用
      expect(consoleSpy).toHaveBeenCalledTimes(2);
    });

    it('应该支持 NONE 级别（不显示任何日志）', () => {
      const consoleSpy = vi.spyOn(console, 'groupCollapsed');

      const logger = createLogger('Test', { level: LogLevel.NONE });

      logger.debug('debug');
      logger.info('info');
      logger.warn('warn');
      logger.error('error');

      expect(consoleSpy).not.toHaveBeenCalled();
    });
  });

  describe('日志方法', () => {
    it('应该支持 debug 方法', () => {
      const consoleSpy = vi.spyOn(console, 'groupCollapsed');
      const logger = createLogger('Test', { level: LogLevel.DEBUG });

      logger.debug('test message');

      expect(consoleSpy).toHaveBeenCalled();
    });

    it('应该支持 info 方法', () => {
      const consoleSpy = vi.spyOn(console, 'groupCollapsed');
      const logger = createLogger('Test');

      logger.info('test message');

      expect(consoleSpy).toHaveBeenCalled();
    });

    it('应该支持 success 方法', () => {
      const consoleSpy = vi.spyOn(console, 'groupCollapsed');
      const logger = createLogger('Test');

      logger.success('test message');

      expect(consoleSpy).toHaveBeenCalled();
    });

    it('应该支持 warn 方法', () => {
      const consoleSpy = vi.spyOn(console, 'groupCollapsed');
      const logger = createLogger('Test');

      logger.warn('test message');

      expect(consoleSpy).toHaveBeenCalled();
    });

    it('应该支持 error 方法', () => {
      const consoleSpy = vi.spyOn(console, 'groupCollapsed');
      const logger = createLogger('Test');

      logger.error('test message');

      expect(consoleSpy).toHaveBeenCalled();
    });
  });

  describe('特殊日志方法', () => {
    it('应该支持 api 方法', () => {
      const consoleSpy = vi.spyOn(console, 'groupCollapsed');
      const logger = createLogger('Test', { level: LogLevel.DEBUG });

      logger.api('GET', '/api/users');

      expect(consoleSpy).toHaveBeenCalled();
    });

    it('应该支持 router 方法', () => {
      const consoleSpy = vi.spyOn(console, 'groupCollapsed');
      const logger = createLogger('Test', { level: LogLevel.DEBUG });

      logger.router('/home', '/about');

      expect(consoleSpy).toHaveBeenCalled();
    });

    it('应该支持 store 方法', () => {
      const consoleSpy = vi.spyOn(console, 'groupCollapsed');
      const logger = createLogger('Test', { level: LogLevel.DEBUG });

      logger.store('用户登录');

      expect(consoleSpy).toHaveBeenCalled();
    });
  });

  describe('工具方法', () => {
    it('应该支持分组日志', () => {
      const groupSpy = vi.spyOn(console, 'group');
      const groupEndSpy = vi.spyOn(console, 'groupEnd');
      const logger = createLogger('Test');

      logger.group('测试分组');
      logger.groupEnd();

      expect(groupSpy).toHaveBeenCalled();
      expect(groupEndSpy).toHaveBeenCalled();
    });

    it('应该支持性能计时', () => {
      const timeSpy = vi.spyOn(console, 'time');
      const timeEndSpy = vi.spyOn(console, 'timeEnd');
      const logger = createLogger('Test', { level: LogLevel.DEBUG });

      logger.time('测试计时');
      logger.timeEnd('测试计时');

      expect(timeSpy).toHaveBeenCalled();
      expect(timeEndSpy).toHaveBeenCalled();
    });
  });

  describe('配置', () => {
    it('应该支持更新配置', () => {
      const logger = createLogger('Test', { level: LogLevel.INFO });
      const consoleSpy = vi.spyOn(console, 'groupCollapsed');

      logger.debug('不应该显示');
      expect(consoleSpy).not.toHaveBeenCalled();

      logger.setLevel(LogLevel.DEBUG);
      logger.debug('应该显示');
      expect(consoleSpy).toHaveBeenCalled();
    });

    it('应该支持自定义前缀', () => {
      const logger = createLogger('Test', { prefix: 'MyApp' });
      expect(logger).toBeInstanceOf(Logger);
    });
  });

  describe('全局 log 对象', () => {
    it('应该提供便捷的全局方法', () => {
      expect(log.debug).toBeDefined();
      expect(log.info).toBeDefined();
      expect(log.success).toBeDefined();
      expect(log.warn).toBeDefined();
      expect(log.error).toBeDefined();
      expect(log.api).toBeDefined();
      expect(log.router).toBeDefined();
      expect(log.store).toBeDefined();
    });
  });
});
