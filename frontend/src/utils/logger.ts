/**
 * Logger Utility
 *
 * 规范化的日志工具，提供更清晰、更易于查看的日志输出
 * 支持不同级别的日志、颜色标识、时间戳、上下文信息等
 */

/**
 * 日志级别类型
 */
export const LogLevel = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3,
  NONE: 4,
} as const;

export type LogLevel = (typeof LogLevel)[keyof typeof LogLevel];

/**
 * 日志配置接口
 */
export interface LoggerConfig {
  level: LogLevel;
  enableTimestamp: boolean;
  enableStackTrace: boolean;
  prefix?: string;
}

/**
 * 日志样式配置
 */
const LOG_STYLES = {
  debug: {
    icon: '🔍',
    color: '#6B7280', // gray-500
    bgColor: '#F3F4F6', // gray-100
  },
  info: {
    icon: 'ℹ️',
    color: '#0EA5E9', // blue-500
    bgColor: '#E0F2FE', // blue-100
  },
  success: {
    icon: '✅',
    color: '#10B981', // green-500
    bgColor: '#D1FAE5', // green-100
  },
  warn: {
    icon: '⚠️',
    color: '#F59E0B', // amber-500
    bgColor: '#FEF3C7', // amber-100
  },
  error: {
    icon: '❌',
    color: '#EF4444', // red-500
    bgColor: '#FEE2E2', // red-100
  },
  api: {
    icon: '🌐',
    color: '#8B5CF6', // purple-500
    bgColor: '#EDE9FE', // purple-100
  },
  router: {
    icon: '🧭',
    color: '#EC4899', // pink-500
    bgColor: '#FCE7F3', // pink-100
  },
  store: {
    icon: '📦',
    color: '#14B8A6', // teal-500
    bgColor: '#CCFBF1', // teal-100
  },
};

/**
 * Logger 类
 */
class Logger {
  private config: LoggerConfig;
  private context: string;

  constructor(context = 'App', config?: Partial<LoggerConfig>) {
    this.context = context;
    this.config = {
      level: import.meta.env.DEV ? LogLevel.DEBUG : LogLevel.INFO,
      enableTimestamp: true,
      enableStackTrace: false,
      ...config,
    };
  }

  /**
   * 获取格式化的时间戳
   */
  private getTimestamp(): string {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    const ms = String(now.getMilliseconds()).padStart(3, '0');
    return `${hours}:${minutes}:${seconds}.${ms}`;
  }

  /**
   * 格式化日志消息
   */
  private formatMessage(level: keyof typeof LOG_STYLES, message: string, data?: unknown): void {
    if (this.config.level === LogLevel.NONE) return;

    const style = LOG_STYLES[level];
    const timestamp = this.config.enableTimestamp ? `[${this.getTimestamp()}]` : '';
    const prefix = this.config.prefix ? `[${this.config.prefix}]` : '';
    const context = `[${this.context}]`;

    // 构建样式字符串
    const labelStyle = `
      background: ${style.bgColor};
      color: ${style.color};
      font-weight: bold;
      padding: 2px 6px;
      border-radius: 3px;
    `;

    const timestampStyle = `
      color: #9CA3AF;
      font-size: 0.9em;
    `;

    const contextStyle = `
      color: #6B7280;
      font-weight: 600;
    `;

    // 输出日志
    console.groupCollapsed(
      `%c${style.icon} ${level.toUpperCase()}%c ${timestamp} %c${prefix}${context}%c ${message}`,
      labelStyle,
      timestampStyle,
      contextStyle,
      'color: inherit',
    );

    // 如果有数据，输出数据
    if (data !== undefined) {
      if (typeof data === 'object' && data !== null) {
        console.table(data);
      } else {
        console.log(data);
      }
    }

    // 如果启用堆栈跟踪，输出堆栈
    if (this.config.enableStackTrace && (level === 'error' || level === 'warn')) {
      console.trace('Stack trace:');
    }

    console.groupEnd();
  }

  /**
   * Debug 级别日志
   */
  debug(message: string, data?: unknown): void {
    if (this.config.level <= LogLevel.DEBUG) {
      this.formatMessage('debug', message, data);
    }
  }

  /**
   * Info 级别日志
   */
  info(message: string, data?: unknown): void {
    if (this.config.level <= LogLevel.INFO) {
      this.formatMessage('info', message, data);
    }
  }

  /**
   * Success 日志（特殊的 info 级别）
   */
  success(message: string, data?: unknown): void {
    if (this.config.level <= LogLevel.INFO) {
      this.formatMessage('success', message, data);
    }
  }

  /**
   * Warn 级别日志
   */
  warn(message: string, data?: unknown): void {
    if (this.config.level <= LogLevel.WARN) {
      this.formatMessage('warn', message, data);
    }
  }

  /**
   * Error 级别日志
   */
  error(message: string, error?: unknown): void {
    if (this.config.level <= LogLevel.ERROR) {
      this.formatMessage('error', message, error);
    }
  }

  /**
   * API 请求日志
   */
  api(method: string, url: string, data?: unknown): void {
    if (this.config.level <= LogLevel.DEBUG) {
      this.formatMessage('api', `${method.toUpperCase()} ${url}`, data);
    }
  }

  /**
   * 路由导航日志
   */
  router(from: string, to: string, data?: unknown): void {
    if (this.config.level <= LogLevel.DEBUG) {
      this.formatMessage('router', `${from} → ${to}`, data);
    }
  }

  /**
   * Store 状态变更日志
   */
  store(action: string, data?: unknown): void {
    if (this.config.level <= LogLevel.DEBUG) {
      this.formatMessage('store', action, data);
    }
  }

  /**
   * 分组日志开始
   */
  group(label: string): void {
    if (this.config.level !== LogLevel.NONE) {
      console.group(`📂 ${label}`);
    }
  }

  /**
   * 分组日志结束
   */
  groupEnd(): void {
    if (this.config.level !== LogLevel.NONE) {
      console.groupEnd();
    }
  }

  /**
   * 性能计时开始
   */
  time(label: string): void {
    if (this.config.level <= LogLevel.DEBUG) {
      console.time(`⏱️ ${label}`);
    }
  }

  /**
   * 性能计时结束
   */
  timeEnd(label: string): void {
    if (this.config.level <= LogLevel.DEBUG) {
      console.timeEnd(`⏱️ ${label}`);
    }
  }

  /**
   * 创建子 Logger
   */
  child(context: string): Logger {
    return new Logger(`${this.context}:${context}`, this.config);
  }

  /**
   * 更新配置
   */
  setConfig(config: Partial<LoggerConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /**
   * 设置日志级别
   */
  setLevel(level: LogLevel): void {
    this.config.level = level;
  }
}

/**
 * 创建默认 Logger 实例
 */
export const logger = new Logger('Morado');

/**
 * 创建特定上下文的 Logger
 */
export function createLogger(context: string, config?: Partial<LoggerConfig>): Logger {
  return new Logger(context, config);
}

/**
 * 便捷的全局日志方法
 */
export const log = {
  debug: (message: string, data?: unknown) => logger.debug(message, data),
  info: (message: string, data?: unknown) => logger.info(message, data),
  success: (message: string, data?: unknown) => logger.success(message, data),
  warn: (message: string, data?: unknown) => logger.warn(message, data),
  error: (message: string, error?: unknown) => logger.error(message, error),
  api: (method: string, url: string, data?: unknown) => logger.api(method, url, data),
  router: (from: string, to: string, data?: unknown) => logger.router(from, to, data),
  store: (action: string, data?: unknown) => logger.store(action, data),
  group: (label: string) => logger.group(label),
  groupEnd: () => logger.groupEnd(),
  time: (label: string) => logger.time(label),
  timeEnd: (label: string) => logger.timeEnd(label),
};

/**
 * 导出 Logger 类供高级使用
 */
export { Logger };

/**
 * 默认导出
 */
export default logger;
