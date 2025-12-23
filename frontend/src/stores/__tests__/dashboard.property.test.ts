/**
 * Dashboard Store Property-Based Tests
 *
 * Property-based tests using fast-check to verify dashboard store behavior.
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import * as fc from 'fast-check';
import { setCacheData, getCacheData, isCacheValid, clearCache } from '../dashboard';

describe('Dashboard Store Property Tests', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();
  });

  /**
   * Feature: home-dashboard, Property 6: Cache freshness validation
   * Validates: Requirements 7.4, 7.5
   */
  it('cache should be invalidated after 5 minutes', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 0, max: 10 }), // minutes elapsed
        fc.record({
          userData: fc.record({
            id: fc.string(),
            username: fc.string(),
            avatar: fc.oneof(fc.string(), fc.constant(null)),
            registrationDate: fc.string(),
            metrics: fc.record({
              totalExecutions: fc.nat(),
              passedTests: fc.nat(),
              failedTests: fc.nat(),
            }),
          }),
          statistics: fc.record({
            steps: fc.record({
              completed: fc.nat(),
              sqlFailed: fc.nat(),
              apiRequest: fc.nat(),
            }),
            apiUsage: fc.record({
              apiCompletion: fc.record({
                percentage: fc.nat(100),
                totalApis: fc.nat(),
                completedApis: fc.nat(),
                taggedApis: fc.nat(),
              }),
              testCaseCompletion: fc.record({
                percentage: fc.nat(100),
                totalTestCases: fc.nat(),
                passedTestCases: fc.nat(),
                taggedTestCases: fc.nat(),
              }),
            }),
            trends: fc.array(
              fc.record({
                date: fc.string(),
                scheduledComponents: fc.nat(),
                testCaseComponents: fc.nat(),
                actualComponents: fc.nat(),
                detectionComponents: fc.nat(),
              })
            ),
          }),
        }),
        (minutesElapsed, cachedData) => {
          // Clear cache before each iteration
          clearCache();

          // Set cache with a timestamp in the past
          const cacheTimestamp = Date.now() - minutesElapsed * 60 * 1000;
          localStorage.setItem(
            'dashboard_cache',
            JSON.stringify({
              ...cachedData,
              timestamp: cacheTimestamp,
            })
          );

          const shouldUseFreshData = minutesElapsed > 5;
          const cacheIsValid = isCacheValid();

          // If more than 5 minutes have elapsed, cache should be invalid
          // If less than 5 minutes, cache should be valid
          // At exactly 5 minutes, the behavior depends on milliseconds precision
          if (minutesElapsed === 5) {
            // At exactly 5 minutes, we accept either valid or invalid
            return true;
          }
          return shouldUseFreshData ? !cacheIsValid : cacheIsValid;
        }
      ),
      { numRuns: 100 }
    );
  });

  it('cached data should round-trip correctly', () => {
    fc.assert(
      fc.property(
        fc.record({
          userData: fc.record({
            id: fc.string(),
            username: fc.string(),
            avatar: fc.oneof(fc.string(), fc.constant(null)),
            registrationDate: fc.string(),
            metrics: fc.record({
              totalExecutions: fc.nat(),
              passedTests: fc.nat(),
              failedTests: fc.nat(),
            }),
          }),
          statistics: fc.record({
            steps: fc.record({
              completed: fc.nat(),
              sqlFailed: fc.nat(),
              apiRequest: fc.nat(),
            }),
            apiUsage: fc.record({
              apiCompletion: fc.record({
                percentage: fc.nat(100),
                totalApis: fc.nat(),
                completedApis: fc.nat(),
                taggedApis: fc.nat(),
              }),
              testCaseCompletion: fc.record({
                percentage: fc.nat(100),
                totalTestCases: fc.nat(),
                passedTestCases: fc.nat(),
                taggedTestCases: fc.nat(),
              }),
            }),
            trends: fc.array(
              fc.record({
                date: fc.string(),
                scheduledComponents: fc.nat(),
                testCaseComponents: fc.nat(),
                actualComponents: fc.nat(),
                detectionComponents: fc.nat(),
              })
            ),
          }),
        }),
        data => {
          // Clear cache before each iteration
          clearCache();

          // Set cache data
          setCacheData(data.userData, data.statistics);

          // Get cache data
          const cached = getCacheData();

          // Verify data round-trips correctly
          return (
            cached !== null &&
            cached.userData.id === data.userData.id &&
            cached.userData.username === data.userData.username &&
            cached.statistics.steps.completed === data.statistics.steps.completed
          );
        }
      ),
      { numRuns: 100 }
    );
  });
});
