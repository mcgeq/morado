<template>
  <div class="p-8 bg-gray-100 min-h-screen">
    <h1 class="text-3xl font-bold mb-8">UserProfileCard Examples</h1>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Example 1: User with avatar -->
      <div>
        <h2 class="text-xl font-semibold mb-4">With Avatar</h2>
        <UserProfileCard :user="userWithAvatar" :metrics="metrics1" />
      </div>

      <!-- Example 2: User without avatar -->
      <div>
        <h2 class="text-xl font-semibold mb-4">Without Avatar (Fallback)</h2>
        <UserProfileCard :user="userWithoutAvatar" :metrics="metrics2" />
      </div>

      <!-- Example 3: High numbers -->
      <div>
        <h2 class="text-xl font-semibold mb-4">High Numbers</h2>
        <UserProfileCard :user="userWithAvatar" :metrics="highMetrics" />
      </div>

      <!-- Example 4: Zero metrics -->
      <div>
        <h2 class="text-xl font-semibold mb-4">Zero Metrics</h2>
        <UserProfileCard :user="userWithoutAvatar" :metrics="zeroMetrics" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import type { UserProfileCardProps } from '@/types/dashboard';
  import UserProfileCard from './UserProfileCard.vue';

  const userWithAvatar: UserProfileCardProps['user'] = {
    id: '1',
    username: 'JohnDoe',
    avatar: 'https://i.pravatar.cc/150?img=1',
    registrationDate: '2024-01-15T10:30:00Z',
  };

  const userWithoutAvatar: UserProfileCardProps['user'] = {
    id: '2',
    username: 'JaneSmith',
    registrationDate: '2023-12-01T08:15:00Z',
  };

  const metrics1: UserProfileCardProps['metrics'] = {
    totalExecutions: 1234,
    passedTests: 890,
    failedTests: 344,
  };

  const metrics2: UserProfileCardProps['metrics'] = {
    totalExecutions: 567,
    passedTests: 450,
    failedTests: 117,
  };

  const highMetrics: UserProfileCardProps['metrics'] = {
    totalExecutions: 123456,
    passedTests: 98765,
    failedTests: 24691,
  };

  const zeroMetrics: UserProfileCardProps['metrics'] = {
    totalExecutions: 0,
    passedTests: 0,
    failedTests: 0,
  };
</script>
