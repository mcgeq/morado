<template>
  <div class="overflow-x-auto">
    <table class="min-w-full divide-y divide-gray-200">
      <thead :class="headerClass">
        <tr>
          <th
            v-for="column in columns"
            :key="column.key"
            scope="col"
            :class="getHeaderCellClass(column)"
            @click="handleSort(column)"
          >
            <div class="flex items-center gap-2">
              <span>{{ column.label }}</span>
              <span v-if="column.sortable && sortBy === column.key" class="text-xs">
                {{ sortOrder === 'asc' ? '↑' : '↓' }}
              </span>
            </div>
          </th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-gray-200">
        <tr
          v-for="(row, rowIndex) in sortedData"
          :key="getRowKey(row, rowIndex)"
          :class="getRowClass(rowIndex)"
          @click="handleRowClick(row)"
        >
          <td v-for="column in columns" :key="column.key" :class="getCellClass(column)">
            <slot :name="`cell-${column.key}`" :row="row" :value="getCellValue(row, column.key)">
              {{ getCellValue(row, column.key) }}
            </slot>
          </td>
        </tr>
        <tr v-if="!data || data.length === 0">
          <td :colspan="columns.length" class="px-6 py-4 text-center text-gray-500">
            <slot name="empty">{{ emptyText }}</slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
  import { computed, ref } from 'vue';

  interface Column {
    key: string;
    label: string;
    sortable?: boolean;
    align?: 'left' | 'center' | 'right';
    width?: string;
  }

  type TableRow = Record<string, unknown>;

  interface Props {
    columns: Column[];
    data: TableRow[];
    rowKey?: string;
    striped?: boolean;
    hoverable?: boolean;
    emptyText?: string;
    headerClass?: string;
  }

  const props = withDefaults(defineProps<Props>(), {
    rowKey: 'id',
    striped: false,
    hoverable: true,
    emptyText: '暂无数据',
    headerClass: 'bg-gray-50',
  });

  const emit = defineEmits<{
    rowClick: [row: TableRow];
    sort: [column: string, order: 'asc' | 'desc'];
  }>();

  const sortBy = ref<string | null>(null);
  const sortOrder = ref<'asc' | 'desc'>('asc');

  const getRowKey = (row: TableRow, index: number): string | number => {
    return (row[props.rowKey] as string | number) ?? index;
  };

  const getCellValue = (row: TableRow, key: string): unknown => {
    return row[key];
  };

  const getHeaderCellClass = (column: Column): string => {
    const baseClasses = [
      'px-6',
      'py-3',
      'text-xs',
      'font-medium',
      'text-gray-500',
      'uppercase',
      'tracking-wider',
    ];

    const alignClasses = {
      left: 'text-left',
      center: 'text-center',
      right: 'text-right',
    };

    const align = column.align || 'left';
    const cursorClass = column.sortable ? 'cursor-pointer hover:text-gray-700' : '';

    return [...baseClasses, alignClasses[align], cursorClass].filter(Boolean).join(' ');
  };

  const getCellClass = (column: Column): string => {
    const baseClasses = ['px-6', 'py-4', 'whitespace-nowrap', 'text-sm', 'text-gray-900'];

    const alignClasses = {
      left: 'text-left',
      center: 'text-center',
      right: 'text-right',
    };

    const align = column.align || 'left';

    return [...baseClasses, alignClasses[align]].join(' ');
  };

  const getRowClass = (index: number): string => {
    const classes: string[] = [];

    if (props.striped && index % 2 === 1) {
      classes.push('bg-gray-50');
    }

    if (props.hoverable) {
      classes.push('hover:bg-gray-100', 'cursor-pointer');
    }

    return classes.join(' ');
  };

  const handleRowClick = (row: TableRow) => {
    emit('rowClick', row);
  };

  const handleSort = (column: Column) => {
    if (!column.sortable) return;

    if (sortBy.value === column.key) {
      sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
    } else {
      sortBy.value = column.key;
      sortOrder.value = 'asc';
    }

    emit('sort', column.key, sortOrder.value);
  };

  const sortedData = computed(() => {
    if (!(sortBy.value && props.data)) return props.data;

    const sortKey = sortBy.value;
    const sorted = [...props.data].sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];

      if (aVal === bVal) return 0;

      // Handle null/undefined values
      if (aVal == null) return 1;
      if (bVal == null) return -1;

      // Type-safe comparison
      const comparison = String(aVal) > String(bVal) ? 1 : -1;
      return sortOrder.value === 'asc' ? comparison : -comparison;
    });

    return sorted;
  });
</script>
