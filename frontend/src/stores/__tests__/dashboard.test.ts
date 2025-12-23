/**
 * Dashboard Store Tests
 *
 * Unit tests for the dashboard store functionality.
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useDashboardStore, isCacheValid, setCacheData, getCacheData, clearCache } from '../dashboard';

describe('Dashboard Store', () => {
  beforeEach(() => {
    // Create a fresh pinia instance for each test
    setActivePinia(createPinia());
    // Clear localStorage before each test
    localStorage.clear();
  });

  describe('Cache Utilities', () => {
    it('should return false for invalid cache when no data exists', () => {
      expect(isCacheValid()).toBe(false);
    });

    it('should return true for valid cache within 5 minutes', () => {
      const userData = {
        id: '1',
        username: 'test',
        avatar: null,
        registrationDate: '2024-01-01',
        metrics: {
          totalExecutions: 10,
          passedTests: 8,
          failedTests: 2,
        },
      };

      const statistics = {
        steps: { completed: 5, sqlFailed: 2, apiRequest: 3 },
        apiUsage: {
          apiCompletion: {
            percentage: 80,
            totalApis: 10,
            completedApis: 8,
            taggedApis: 6,
          },
          testCaseCompletion: {
            percentage: 90,
            totalTestCases: 20,
            passedTestCases: 18,
            taggedTestCases: 15,
          },
        },
        trends: [],
      };

      setCacheData(userData, statistics);
      expect(isCacheValid()).toBe(true);
    });

    it('should return cached data when valid', () => {
      const userData = {
        id: '1',
        username: 'test',
        avatar: null,
        registrationDate: '2024-01-01',
        metrics: {
          totalExecutions: 10,
          passedTests: 8,
          failedTests: 2,
        },
      };

      const statistics = {
        steps: { completed: 5, sqlFailed: 2, apiRequest: 3 },
        apiUsage: {
          apiCompletion: {
            percentage: 80,
            totalApis: 10,
            completedApis: 8,
            taggedApis: 6,
          },
          testCaseCompletion: {
            percentage: 90,
            totalTestCases: 20,
            passedTestCases: 18,
            taggedTestCases: 15,
          },
        },
        trends: [],
      };

      setCacheData(userData, statistics);
      const cached = getCacheData();

      expect(cached).not.toBeNull();
      expect(cached?.userData.username).toBe('test');
      expect(cached?.statistics.steps.completed).toBe(5);
    });

    it('should clear cache data', () => {
      const userData = {
        id: '1',
        username: 'test',
        avatar: null,
        registrationDate: '2024-01-01',
        metrics: {
          totalExecutions: 10,
          passedTests: 8,
          failedTests: 2,
        },
      };

      const statistics = {
        steps: { completed: 5, sqlFailed: 2, apiRequest: 3 },
        apiUsage: {
          apiCompletion: {
            percentage: 80,
            totalApis: 10,
            completedApis: 8,
            taggedApis: 6,
          },
          testCaseCompletion: {
            percentage: 90,
            totalTestCases: 20,
            passedTestCases: 18,
            taggedTestCases: 15,
          },
        },
        trends: [],
      };

      setCacheData(userData, statistics);
      clearCache();
      expect(getCacheData()).toBeNull();
    });
  });

  describe('Store State', () => {
    it('should initialize with default state', () => {
      const store = useDashboardStore();

      expect(store.loading).toBe(false);
      expect(store.error).toBeNull();
      expect(store.lastUpdated).toBeNull();
      expect(store.userData).toBeNull();
      expect(store.statistics).toBeNull();
    });

    it('should have computed properties', () => {
      const store = useDashboardStore();

      expect(store.hasData).toBe(false);
      expect(store.isError).toBe(false);
    });

    it('should clear error', () => {
      const store = useDashboardStore();
      store.error = 'Test error';

      store.clearError();
      expect(store.error).toBeNull();
    });

    it('should reset store state', () => {
      const store = useDashboardStore();
      store.loading = true;
      store.error = 'Test error';

      store.reset();

      expect(store.loading).toBe(false);
      expect(store.error).toBeNull();
      expect(store.userData).toBeNull();
      expect(store.statistics).toBeNull();
    });
  });
});
