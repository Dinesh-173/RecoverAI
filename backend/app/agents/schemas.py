from pydantic import BaseModel, Field
from typing import List, Optional


class ProposedActionSpec(BaseModel):
    type: str = Field(..., description="Action type: RETRY_PAYMENT, CUSTOMER_NOTIFICATION, PAYMENT_LINK, HUMAN_REVIEW, STOP_RECOVERY")
    delay_minutes: int = Field(0, description="Recommended delay before action execution in minutes")
    channel: str = Field("DIRECT_RETRY", description="Execution channel, e.g. DIRECT_RETRY, SMS, WHATSAPP, EMAIL, OPS_QUEUE")


class AgentDiagnosticOutput(BaseModel):
    diagnosis: str = Field(..., description="Concise, factual explanation of why the revenue was lost")
    recovery_strategy: str = Field(..., description="Target strategy: RETRY_PAYMENT, DELAYED_RETRY, CUSTOMER_NOTIFICATION, HUMAN_REVIEW, STOP_RECOVERY")
    confidence: float = Field(..., ge=0.0, le=1.0, description="AI confidence score between 0.0 and 1.0")
    reason_codes: List[str] = Field(default_factory=list, description="Machine-readable evidence codes justifying the decision")
    requires_human_approval: bool = Field(False, description="Flag if action needs merchant signoff")
    proposed_action: ProposedActionSpec = Field(..., description="Structured execution payload")
    is_fallback: bool = Field(False, description="Flag indicating if deterministic fallback was used instead of LLM")
