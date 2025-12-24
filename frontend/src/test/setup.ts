/**
 * Vitest Test Setup
 *
 * Global test configuration and setup for the dashboard tests.
 */

import { cleanup } from '@testing-library/vue';
import { LineChart, PieChart } from 'echarts/charts';
import {
  GridComponent,
  LegendComponent,
  TitleComponent,
  TooltipComponent,
} from 'echarts/components';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { afterEach, beforeEach, expect, vi } from 'vitest';
import { config } from '@vue/test-utils';
import { createI18n } from 'vue-i18n';

// Register ECharts components for tests
use([
  CanvasRenderer,
  PieChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
]);

// Create i18n instance for tests
const i18n = createI18n({
  legacy: false,
  locale: 'zh-CN',
  messages: {
    'zh-CN': {
      common: {
        loading: '加载中...',
        refresh: '刷新',
        refreshing: '刷新中...',
        error: '错误',
        retry: '重试',
        noData: '暂无数据',
      },
      dashboard: {
        title: '仪表板',
        userProfile: '用户资料',
        quickActions: '快捷操作',
        statistics: '统计信息',
      },
    },
    'en-US': {
      common: {
        loading: 'Loading...',
        refresh: 'Refresh',
        refreshing: 'Refreshing...',
        error: 'Error',
        retry: 'Retry',
        noData: 'No Data',
      },
      dashboard: {
        title: 'Dashboard',
        userProfile: 'User Profile',
        quickActions: 'Quick Actions',
        statistics: 'Statistics',
      },
    },
  },
});

// Install i18n globally for all tests
config.global.plugins = [i18n];

// Mock HTMLCanvasElement for ECharts tests
beforeEach(() => {
  HTMLCanvasElement.prototype.getContext = vi.fn(() => ({
    fillStyle: '',
    strokeStyle: '',
    lineWidth: 1,
    lineCap: 'butt',
    lineJoin: 'miter',
    miterLimit: 10,
    font: '10px sans-serif',
    textAlign: 'start',
    textBaseline: 'alphabetic',
    fillRect: vi.fn(),
    strokeRect: vi.fn(),
    clearRect: vi.fn(),
    fillText: vi.fn(),
    strokeText: vi.fn(),
    getImageData: vi.fn(),
    putImageData: vi.fn(),
    createImageData: vi.fn(),
    setTransform: vi.fn(),
    drawImage: vi.fn(),
    save: vi.fn(),
    restore: vi.fn(),
    beginPath: vi.fn(),
    moveTo: vi.fn(),
    lineTo: vi.fn(),
    closePath: vi.fn(),
    stroke: vi.fn(),
    fill: vi.fn(),
    translate: vi.fn(),
    scale: vi.fn(),
    rotate: vi.fn(),
    arc: vi.fn(),
    arcTo: vi.fn(),
    quadraticCurveTo: vi.fn(),
    bezierCurveTo: vi.fn(),
    rect: vi.fn(),
    clip: vi.fn(),
    isPointInPath: vi.fn(() => false),
    measureText: vi.fn(() => ({ width: 0, actualBoundingBoxLeft: 0, actualBoundingBoxRight: 0 })),
    transform: vi.fn(),
    setLineDash: vi.fn(),
    getLineDash: vi.fn(() => []),
    createLinearGradient: vi.fn(() => ({
      addColorStop: vi.fn(),
    })),
    createRadialGradient: vi.fn(() => ({
      addColorStop: vi.fn(),
    })),
    createPattern: vi.fn(),
    canvas: {
      width: 300,
      height: 300,
      style: {},
      getContext: vi.fn(),
    },
  })) as any;
});

// Cleanup after each test
afterEach(() => {
  cleanup();
});

// Extend expect with custom matchers if needed
expect.extend({
  // Custom matchers can be added here
});

// Mock localStorage for tests
const localStorageMock = (() => {
  let store: Record<string, string> = {};

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString();
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock window.matchMedia for responsive tests
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {}, // deprecated
    removeListener: () => {}, // deprecated
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => true,
  }),
});

// Mock ResizeObserver for ECharts
globalThis.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};
