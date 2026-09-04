import {
  DashboardMetrics,
  Transaction,
  TransactionListResponse,
  RecoveryCase,
  RecoveryCaseDetail,
  RecoveryCaseListResponse,
  AuditLogResponse,
  SimulationResult,
  EvaluationReport,
  ApprovalListResponse,
  AssistantChatRequest,
  AssistantChatResponse,
} from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    cache: "no-store",
  });

  let data: any = null;

  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    const message =
      data?.detail ||
      data?.message ||
      data?.error?.message ||
      `API request failed with status ${response.status}`;

    throw new Error(message);
  }

  if (data?.error) {
    throw new Error(
      data.error.message || "API returned an error."
    );
  }

  return data as T;
}

export const api = {
  // Dashboard
  async getDashboardMetrics(): Promise<DashboardMetrics> {
    return request<DashboardMetrics>("/dashboard/metrics");
  },

  // Transactions
  async getTransactions(
    query = ""
  ): Promise<TransactionListResponse> {
    return request<TransactionListResponse>(
      `/transactions${query ? `?${query}` : ""}`
    );
  },

  async getTransactionById(
    transactionId: string
  ): Promise<Transaction> {
    return request<Transaction>(
      `/transactions/${encodeURIComponent(transactionId)}`
    );
  },

  async createTransaction(data: Record<string, any>) {
    return request<{ status: string; id: string }>(
      "/transactions",
      {
        method: "POST",
        body: JSON.stringify(data),
      }
    );
  },

  // Recovery Cases
  async getRecoveryCases(
    query = ""
  ): Promise<RecoveryCaseListResponse> {
    return request<RecoveryCaseListResponse>(
      `/recovery-cases${query ? `?${query}` : ""}`
    );
  },

  async getRecoveryCaseById(
    caseId: string
  ): Promise<RecoveryCaseDetail> {
    return request<RecoveryCaseDetail>(
      `/recovery-cases/${encodeURIComponent(caseId)}`
    );
  },

  async analyzeCase(caseId: string) {
    return request<{
      status: string;
      case_id: string;
      case_status: string;
      recommended_action?: string;
      confidence: number;
      recovery_score: number;
      requires_human_approval: boolean;
    }>(
      `/recovery-cases/${encodeURIComponent(caseId)}/analyze`,
      {
        method: "POST",
      }
    );
  },

  async executeCaseAction(caseId: string) {
    return request<{
      status: string;
      action_id: string;
      action_type: string;
      execution_status: string;
      result?: Record<string, any>;
    }>(
      `/recovery-cases/${encodeURIComponent(caseId)}/execute`,
      {
        method: "POST",
      }
    );
  },

  // Audit Logs
  async getAuditLogs(
    query = ""
  ): Promise<AuditLogResponse> {
    return request<AuditLogResponse>(
      `/audit-logs${query ? `?${query}` : ""}`
    );
  },

  // Approvals
  async getPendingApprovals(): Promise<ApprovalListResponse> {
    return request<ApprovalListResponse>("/approvals/pending");
  },

  async approveRecoveryCase(caseId: string) {
    return request<{
      status: string;
      case_id: string;
      action_id: string;
      action_type: string;
      execution_status: string;
    }>(
      `/recovery-cases/${encodeURIComponent(caseId)}/approve`,
      {
        method: "POST",
      }
    );
  },

  async rejectRecoveryCase(
    caseId: string,
    reason = "Rejected by merchant operator"
  ) {
    return request<{
      status: string;
      case_id: string;
      case_status: string;
    }>(
      `/recovery-cases/${encodeURIComponent(caseId)}/reject`,
      {
        method: "POST",
        body: JSON.stringify({ reason }),
      }
    );
  },
 // Approvals
  async approveCase(caseId: string) {
    return this.approveRecoveryCase(caseId);
  },

  async rejectCase(
    caseId: string,
    reason = "Rejected by merchant operator"
  ) {
    return this.rejectRecoveryCase(caseId, reason);
  },

  // Simulation
  async runSimulation(data: {
    scenario_name?: string;
    batch_size?: number;
    source?: string;
    custom_transactions?: any[];
    start_date?: string;
    end_date?: string;
    enable_ai_agent?: boolean;
    enable_policy_engine?: boolean;
  }): Promise<SimulationResult> {
    return request<SimulationResult>("/simulation/run", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async resetSimulation() {
    return request<{
      status: string;
      message: string;
      purged_simulation_transactions: number;
      purged_simulation_cases: number;
      live_data_protected: boolean;
    }>("/simulation/reset", {
      method: "POST",
    });
  },

  // Health
  async getSystemHealth() {
    const response = await fetch(`${API_BASE_URL.replace("/api/v1", "")}/health`, {
      cache: "no-store",
    });
    return response.json();
  },

  // Evaluation
  async getEvaluationResults(): Promise<EvaluationReport> {
    return request<EvaluationReport>("/evaluation/results");
  },

  // Intelligence Assistant
  async sendAssistantMessage(
    payload: AssistantChatRequest
  ): Promise<AssistantChatResponse> {
    return request<AssistantChatResponse>("/assistant/chat", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
};