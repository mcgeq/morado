/**
 * Dashboard Component Type Definitions
 *
 * TypeScript interfaces for dashboard component props and data structures.
 */

// ============================================================================
// User Profile Card Types
// ============================================================================

export interface UserProfileCardProps {
  user: {
    id: string;
    username: string;
    avatar?: string;
    registrationDate: string;
  };
  metrics: {
    totalExecutions: number;
    passedTests: number;
    failedTests: number;
  };
}

// ============================================================================
// Quick Actions Types
// ============================================================================

export interface QuickAction {
  id: string;
  title: string;
  icon: string;
  route: string;
  description?: string;
}

export interface QuickActionsPanelProps {
  actions: QuickAction[];
  title?: string;
}

// ============================================================================
// Statistics Widget Types
// ============================================================================

export interface StepStatistics {
  completed: number;
  sqlFailed: number;
  apiRequest: number;
}

export interface StepsStatisticsWidgetProps {
  statistics: StepStatistics;
  title?: string;
}

// ============================================================================
// API Usage Widget Types
// ============================================================================

export interface ApiUsageData {
  apiCompletion: {
    percentage: number;
    totalApis: number;
    completedApis: number;
    taggedApis: number;
  };
  testCaseCompletion: {
    percentage: number;
    totalTestCases: number;
    passedTestCases: number;
    taggedTestCases: number;
  };
}

export interface ApiUsageWidgetProps {
  data: ApiUsageData;
  title?: string;
}

// ============================================================================
// Trend Analysis Widget Types
// ============================================================================

export interface TrendDataPoint {
  date: string; // YYYY-MM-DD format
  scheduledComponents: number;
  testCaseComponents: number;
  actualComponents: number;
  detectionComponents: number;
}

export interface TrendAnalysisWidgetProps {
  data: TrendDataPoint[];
  title?: string;
  dateRange?: { start: string; end: string };
}

// ============================================================================
// Chart Component Types
// ============================================================================

export interface ChartDataset {
  label: string;
  value: number;
  color: string;
}

export interface DonutChartProps {
  datasets: ChartDataset[];
  centerText?: string;
  showLegend?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export interface AreaChartSeries {
  name: string;
  data: number[];
  color: string;
}

export interface AreaChartProps {
  series: AreaChartSeries[];
  labels: string[];
  yAxisLabel?: string;
  xAxisLabel?: string;
  showGrid?: boolean;
}

// ============================================================================
// Dashboard State Types
// ============================================================================

export interface DashboardState {
  loading: boolean;
  error: string | null;
  lastUpdated: Date | null;
  userData: UserData;
  statistics: DashboardStatistics;
}

export interface UserData {
  id: string;
  username: string;
  avatar: string | null;
  registrationDate: string;
  metrics: UserMetrics;
}

export interface UserMetrics {
  totalExecutions: number;
  passedTests: number;
  failedTests: number;
}

export interface DashboardStatistics {
  steps: StepStatistics;
  apiUsage: ApiUsageData;
  trends: TrendDataPoint[];
}
