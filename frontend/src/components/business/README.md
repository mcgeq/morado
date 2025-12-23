# Business Components

This directory contains business-specific components for the Morado test platform, organized according to the four-layer architecture.

## Important: Data Format Convention

**All frontend TypeScript code uses camelCase naming convention** (JavaScript/TypeScript standard), while the backend API returns snake_case. Automatic conversion is handled at the API layer:

- **Request interceptor**: Converts camelCase → snake_case before sending to backend
- **Response interceptor**: Converts snake_case → camelCase after receiving from backend
- **Implementation**: See `frontend/src/utils/caseConverter.ts` and `frontend/src/api/index.ts`

This means all Vue components, stores, and TypeScript interfaces use camelCase property names (e.g., `componentType`, `executionMode`, `isActive`), while the backend continues to use snake_case.

## Components Overview

### Layer 1: API Definition Components

#### HeaderCard.vue
Displays a reusable HTTP header component with:
- Header name and description
- Scope badge (global/project/private)
- Preview of header key-value pairs
- Actions: Edit, Duplicate, Delete, Use
- Tags and version information

#### BodyCard.vue
Displays a reusable request/response body template with:
- Body name and description
- Type badge (request/response/both)
- Content-Type display
- Schema and example data preview
- Actions: Edit, Duplicate, Delete, Validate, Use
- Tags and version information

#### ApiDefinitionCard.vue
Displays a complete API interface definition with:
- API name and HTTP method badge
- Full endpoint URL
- Component references (Header, Request Body, Response Body)
- Parameter counts (query and path)
- Actions: Edit, Duplicate, Delete, Test, Use
- Tags and version information

### Layer 2: Test Scripts

#### ScriptCard.vue
Displays a test script that references an API definition with:
- Script name and type badge (setup/main/teardown/utility)
- API definition reference
- Execution order and retry configuration
- Feature badges (variables, assertions, pre/post scripts)
- Actions: Edit, Duplicate, Delete, Execute, Debug
- Tags and version information

#### ScriptDebugger.vue
Interactive debugger for test scripts with:
- Runtime parameter input (JSON format)
- Breakpoint configuration
- Debug controls (start/stop)
- Real-time execution results
- Response data display
- Extracted variables view
- Assertion results with pass/fail status
- Error display

### Layer 3: Test Components

#### ComponentCard.vue
Displays a composite component that combines multiple scripts with:
- Component name and type badge (simple/composite/template)
- Execution mode badge (sequential/parallel/conditional)
- Script count and nesting indicator
- Shared variables preview
- Actions: Edit, Duplicate, Delete, Execute, View Hierarchy
- Tags and version information

#### ComponentTree.vue
Hierarchical tree view for nested components with:
- Root component display
- Child components (recursive)
- Associated scripts with execution order
- Visual hierarchy indicators
- Parameter override indicators
- Interactive selection

### Layer 4: Test Cases

#### TestCaseCard.vue
Displays a test case that references scripts and components with:
- Test case name and status badge (draft/active/deprecated/archived)
- Priority badge (low/medium/high/critical)
- Automation indicator
- Category display
- Script and component counts
- Test data preview
- Last execution status and timestamp
- Actions: Edit, Duplicate, Delete, Execute, View History
- Tags and version information

#### TestResultChart.vue
Visualizes test execution results with:
- Summary statistics (total, passed, failed, skipped)
- Multiple view modes:
  - Bar chart: Horizontal bars showing pass/fail/skip distribution
  - Pie chart: Radial progress showing pass rate
  - List view: Detailed list of individual results
- Interactive result selection
- Duration and timestamp display

## Usage Examples

### Using HeaderCard

```vue
<template>
  <HeaderCard
    :header="header"
    @edit="handleEdit"
    @duplicate="handleDuplicate"
    @delete="handleDelete"
    @use="handleUse"
  />
</template>

<script setup>
import { HeaderCard } from '@/components/business';

const header = {
  id: 1,
  name: 'Auth Header',
  scope: 'global',
  headers: {
    'Authorization': 'Bearer ${token}',
    'Content-Type': 'application/json'
  },
  // ... other properties
};
</script>
```

### Using ScriptDebugger

```vue
<template>
  <ScriptDebugger
    ref="debuggerRef"
    :script="currentScript"
    @close="closeDebugger"
    @debug="handleDebug"
  />
</template>

<script setup>
import { ref } from 'vue';
import { ScriptDebugger } from '@/components/business';

const debuggerRef = ref(null);

async function handleDebug(params, breakpoints) {
  const result = await executeScriptDebug(params, breakpoints);
  debuggerRef.value?.setDebugResult(result);
}
</script>
```

### Using ComponentTree

```vue
<template>
  <ComponentTree
    :root-component="rootComponent"
    :children="childComponents"
    :scripts="componentScripts"
    @select-component="handleSelectComponent"
    @select-script="handleSelectScript"
  />
</template>

<script setup>
import { ComponentTree } from '@/components/business';

// Component hierarchy data
const rootComponent = { /* ... */ };
const childComponents = [ /* ... */ ];
const componentScripts = [ /* ... */ ];
</script>
```

### Using TestResultChart

```vue
<template>
  <TestResultChart
    :results="testResults"
    title="Recent Test Executions"
    @select-result="handleSelectResult"
  />
</template>

<script setup>
import { TestResultChart } from '@/components/business';

const testResults = [
  {
    id: 1,
    name: 'User Login Test',
    status: 'passed',
    duration: 1250,
    executed_at: '2024-01-15T10:30:00Z',
    total: 10,
    passed: 10,
    failed: 0,
    skipped: 0
  },
  // ... more results
];
</script>
```

## Design Principles

1. **Consistency**: All cards follow a similar structure with header, content, and footer sections
2. **Interactivity**: Dropdown menus provide quick access to common actions
3. **Visual Hierarchy**: Badges and icons help users quickly identify component types and states
4. **Responsiveness**: Components adapt to different screen sizes using Tailwind's grid system
5. **Accessibility**: Proper ARIA labels and keyboard navigation support
6. **DaisyUI Integration**: Leverages DaisyUI components for consistent styling

## Styling

All components use:
- **Tailwind CSS 4** for utility classes
- **DaisyUI** for component styling
- **Headless UI** for accessible interactive elements
- Consistent color scheme based on DaisyUI themes
- Hover effects for better user feedback
- Shadow and transition effects for depth

## Events

All card components emit standard events:
- `edit`: User wants to edit the item
- `duplicate`: User wants to duplicate the item
- `delete`: User wants to delete the item
- `view`: User wants to view full details
- `execute`: User wants to execute the item (scripts, components, test cases)

Additional component-specific events are documented in each component's props/emits.
