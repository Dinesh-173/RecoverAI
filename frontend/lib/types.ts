export interface Customer {
  id: string;
  name: string;
  customer_segment: string;
  total_lifetime_value: number;
  successful_payment_count: number;
  failed_payment_count: number;
  communication_opt_out: boolean;
}

export interface Transaction {
  id: string;
  external_transaction_id?: string | null;
  merchant_id?: string;
  customer_id?: string;
  customer_name?: string | null;
  customer_segment?: string | null;
  amount: number;
  currency: string;
  payment_method: string;
  status: string;
  failure_code?: string | null;
  failure_reason?: string | null;
  attempt_number: number;
  order_id?: string | null;
  subscription_id?: string | null;
  metadata_json?: Record<string, any>;
  customer?: Customer | null;
  risk_score?: number | null;
  case_status?: string | null;
  created_at?: string;
  updated_at?: string;
}

export type TransactionItem = Transaction;

export interface RecoveryAction {
  id: string;
  recovery_case_id?: string;
  action_type: string;
  status: string;
  amount: number;
  reason?: string | null;
  policy_decision?: string;
  policy_version?: string;
  executed_at?: string | null;
  result?: Record<string, any>;
  result_json?: Record<string, any>;
  error_code?: string | null;
  created_at?: string;
}

export interface RecoveryCase {
  id: string;
  transaction_id: string;
  transaction_amount?: number;
  payment_method?: string;
  customer_name?: string;
  status: string;
  risk_level: string;
  diagnosis?: string | null;
  recommended_action?: string | null;
  recommended_delay_minutes: number;
  confidence: number;
  recovery_score: number;
  requires_human_approval: boolean;
  approval_reason?: string | null;
  actions_count?: number;
  created_at: string;
  updated_at?: string;
}

export interface RecoveryCaseDetail {
  id: string;
  status: string;
  risk_level: string;
  diagnosis?: string | null;
  recommended_action?: string | null;
  recommended_delay_minutes: number;
  confidence: number;
  recovery_score: number;
  requires_human_approval: boolean;
  approval_reason?: string | null;
  assigned_to?: string | null;
  created_at: string;
  updated_at: string;
  transaction: Transaction | null;
  actions: RecoveryAction[];
}

export interface AuditLogItem {
  id: string;
  entity_type: string;
  entity_id: string;
  actor_type: string;
  actor_id: string;
  action: string;
  reason?: string | null;
  input_summary: Record<string, any>;
  output_summary: Record<string, any>;
  policy_result?: string | null;
  timestamp: string;
  correlation_id: string;
}

export interface DashboardMetrics {
  revenue_at_risk: number;
  recovered_revenue: number;
  expected_recoverable_revenue: number;
  recovery_rate: number;
  open_cases: number;
  pending_approvals: number;
  stopped_cases: number;
  successful_recoveries: number;
  total_evaluated_transactions: number;
  average_recovery_amount: number;
  baseline_recovered_revenue: number;
  baseline_recovery_rate: number;
  delta_revenue_gain: number;

  chart_revenue_timeline: Array<Record<string, any>>;
  chart_recovery_by_method: Array<Record<string, any>>;
  chart_recovery_by_reason: Array<Record<string, any>>;
  chart_strategy_success: Array<Record<string, any>>;
}

export interface CustomTransactionInput {
  transaction_id: string;
  transaction_date?: string;
  amount: number;
  currency?: string;
  payment_method?: string;
  failure_code?: string;
  failure_reason?: string;
  retry_attempt?: number;
  customer_opt_out?: boolean;
  risk_flag?: boolean;
  customer_name?: string;
  customer_email?: string;
  customer_segment?: string;
}

export interface SimulationCase {
  case_id: string;
  transaction_id: string;
  internal_transaction_id?: string;
  transaction_date?: string | null;
  created_at?: string | null;
  amount: number;
  currency?: string;
  payment_method?: string;
  failure_code?: string | null;
  retry_attempt?: number;
  customer_opt_out?: boolean;
  diagnosis?: string | null;
  recommended_action?: string | null;
  confidence: number;
  recovery_score: number;
  case_status: string;
  action_status: string;
}

export interface SimulationResult {
  batch_id: string;
  evaluated_count: number;
  recovered_count: number;
  escalated_count: number;
  stopped_count: number;
  revenue_at_risk: number;
  revenue_recovered: number;
  recovery_rate: number;
  baseline_recovered_revenue: number;
  value_add_percentage: number;
  execution_duration_ms: number;
  cases: SimulationCase[];
}

export interface EvaluationModel {
  model_version: string;
  roc_auc: number;
  precision: number;
  recall: number;
  f1_score: number;
  false_positive_rate: number;

  confusion_matrix: {
    true_negatives: number;
    false_positives: number;
    false_negatives: number;
    true_positives: number;
  };

  domain_analysis: {
    why_false_positives_matter: string;
    why_false_negatives_matter: string;
  };
}

export interface RecoveryPerformance {
  recovered_revenue: number;
  recovery_rate_pct: number;
  wasted_retries: number;
  avoided_wasteful_retries: number;
}

export interface EvaluationReport {
  status?: string;

  model_evaluation: EvaluationModel;

  recovery_evaluation: {
    total_evaluated_transactions: number;

    baseline_performance: RecoveryPerformance;

    recoverai_performance: RecoveryPerformance;

    impact_delta: {
      additional_revenue_recovered: number;
      relative_improvement_percentage: number;
      human_escalation_rate_pct: number;
      stopped_case_rate_pct: number;
    };
  };
}

export interface PendingApprovalItem {
  id: string;
  transaction_id: string;
  amount: number;
  currency: string;
  payment_method: string;
  customer_name: string;
  customer_segment: string;
  failure_code: string;
  failure_reason: string;
  diagnosis?: string | null;
  recommended_action?: string | null;
  confidence: number;
  recovery_score: number;
  approval_reason: string;
  created_at: string;
}

export interface TransactionListResponse {
  items: Transaction[];
  total: number;
  skip: number;
  limit: number;
}

export interface RecoveryCaseListResponse {
  items: RecoveryCase[];
  count: number;
}

export interface AuditLogResponse {
  items: AuditLogItem[];
  count: number;
}

export interface ApprovalListResponse {
  items: PendingApprovalItem[];
  count: number;
}

export interface SuggestedAction {
  label: string;
  action_type: string;
  payload: Record<string, any>;
}

export interface ToolExecutionLog {
  tool_name: string;
  status: string;
  summary: string;
}

export interface AssistantCitation {
  source_type: string;
  title: string;
  reference_id?: string;
}

export interface AssistantChatRequest {
  message: string;
  conversation_id?: string;
  page_context?: string;
  entity_id?: string;
  presentation_mode?: boolean;
}

export interface AssistantChatResponse {
  message: string;
  conversation_id: string;
  tools_used: ToolExecutionLog[];
  citations: AssistantCitation[];
  suggested_actions: SuggestedAction[];
}

