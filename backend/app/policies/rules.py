from enum import Enum
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class PolicyDecision(str, Enum):
    APPROVED = "APPROVED"
    BLOCKED = "BLOCKED"
    ESCALATED_HUMAN_APPROVAL = "ESCALATED_HUMAN_APPROVAL"
    STOPPED = "STOPPED"


class PolicyEvaluationResult(BaseModel):
    decision: PolicyDecision
    rule_name: str
    reason: str
    policy_version: str = "v1.0.0"
    requires_human_approval: bool = False
    allowed_action_type: Optional[str] = None
    applied_checks: List[Dict[str, Any]] = []
