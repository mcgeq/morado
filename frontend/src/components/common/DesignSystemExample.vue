<!--
  Design System Example Component
  
  This component demonstrates how to use the design system utilities.
  It's for documentation purposes and can be used as a reference.
-->

<template>
  <div class="design-system-example space-y-6">
    <!-- Example 1: Using CSS Classes -->
    <section>
      <h2 class="text-2xl font-bold mb-4">Using CSS Classes</h2>

      <div class="widget widget-hoverable">
        <div class="widget-header">
          <h3 class="widget-title">Widget with CSS Classes</h3>
          <p class="widget-subtitle">This uses utility classes from widgets.css</p>
        </div>
        <p class="text-gray-600">
          This widget uses the <code>widget</code>and <code>widget-hoverable</code>classes for
          consistent styling.
        </p>
      </div>
    </section>

    <!-- Example 2: Using Composable -->
    <section>
      <h2 class="text-2xl font-bold mb-4">Using Composable</h2>

      <div :class="widgetClasses" :style="widgetStyle">
        <div :style="headerStyle">
          <h3>Widget with Composable</h3>
          <p class="text-sm text-gray-500 mt-1">This uses the useWidgetStyles composable</p>
        </div>
        <p class="text-gray-600">
          This widget uses the <code>useWidgetStyles()</code>composable for programmatic styling.
        </p>
      </div>
    </section>

    <!-- Example 3: Design Tokens -->
    <section>
      <h2 class="text-2xl font-bold mb-4">Design Tokens</h2>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- Spacing -->
        <div class="card">
          <h4 class="font-semibold mb-3">Spacing</h4>
          <div class="space-y-2">
            <div v-for="(value, key) in spacingExamples" :key="key" class="flex items-center">
              <div class="bg-blue-500 mr-2" :style="{ width: value, height: '1rem' }" />
              <span class="text-sm">{{ key }}: {{ value }}</span>
            </div>
          </div>
        </div>

        <!-- Colors -->
        <div class="card">
          <h4 class="font-semibold mb-3">Colors</h4>
          <div class="space-y-2">
            <div v-for="(color, name) in colorExamples" :key="name" class="flex items-center">
              <div
                class="w-8 h-8 rounded mr-2 border border-gray-200"
                :style="{ backgroundColor: color }"
              />
              <span class="text-sm">{{ name }}</span>
            </div>
          </div>
        </div>

        <!-- Shadows -->
        <div class="card">
          <h4 class="font-semibold mb-3">Shadows</h4>
          <div class="space-y-3">
            <div
              v-for="(shadow, name) in shadowExamples"
              :key="name"
              class="bg-white p-3 rounded"
              :style="{ boxShadow: shadow }"
            >
              <span class="text-sm">{{ name }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Example 4: Typography -->
    <section>
      <h2 class="text-2xl font-bold mb-4">Typography</h2>

      <div class="card space-y-3">
        <div v-for="(style, name) in typographyExamples" :key="name">
          <p :style="style">{{ name }}- The quick brown fox jumps over the lazy dog</p>
        </div>
      </div>
    </section>

    <!-- Example 5: Empty State -->
    <section>
      <h2 class="text-2xl font-bold mb-4">Empty State</h2>

      <div class="widget">
        <div class="empty-state">
          <svg class="empty-state-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <p class="empty-state-text">No data available</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
  import { useWidgetStyles } from '@/composables/useWidgetStyles';
  import { colors, componentShadows, spacing, typography } from '@/styles/design-system';

  // Use the composable
  const { widgetClasses, widgetStyle, headerStyle } = useWidgetStyles({
    hoverable: true,
    minHeight: '200px',
  });

  // Examples for display
  const spacingExamples = {
    xs: spacing.xs,
    sm: spacing.sm,
    md: spacing.md,
    lg: spacing.lg,
    xl: spacing.xl,
  };

  const colorExamples = {
    blue: colors.blue,
    green: colors.green,
    orange: colors.orange,
    red: colors.red,
    purple: colors.purple,
  };

  const shadowExamples = {
    sm: componentShadows.card,
    md: componentShadows.cardHover,
    lg: componentShadows.dropdown,
  };

  const typographyExamples = {
    h1: typography.h1,
    h2: typography.h2,
    h3: typography.h3,
    body: typography.body,
    caption: typography.caption,
  };
</script>

<style scoped>
  .design-system-example {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
  }

  code {
    background-color: #f3f4f6;
    padding: 0.125rem 0.375rem;
    border-radius: 0.25rem;
    font-family: monospace;
    font-size: 0.875rem;
  }
</style>
