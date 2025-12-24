<template>
  <div class="loading-state-examples p-8 space-y-8 bg-gray-50">
    <h1 class="text-3xl font-bold text-gray-900 mb-8">LoadingState Component Examples</h1>

    <!-- Example 1: Full Dashboard Loading -->
    <section class="example-section">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">1. Full Dashboard Loading</h2>
      <LoadingState :full-dashboard="true" />
    </section>

    <!-- Example 2: Profile Card Loading -->
    <section class="example-section">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">2. Profile Card Loading</h2>
      <LoadingState :full-dashboard="false" :show-profile="true" />
    </section>

    <!-- Example 3: Quick Actions Loading -->
    <section class="example-section">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">3. Quick Actions Loading</h2>
      <LoadingState :full-dashboard="false" :show-quick-actions="true" />
    </section>

    <!-- Example 4: Statistics Grid Loading -->
    <section class="example-section">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">4. Statistics Grid Loading</h2>
      <LoadingState
        :full-dashboard="false"
        :show-statistics="true"
        :show-steps-stats="true"
        :show-api-usage="true"
        :show-trends="true"
      />
    </section>

    <!-- Example 5: With Loading Text -->
    <section class="example-section">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">5. With Loading Text</h2>
      <LoadingState
        :full-dashboard="true"
        :show-loading-text="true"
        loading-text="正在加载仪表板数据..."
      />
    </section>

    <!-- Example 6: Header and Profile Only -->
    <section class="example-section">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">6. Header and Profile Only</h2>
      <LoadingState :full-dashboard="false" :show-header="true" :show-profile="true" />
    </section>
  </div>
</template>

<script setup lang="ts">
  import LoadingState from './LoadingState.vue';
</script>

<style scoped>
  .example-section {
    background: white;
    padding: 1.5rem;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
</style>
