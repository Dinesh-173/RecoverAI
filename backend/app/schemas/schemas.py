from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class MerchantBase(BaseModel):
    name: str
    business_category: str = "ECOMMERCE"
    currency: str = "INR"
    high_value_threshold: float = 10000.0
    max_retries: int = 2
    min_ai_confidence: float = 0.70
    min_recovery_score: float = 15.0
    cooldown_minutes: int = 60


class MerchantCreate(MerchantBase):
    id: Optional[str] = None


class MerchantResponse(MerchantBase):
    id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CustomerBase(BaseModel):
    name: str
    email_hash: str
    customer_segment: str = "STANDARD"
    successful_payment_count: int = 0
    failed_payment_count: int = 0
    total_lifetime_value: float = 0.0
    communication_opt_out: bool = False


class CustomerCreate(CustomerBase):
    merchant_id: str
    id: Optional[str] = None


class CustomerResponse(CustomerBase):
    id: str
    merchant_id: str
    last_payment_at: Optional[datetime] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TransactionBase(BaseModel):
    amount: float
    currency: str = "INR"
    payment_method: str = "UPI"
    status: str
    failure_reason: Optional[str] = None
    failure_code: Optional[str] = None
    attempt_number: int = 1
    order_id: Optional[str] = None
    subscription_id: Optional[str] = None
    metadata_json: Dict[str, Any] = {}


class TransactionCreate(TransactionBase):
    external_transaction_id: Optional[str] = None
    merchant_id: str
    customer_id: str
    id: Optional[str] = None


class TransactionResponse(TransactionBase):
    id: str
    external_transaction_id: Optional[str] = None
    merchant_id: str
    customer_id: str
    customer_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class RiskAssessmentResponse(BaseModel):
    id: str
    transaction_id: str
    risk_score: float
    expected_recoverable_amount: float
    confidence: float
    model_version: str
    features_version: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class RecoveryActionCreate(BaseModel):
    action_type: str
    amount: float
    reason: Optional[str] = None
    policy_decision: str = "APPROVED"
    policy_version: str = "v1.0.0"


class RecoveryActionResponse(BaseModel):
    id: str
    recovery_case_id: str
    action_type: str
    status: str
    amount: float
    reason: Optional[str] = None
    policy_decision: str
    policy_version: str
    executed_at: Optional[datetime] = None
    result_json: Dict[str, Any] = {}
    error_code: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class RecoveryCaseResponse(BaseModel):
    id: str
    transaction_id: str
    status: str
    risk_level: str
    diagnosis: Optional[str] = None
    recommended_action: Optional[str] = None
    recommended_delay_minutes: int = 0
    confidence: float = 0.0
    recovery_score: float = 0.0
    requires_human_approval: bool = False
    approval_reason: Optional[str] = None
    assigned_to: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    transaction: Optional[TransactionResponse] = None
    actions: List[RecoveryActionResponse] = []
    model_config = ConfigDict(from_attributes=True)


class AuditLogResponse(BaseModel):
    id: str
    entity_type: str
    entity_id: str
    actor_type: str
    actor_id: str
    action: str
    reason: Optional[str] = None
    input_summary: Dict[str, Any] = {}
    output_summary: Dict[str, Any] = {}
    policy_result: Optional[str] = None
    timestamp: datetime
    correlation_id: str
    model_config = ConfigDict(from_attributes=True)


class DashboardMetrics(BaseModel):
    revenue_at_risk: float
    recovered_revenue: float
    expected_recoverable_revenue: float
    recovery_rate: float
    open_cases: int
    pending_approvals: int
    stopped_cases: int
    successful_recoveries: int
    total_evaluated_transactions: int
    average_recovery_amount: float
    baseline_recovered_revenue: float
    baseline_recovery_rate: float
    delta_revenue_gain: float
    chart_revenue_timeline: List[Dict[str, Any]] = []
    chart_recovery_by_method: List[Dict[str, Any]] = []
    chart_recovery_by_reason: List[Dict[str, Any]] = []
    chart_strategy_success: List[Dict[str, Any]] = []


class SimulationRunRequest(BaseModel):
    scenario_name: Optional[str] = "default_batch"
    batch_size: int = 10
    enable_ai_agent: bool = True
    enable_policy_engine: bool = True


class SimulationRunResponse(BaseModel):
    batch_id: str
    evaluated_count: int
    recovered_count: int
    escalated_count: int
    stopped_count: int
    revenue_at_risk: float
    revenue_recovered: float
    recovery_rate: float
    baseline_recovered_revenue: float
    value_add_percentage: float
    execution_duration_ms: float
    cases: List[Dict[str, Any]] = []
