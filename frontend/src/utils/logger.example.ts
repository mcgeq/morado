/**
 * Logger 使用示例
 *
 * 本文件展示了如何在 Morado 前端项目中使用规范化的日志工具
 */

import { createLogger, LogLevel, log, logger } from './logger';

/**
 * 示例 1: 使用全局 logger 实例
 */
export function example1() {
  // 基本日志
  logger.debug('这是一条调试信息');
  logger.info('这是一条普通信息');
  logger.success('操作成功！');
  logger.warn('这是一条警告信息');
  logger.error('这是一条错误信息');

  // 带数据的日志
  logger.info('用户登录成功', {
    用户名: 'testuser',
    角色: 'developer',
    登录时间: new Date().toISOString(),
  });

  // API 请求日志
  logger.api('GET', '/api/v1/users', {
    params: { page: 1, limit: 10 },
  });

  // 路由导航日志
  logger.router('/home', '/test-cases', {
    from: 'Home',
    to: 'TestCaseList',
  });

  // Store 状态变更日志
  logger.store('用户登录', {
    action: 'login',
    payload: { username: 'testuser' },
  });
}

/**
 * 示例 2: 使用便捷的全局 log 对象
 */
export function example2() {
  log.info('使用便捷的 log 对象');
  log.success('操作完成');
  log.warn('注意事项');
  log.error('发生错误');
}

/**
 * 示例 3: 创建特定上下文的 Logger
 */
export function example3() {
  // 为特定模块创建 logger
  const apiLogger = createLogger('API');
  const storeLogger = createLogger('Store');
  const componentLogger = createLogger('Component');

  apiLogger.info('API 模块初始化');
  storeLogger.info('Store 模块初始化');
  componentLogger.info('组件已挂载');
}

/**
 * 示例 4: 使用分组日志
 */
export function example4() {
  logger.group('用户操作流程');
  logger.info('步骤 1: 验证用户输入');
  logger.info('步骤 2: 发送 API 请求');
  logger.info('步骤 3: 更新 UI 状态');
  logger.groupEnd();
}

/**
 * 示例 5: 性能计时
 */
export async function example5() {
  logger.time('数据加载');

  // 模拟异步操作
  await new Promise(resolve => setTimeout(resolve, 1000));

  logger.timeEnd('数据加载');
}

/**
 * 示例 6: 在组件中使用
 */
export function componentExample() {
  // 在 Vue 组件的 setup 中
  const logger = createLogger('TestCaseList');

  // 组件生命周期
  logger.debug('组件已创建');

  // 数据加载
  logger.time('加载测试用例列表');
  // ... 加载数据
  logger.timeEnd('加载测试用例列表');

  // 用户操作
  const handleCreate = () => {
    logger.info('用户点击创建按钮');
  };

  const handleDelete = (id: number) => {
    logger.warn('用户删除测试用例', { id });
  };

  return { handleCreate, handleDelete };
}

/**
 * 示例 7: 在 API 客户端中使用
 */
export class ApiClient {
  private logger = createLogger('ApiClient');

  async get(url: string, params?: Record<string, unknown>) {
    this.logger.api('GET', url, params);

    try {
      // 发送请求
      const response = await fetch(url);
      const data = await response.json();

      this.logger.success('请求成功', { url, data });
      return data;
    } catch (error) {
      this.logger.error('请求失败', { url, error });
      throw error;
    }
  }
}

/**
 * 示例 8: 在 Store 中使用
 */
export function storeExample() {
  const logger = createLogger('UserStore');

  const login = async (username: string, _password: string) => {
    logger.info('开始登录', { username });

    try {
      // 登录逻辑
      logger.success('登录成功', { username });
    } catch (error) {
      logger.error('登录失败', { username, error });
      throw error;
    }
  };

  return { login };
}

/**
 * 示例 9: 配置日志级别
 */
export function example9() {
  // 创建只显示警告和错误的 logger
  const prodLogger = createLogger('Production', {
    level: LogLevel.WARN,
    enableTimestamp: true,
    enableStackTrace: true,
  });

  prodLogger.debug('这条不会显示'); // 不会显示
  prodLogger.info('这条也不会显示'); // 不会显示
  prodLogger.warn('这条会显示'); // 会显示
  prodLogger.error('这条也会显示'); // 会显示
}

/**
 * 示例 10: 子 Logger
 */
export function example10() {
  const parentLogger = createLogger('Parent');
  const childLogger = parentLogger.child('Child');

  parentLogger.info('父级日志'); // [Parent] 父级日志
  childLogger.info('子级日志'); // [Parent:Child] 子级日志
}

/**
 * 示例 11: 错误处理最佳实践
 */
export async function example11() {
  const logger = createLogger('ErrorHandling');

  try {
    // 可能抛出错误的操作
    throw new Error('模拟错误');
  } catch (error) {
    // 记录详细的错误信息
    logger.error('操作失败', {
      error,
      message: error instanceof Error ? error.message : '未知错误',
      stack: error instanceof Error ? error.stack : undefined,
      timestamp: new Date().toISOString(),
    });
  }
}

/**
 * 示例 12: 在路由守卫中使用
 */
export function routerGuardExample() {
  const logger = createLogger('RouterGuard');

  return (to: { path: string; name?: string }, from: { path: string; name?: string }) => {
    logger.router(from.path, to.path, {
      from: from.name,
      to: to.name,
    });

    // 权限检查
    const hasPermission = true; // 实际的权限检查逻辑
    if (!hasPermission) {
      logger.warn('权限不足，拒绝访问', {
        path: to.path,
        name: to.name,
      });
      return false;
    }

    return true;
  };
}
