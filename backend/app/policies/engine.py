from typing import Dict, Any, List
from backend.app.policies.rules import PolicyDecision, PolicyEvaluationResult
from backend.app.agents.schemas import AgentDiagnosticOutput
from backend.app.core.logging import logger


class DeterministicPolicyEngine:
    """
    Deterministic Fintech Policy Engine.
    Enforces immutable business safety rules and guardrails before any financial recovery action.
    The AI Agent CANNOT bypass these rules.
    """
    POLICY_VERSION = "v1.2.0"
    ALLOWED_ACTIONS = {"RETRY_PAYMENT", "CUSTOMER_NOTIFICATION", "HUMAN_REVIEW", "STOP_RECOVERY"}

    @classmethod
    def evaluate(
        cls,
        agent_proposal: AgentDiagnosticOutput,
        transaction_data: Dict[str, Any],
        customer_data: Dict[str, Any],
        merchant_policy: Dict[str, Any],
        recovery_score: float,
    ) -> PolicyEvaluationResult:
        checks_log: List[Dict[str, Any]] = []

        proposed_action_type = agent_proposal.proposed_action.type
        amount = transaction_data.get("amount", 0.0)
        attempt_number = transaction_data.get("attempt_number", 1)
        tx_status = transaction_data.get("status", "FAILED")
        opt_out = customer_data.get("communication_opt_out", False)

        # Merchant policy configurations
        high_value_thresh = merchant_policy.get("high_value_threshold", 10000.0)
        max_retries = merchant_policy.get("max_retries", 2)
        min_confidence = merchant_policy.get("min_ai_confidence", 0.70)
        min_score = merchant_policy.get("min_recovery_score", 15.0)

        # 1. Action Whitelist Check
        if proposed_action_type not in cls.ALLOWED_ACTIONS:
            checks_log.append({"check": "ACTION_WHITELIST", "status": "FAIL", "reason": f"Unknown action {proposed_action_type}"})
            return PolicyEvaluationResult(
                decision=PolicyDecision.BLOCKED,
                rule_name="ACTION_WHITELIST_CHECK",
                reason=f"Action '{proposed_action_type}' is not an authorized recovery action.",
                policy_version=cls.POLICY_VERSION,
                requires_human_approval=False,
                applied_checks=checks_log
            )
        checks_log.append({"check": "ACTION_WHITELIST", "status": "PASS"})

        # 2. Transaction Status Check
        if tx_status != "FAILED":
            checks_log.append({"check": "TX_STATUS_ELIGIBILITY", "status": "FAIL", "reason": f"Transaction is in status {tx_status}"})
            return PolicyEvaluationResult(
                decision=PolicyDecision.BLOCKED,
                rule_name="STATUS_ELIGIBILITY_RULE",
                reason=f"Transaction with status '{tx_status}' is not eligible for recovery.",
                policy_version=cls.POLICY_VERSION,
                requires_human_approval=False,
                applied_checks=checks_log
            )
        checks_log.append({"check": "TX_STATUS_ELIGIBILITY", "status": "PASS"})

        # 3. Customer Communication Opt-Out Check
        if opt_out and proposed_action_type == "CUSTOMER_NOTIFICATION":
            checks_log.append({"check": "CUSTOMER_OPT_OUT", "status": "FAIL", "reason": "Customer opted out of contact"})
            return PolicyEvaluationResult(
                decision=PolicyDecision.BLOCKED,
                rule_name="CUSTOMER_OPT_OUT_RULE",
                reason="Customer has actively opted out of payment notifications. Notification blocked by policy.",
                policy_version=cls.POLICY_VERSION,
                requires_human_approval=False,
                applied_checks=checks_log
            )
        checks_log.append({"check": "CUSTOMER_OPT_OUT", "status": "PASS"})

        # 4. Max Retry Limit Check
        if proposed_action_type == "RETRY_PAYMENT" and attempt_number >= max_retries:
            checks_log.append({"check": "MAX_RETRY_LIMIT", "status": "FAIL", "reason": f"Attempt {attempt_number} >= {max_retries}"})
            return PolicyEvaluationResult(
                decision=PolicyDecision.STOPPED,
                rule_name="MAX_RETRY_LIMIT_RULE",
                reason=f"Transaction attempt {attempt_number} has met or exceeded merchant max retry limit ({max_retries}).",
                policy_version=cls.POLICY_VERSION,
                requires_human_approval=False,
                allowed_action_type="STOP_RECOVERY",
                applied_checks=checks_log
            )
        checks_log.append({"check": "MAX_RETRY_LIMIT", "status": "PASS"})

        # 5. Stop Recovery explicit recommendation
        if proposed_action_type == "STOP_RECOVERY":
            checks_log.append({"check": "STOP_ACTION", "status": "PASS"})
            return PolicyEvaluationResult(
                decision=PolicyDecision.STOPPED,
                rule_name="RECOVERY_STOP_CONFIRMED",
                reason=agent_proposal.diagnosis,
                policy_version=cls.POLICY_VERSION,
                requires_human_approval=False,
                allowed_action_type="STOP_RECOVERY",
                applied_checks=checks_log
            )

        # 6. High-Value Escalation Guardrail
        if amount >= high_value_thresh:
            checks_log.append({"check": "HIGH_VALUE_THRESHOLD", "status": "ESCALATE", "amount": amount, "threshold": high_value_thresh})
            return PolicyEvaluationResult(
                decision=PolicyDecision.ESCALATED_HUMAN_APPROVAL,
                rule_name="HIGH_VALUE_THRESHOLD_RULE",
                reason=f"Transaction amount (₹{amount:,.2f}) exceeds high-value threshold (₹{high_value_thresh:,.2f}). Requires merchant approval.",
                policy_version=cls.POLICY_VERSION,
                requires_human_approval=True,
                allowed_action_type=proposed_action_type,
                applied_checks=checks_log
            )
        checks_log.append({"check": "HIGH_VALUE_THRESHOLD", "status": "PASS"})

        # 7. Minimum Confidence Guardrail
        if agent_proposal.confidence < min_confidence or agent_proposal.requires_human_approval:
            checks_log.append({"check": "MIN_CONFIDENCE_THRESHOLD", "status": "ESCALATE", "confidence": agent_proposal.confidence})
            return PolicyEvaluationResult(
                decision=PolicyDecision.ESCALATED_HUMAN_APPROVAL,
                rule_name="MIN_CONFIDENCE_RULE",
                reason=f"AI diagnostic confidence ({agent_proposal.confidence:.2f}) is below minimum threshold ({min_confidence:.2f}). Requires merchant review.",
                policy_version=cls.POLICY_VERSION,
                requires_human_approval=True,
                allowed_action_type=proposed_action_type,
                applied_checks=checks_log
            )
        checks_log.append({"check": "MIN_CONFIDENCE_THRESHOLD", "status": "PASS"})

        # 8. Minimum Recovery Score Guardrail
        if recovery_score < min_score:
            checks_log.append({"check": "MIN_RECOVERY_SCORE", "status": "FAIL", "score": recovery_score, "min_score": min_score})
            return PolicyEvaluationResult(
                decision=PolicyDecision.STOPPED,
                rule_name="MIN_RECOVERY_SCORE_RULE",
                reason=f"Calculated recovery score ({recovery_score:.1f}) is below economic feasibility threshold ({min_score:.1f}).",
                policy_version=cls.POLICY_VERSION,
                requires_human_approval=False,
                allowed_action_type="STOP_RECOVERY",
                applied_checks=checks_log
            )
        checks_log.append({"check": "MIN_RECOVERY_SCORE", "status": "PASS"})

        # All checks passed: Action Approved
        return PolicyEvaluationResult(
            decision=PolicyDecision.APPROVED,
            rule_name="POLICY_CHECKS_PASSED",
            reason=f"Policy checks passed. Authorized for {proposed_action_type}.",
            policy_version=cls.POLICY_VERSION,
            requires_human_approval=False,
            allowed_action_type=proposed_action_type,
            applied_checks=checks_log
        )
