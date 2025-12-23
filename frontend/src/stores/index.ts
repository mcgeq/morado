/**
 * Pinia Store Configuration
 *
 * Central configuration and export for all Pinia stores.
 * This file sets up Pinia and exports all store modules.
 */

import { createPinia } from 'pinia';

// Create and export Pinia instance
export const pinia = createPinia();

export { useApiDefinitionStore } from './apiDefinition';
export { useBodyStore } from './body';
export { useComponentStore } from './component';
export { useHeaderStore } from './header';
export { useScriptStore } from './script';
export { useTestCaseStore } from './testCase';
// Export all stores
export { useUserStore } from './user';

// Export default pinia instance
export default pinia;
