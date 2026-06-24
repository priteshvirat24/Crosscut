/** API types matching backend Pydantic schemas for Crosscut */

export interface AnalysisResponse {
  id: string;
  project_name: string;
  mr_iid: number;
  mr_title: string;
  mr_url: string;
  status: "pending" | "running" | "completed" | "failed";
  total_tests_available: number;
  selected_tests_count: number;
  ci_minutes_saved: number | null;
  percentage_reduction: number | null;
  estimated_original_runtime: string | null;
  estimated_optimized_runtime: string | null;
  created_at: string;
  updated_at: string;
}

export interface ImpactedTestResponse {
  id: string;
  repository: string;
  file_path: string;
  test_name: string;
  dependency_depth: number;
  changed_symbol_name: string | null;
  reasoning: string | null;
}

export interface PipelineExecutionResponse {
  id: string;
  pipeline_id: string;
  status: string;
  tests_run: number;
  tests_passed: number;
  tests_failed: number;
  runtime_seconds: number;
  log_url: string | null;
}

export interface AnalysisDetail extends AnalysisResponse {
  source_branch: string;
  target_branch: string;
  change_report: Record<string, unknown> | null;
  dependency_graph: DependencyGraph | null;
  pipeline_report: Record<string, unknown> | null;
  executive_summary: string | null;
  execution_log: string[] | null;
  impacted_tests: ImpactedTestResponse[];
  pipeline_executions: PipelineExecutionResponse[];
}

export interface DependencyGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface GraphNode {
  id: string;
  type: string;
  name: string;
  repository?: string;
  file_path?: string;
  metadata?: Record<string, unknown>;
}

export interface GraphEdge {
  source: string;
  target: string;
  relationship: string;
  weight: number;
}

export interface OverviewStats {
  total_analyses: number;
  active_analyses: number;
  ci_minutes_saved: number;
  tests_skipped: number;
  avg_reduction_percentage: number;
  repositories_covered: number;
}

export interface SavingsDistribution {
  high_savings: number;
  medium_savings: number;
  low_savings: number;
  zero_savings: number;
}

export interface DashboardOverview {
  stats: OverviewStats;
  savings_distribution: SavingsDistribution;
  recent_analyses: AnalysisResponse[];
}
