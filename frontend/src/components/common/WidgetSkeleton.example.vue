<template>
  <div class="widget-skeleton-examples p-8 space-y-8 bg-gray-50">
    <h1 class="text-3xl font-bold text-gray-900 mb-8">WidgetSkeleton Component Examples</h1>

    <!-- Example 1: Profile Skeleton -->
    <section class="example-section">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">1. Profile Widget Skeleton</h2>
      <WidgetSkeleton type="profile" />
    </section>

    <!-- Example 2: Chart Skeleton -->
    <section class="example-section">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">2. Chart Widget Skeleton</h2>
      <WidgetSkeleton type="chart" />
    </section>

    <!-- Example 3: Stats Skeleton -->
    <section class="example-section">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">3. Stats Widget Skeleton</h2>
      <WidgetSkeleton type="stats" />
    </section>

    <!-- Example 4: Trend Skeleton -->
    <section class="example-section">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">4. Trend Widget Skeleton</h2>
      <WidgetSkeleton type="trend" />
    </section>

    <!-- Example 5: Actions Skeleton -->
    <section class="example-section">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">5. Actions Widget Skeleton</h2>
      <WidgetSkeleton type="actions" />
    </section>

    <!-- Example 6: Default Skeleton -->
    <section class="example-section">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">6. Default Widget Skeleton</h2>
      <WidgetSkeleton type="default" />
    </section>

    <!-- Example 7: Grid Layout -->
    <section class="example-section">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">
        7. Grid Layout with Multiple Skeletons
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <WidgetSkeleton type="chart" />
        <WidgetSkeleton type="stats" />
        <div class="lg:col-span-3">
          <WidgetSkeleton type="trend" />
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
  import WidgetSkeleton from './WidgetSkeleton.vue';
</script>

<style scoped>
  .example-section {
    background: white;
    padding: 1.5rem;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
</style>
