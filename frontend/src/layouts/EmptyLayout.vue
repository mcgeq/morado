<template>
  <div class="min-h-screen">
    <!-- Empty layout with no header, footer, or navigation -->
    <!-- Used for pages like login, 404, or full-screen views -->
    <router-view />
  </div>
</template>

<script setup lang="ts">
  /**
   * EmptyLayout Component
   *
   * A minimal layout component that provides no additional UI elements.
   * This layout is useful for:
   * - Login/Authentication pages
   * - 404 Not Found pages
   * - Full-screen views (e.g., presentations, reports)
   * - Landing pages with custom designs
   *
   * The layout simply renders the router-view without any wrapper elements,
   * allowing child components to have complete control over the page layout.
   */
</script>

<style scoped>
  /* No additional styles needed for empty layout */
</style>
