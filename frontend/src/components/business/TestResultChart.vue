<template>
  <div class="card bg-base-100 shadow-md">
    <div class="card-body">
      <!-- Header -->
      <div class="flex items-center justify-between mb-4">
        <h3 class="card-title">{{ title }}</h3>
        <div class="flex gap-2">
          <button
            v-for="view in chartViews"
            :key="view"
            type="button"
            class="btn btn-sm"
            :class="currentView === view ? 'btn-primary' : 'btn-ghost'"
            @click="currentView = view"
          >
            {{ view }}
          </button>
        </div>
      </div>

      <!-- Summary Stats -->
      <div class="grid grid-cols-4 gap-4 mb-6">
        <div class="stat bg-base-200 rounded-lg p-4">
          <div class="stat-title text-xs">Total</div>
          <div class="stat-value text-2xl">{{ totalTests }}</div>
          <div class="stat-desc">Test Cases</div>
        </div>
        <div class="stat bg-success/10 rounded-lg p-4">
          <div class="stat-title text-xs text-success">Passed</div>
          <div class="stat-value text-2xl text-success">{{ passedTests }}</div>
          <div class="stat-desc">{{ passRate }}%</div>
        </div>
        <div class="stat bg-error/10 rounded-lg p-4">
          <div class="stat-title text-xs text-error">Failed</div>
          <div class="stat-value text-2xl text-error">{{ failedTests }}</div>
          <div class="stat-desc">{{ failRate }}%</div>
        </div>
        <div class="stat bg-warning/10 rounded-lg p-4">
          <div class="stat-title text-xs text-warning">Skipped</div>
          <div class="stat-value text-2xl text-warning">{{ skippedTests }}</div>
          <div class="stat-desc">{{ skipRate }}%</div>
        </div>
      </div>

      <!-- Chart View -->
      <div v-if="currentView === 'Bar'" class="space-y-3">
        <div v-for="result in results" :key="result.id" class="space-y-1">
          <div class="flex items-center justify-between text-sm">
            <span class="font-medium truncate flex-1">{{ result.name }}</span>
            <span class="text-xs text-base-content/60">{{ result.duration }}ms</span>
          </div>
          <div class="flex gap-1 h-6">
            <div
              v-if="result.passed > 0"
              class="bg-success rounded flex items-center justify-center text-xs text-success-content font-semibold"
              :style="{ width: `${(result.passed / result.total) * 100}%` }"
            >
              {{ result.passed }}
            </div>
            <div
              v-if="result.failed > 0"
              class="bg-error rounded flex items-center justify-center text-xs text-error-content font-semibold"
              :style="{ width: `${(result.failed / result.total) * 100}%` }"
            >
              {{ result.failed }}
            </div>
            <div
              v-if="result.skipped > 0"
              class="bg-warning rounded flex items-center justify-center text-xs text-warning-content font-semibold"
              :style="{ width: `${(result.skipped / result.total) * 100}%` }"
            >
              {{ result.skipped }}
            </div>
          </div>
        </div>
      </div>

      <!-- Pie Chart View -->
      <div v-else-if="currentView === 'Pie'" class="flex items-center justify-center">
        <div class="radial-progress-container flex flex-col items-center gap-4">
          <div
            class="radial-progress text-primary"
            :style="`--value:${passRate}; --size:12rem; --thickness: 1.5rem;`"
            role="progressbar"
          >
            <div class="text-center">
              <div class="text-3xl font-bold">{{ passRate }}%</div>
              <div class="text-xs text-base-content/60">Pass Rate</div>
            </div>
          </div>
          <div class="flex gap-4 text-sm">
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded-full bg-success"></div>
              <span>Passed: {{ passedTests }}</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded-full bg-error"></div>
              <span>Failed: {{ failedTests }}</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded-full bg-warning"></div>
              <span>Skipped: {{ skippedTests }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- List View -->
      <div v-else-if="currentView === 'List'" class="space-y-2">
        <div
          v-for="result in results"
          :key="result.id"
          class="card bg-base-200 hover:bg-base-300 transition-colors cursor-pointer"
          @click="$emit('selectResult', result)"
        >
          <div class="card-body p-3">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3 flex-1">
                <div
                  class="w-2 h-2 rounded-full"
                  :class="{
                    'bg-success': result.status === 'passed',
                    'bg-error': result.status === 'failed',
                    'bg-warning': result.status === 'skipped',
                  }"
                ></div>
                <div class="flex-1">
                  <div class="font-medium text-sm">{{ result.name }}</div>
                  <div class="text-xs text-base-content/60">
                    {{ formatDate(result.executed_at) }}
                  </div>
                </div>
              </div>
              <div class="flex items-center gap-4">
                <div class="text-right">
                  <div class="text-xs text-base-content/60">Duration</div>
                  <div class="text-sm font-semibold">{{ result.duration }}ms</div>
                </div>
                <div class="badge badge-sm" :class="getStatusBadge(result.status)">
                  {{ result.status }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="results.length === 0" class="text-center py-12">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-base-content/20 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        <p class="text-base-content/60">No test results available</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';

interface TestResult {
  id: number;
  name: string;
  status: 'passed' | 'failed' | 'skipped';
  duration: number;
  executed_at: string;
  total: number;
  passed: number;
  failed: number;
  skipped: number;
}

interface Props {
  results: TestResult[];
  title?: string;
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Test Results',
});

defineEmits<{
  selectResult: [result: TestResult];
}>();

const chartViews = ['Bar', 'Pie', 'List'] as const;
const currentView = ref<typeof chartViews[number]>('Bar');

const totalTests = computed(() => {
  return props.results.reduce((sum, r) => sum + r.total, 0);
});

const passedTests = computed(() => {
  return props.results.reduce((sum, r) => sum + r.passed, 0);
});

const failedTests = computed(() => {
  return props.results.reduce((sum, r) => sum + r.failed, 0);
});

const skippedTests = computed(() => {
  return props.results.reduce((sum, r) => sum + r.skipped, 0);
});

const passRate = computed(() => {
  if (totalTests.value === 0) return 0;
  return Math.round((passedTests.value / totalTests.value) * 100);
});

const failRate = computed(() => {
  if (totalTests.value === 0) return 0;
  return Math.round((failedTests.value / totalTests.value) * 100);
});

const skipRate = computed(() => {
  if (totalTests.value === 0) return 0;
  return Math.round((skippedTests.value / totalTests.value) * 100);
});

function getStatusBadge(status: string): string {
  switch (status) {
    case 'passed':
      return 'badge-success';
    case 'failed':
      return 'badge-error';
    case 'skipped':
      return 'badge-warning';
    default:
      return 'badge-ghost';
  }
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays} days ago`;
  return date.toLocaleDateString();
}
</script>
