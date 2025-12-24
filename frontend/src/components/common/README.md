# Common Components

This directory contains reusable UI components built with Tailwind CSS 4 and Headless UI.

## Components

### Button

A flexible button component with multiple variants and sizes.

**Props:**
- `variant`: 'primary' | 'secondary' | 'danger' | 'ghost' (default: 'primary')
- `size`: 'sm' | 'md' | 'lg' (default: 'md')
- `type`: 'button' | 'submit' | 'reset' (default: 'button')
- `disabled`: boolean (default: false)
- `loading`: boolean (default: false)
- `fullWidth`: boolean (default: false)

**Events:**
- `click`: Emitted when button is clicked

**Example:**
```vue
<Button variant="primary" size="md" @click="handleClick">
  Click Me
</Button>

<Button variant="danger" :loading="isLoading">
  Delete
</Button>
```

### Table

A data table component with sorting, striping, and custom cell rendering.

**Props:**
- `columns`: Array of column definitions
  - `key`: string - Column key
  - `label`: string - Column header label
  - `sortable`: boolean - Enable sorting
  - `align`: 'left' | 'center' | 'right' - Text alignment
  - `width`: string - Column width
- `data`: Array of row data objects
- `rowKey`: string - Unique key for rows (default: 'id')
- `striped`: boolean - Alternate row colors (default: false)
- `hoverable`: boolean - Highlight on hover (default: true)
- `emptyText`: string - Text when no data (default: '暂无数据')
- `headerClass`: string - Custom header class (default: 'bg-gray-50')

**Events:**
- `rowClick`: Emitted when a row is clicked
- `sort`: Emitted when a column is sorted

**Slots:**
- `cell-{key}`: Custom cell rendering for specific column
- `empty`: Custom empty state

**Example:**
```vue
<Table
  :columns="[
    { key: 'name', label: '名称', sortable: true },
    { key: 'status', label: '状态', align: 'center' },
    { key: 'actions', label: '操作', align: 'right' }
  ]"
  :data="tableData"
  striped
  @row-click="handleRowClick"
  @sort="handleSort"
>
  <template #cell-status="{ value }">
    <span :class="getStatusClass(value)">{{ value }}</span>
  </template>
  
  <template #cell-actions="{ row }">
    <Button size="sm" @click="editRow(row)">编辑</Button>
  </template>
</Table>
```

### Modal

A modal dialog component built with Headless UI.

**Props:**
- `modelValue`: boolean - Controls modal visibility
- `title`: string - Modal title
- `size`: 'sm' | 'md' | 'lg' | 'xl' | 'full' (default: 'md')
- `showHeader`: boolean - Show header section (default: true)
- `showFooter`: boolean - Show footer section (default: true)
- `showClose`: boolean - Show close button (default: true)
- `closeOnClickOutside`: boolean - Close on backdrop click (default: true)
- `confirmText`: string - Confirm button text (default: '确认')
- `cancelText`: string - Cancel button text (default: '取消')

**Events:**
- `update:modelValue`: Emitted to update visibility
- `confirm`: Emitted when confirm button is clicked
- `cancel`: Emitted when cancel button is clicked
- `close`: Emitted when modal is closed

**Slots:**
- `title`: Custom title content
- `default`: Modal body content
- `footer`: Custom footer content

**Example:**
```vue
<Modal
  v-model="showModal"
  title="确认删除"
  size="md"
  @confirm="handleConfirm"
  @cancel="handleCancel"
>
  <p>确定要删除这条记录吗？此操作不可撤销。</p>
</Modal>

<Modal
  v-model="showEditModal"
  title="编辑用户"
  size="lg"
  :show-footer="false"
>
  <template #default>
    <form @submit.prevent="handleSubmit">
      <!-- Form fields -->
    </form>
  </template>
  
  <template #footer>
    <Button variant="secondary" @click="showEditModal = false">取消</Button>
    <Button variant="primary" @click="handleSubmit">保存</Button>
  </template>
</Modal>
```

## Usage

Import components individually:
```typescript
import Button from '@/components/common/Button.vue'
import Table from '@/components/common/Table.vue'
import Modal from '@/components/common/Modal.vue'
import UserProfileCard from '@/components/common/UserProfileCard.vue'
```

Or import from the index:
```typescript
import { Button, Table, Modal, UserProfileCard } from '@/components/common'
```

## Dashboard Components

### UserProfileCard

A user profile card component that displays user information and testing metrics.

**Props:**
- `user`: Object containing user information
  - `id`: string - User ID
  - `username`: string - Username
  - `avatar`: string (optional) - Avatar URL
  - `registrationDate`: string - Registration date (ISO format)
- `metrics`: Object containing user metrics
  - `totalExecutions`: number - Total test executions
  - `passedTests`: number - Number of passed tests
  - `failedTests`: number - Number of failed tests

**Features:**
- Avatar display with fallback to user initial
- Formatted registration date
- Three metric badges with icons (executions, passed, failed)
- Number formatting with thousand separators
- Click to navigate to profile page
- Keyboard navigation support (Enter/Space)
- Hover effects for interactivity

**Example:**
```vue
<UserProfileCard
  :user="{
    id: '123',
    username: 'JohnDoe',
    avatar: 'https://example.com/avatar.jpg',
    registrationDate: '2024-01-15T10:30:00Z'
  }"
  :metrics="{
    totalExecutions: 1234,
    passedTests: 890,
    failedTests: 344
  }"
/>
```

### DonutChart

A reusable donut chart component for displaying statistics.

**Props:**
- `datasets`: Array of chart datasets
  - `label`: string - Dataset label
  - `value`: number - Dataset value
  - `color`: string - Color hex code
- `centerText`: string (optional) - Text to display in center
- `showLegend`: boolean (default: true) - Show/hide legend
- `size`: 'sm' | 'md' | 'lg' (default: 'md') - Chart size

**Example:**
```vue
<DonutChart
  :datasets="[
    { label: 'Completed', value: 50, color: '#3B82F6' },
    { label: 'Failed', value: 30, color: '#F59E0B' },
    { label: 'Pending', value: 20, color: '#8B5CF6' }
  ]"
  centerText="Total: 100"
  size="lg"
/>
```

### AreaChart

A reusable area chart component for displaying trends over time.

**Props:**
- `series`: Array of chart series
  - `name`: string - Series name
  - `data`: number[] - Series data points
  - `color`: string - Color hex code
- `labels`: string[] - X-axis labels
- `yAxisLabel`: string (optional) - Y-axis label
- `xAxisLabel`: string (optional) - X-axis label
- `showGrid`: boolean (default: true) - Show/hide grid

**Example:**
```vue
<AreaChart
  :series="[
    { name: 'Series 1', data: [10, 20, 30], color: '#3B82F6' },
    { name: 'Series 2', data: [15, 25, 35], color: '#10B981' }
  ]"
  :labels="['Jan', 'Feb', 'Mar']"
  yAxisLabel="Count"
  xAxisLabel="Month"
/>
```
