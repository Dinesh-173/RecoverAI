import pytest
from backend.app.policies.engine import DeterministicPolicyEngine
from backend.app.policies.rules import PolicyDecision
from backend.app.agents.schemas import AgentDiagnosticOutput, ProposedActionSpec


def test_policy_approves_valid_delayed_retry():
    proposal = AgentDiagnosticOutput(
        diagnosis="Transient bank downtime.",
        recovery_strategy="DELAYED_RETRY",
        confidence=0.88,
        reason_codes=["TRANSIENT_FAILURE"],
        requires_human_approval=False,
        proposed_action=ProposedActionSpec(type="RETRY_PAYMENT", delay_minutes=45),
    )
    tx_data = {"amount": 1500.0, "attempt_number": 1, "status": "FAILED"}
    cust_data = {"communication_opt_out": False}
    merchant_policy = {"high_value_threshold": 10000.0, "max_retries": 2, "min_ai_confidence": 0.70, "min_recovery_score": 15.0}

    result = DeterministicPolicyEngine.evaluate(proposal, tx_data, cust_data, merchant_policy, recovery_score=25.0)
    assert result.decision == PolicyDecision.APPROVED
    assert result.requires_human_approval is False


def test_policy_blocks_opted_out_customer_notifications():
    proposal = AgentDiagnosticOutput(
        diagnosis="Insufficient balance on card.",
        recovery_strategy="CUSTOMER_NOTIFICATION",
        confidence=0.85,
        reason_codes=["INSUFFICIENT_FUNDS"],
        requires_human_approval=False,
        proposed_action=ProposedActionSpec(type="CUSTOMER_NOTIFICATION", delay_minutes=60),
    )
    tx_data = {"amount": 2000.0, "attempt_number": 1, "status": "FAILED"}
    cust_data = {"communication_opt_out": True} # Customer opted out
    merchant_policy = {"high_value_threshold": 10000.0, "max_retries": 2, "min_ai_confidence": 0.70, "min_recovery_score": 15.0}

    result = DeterministicPolicyEngine.evaluate(proposal, tx_data, cust_data, merchant_policy, recovery_score=20.0)
    assert result.decision == PolicyDecision.BLOCKED
    assert "opted out" in result.reason.lower()


def test_policy_stops_exceeded_max_retries():
    proposal = AgentDiagnosticOutput(
        diagnosis="Gateway retry attempt.",
        recovery_strategy="DELAYED_RETRY",
        confidence=0.82,
        reason_codes=["GATEWAY_ERROR"],
        requires_human_approval=False,
        proposed_action=ProposedActionSpec(type="RETRY_PAYMENT", delay_minutes=30),
    )
    tx_data = {"amount": 1000.0, "attempt_number": 2, "status": "FAILED"} # Attempt 2 meets limit of 2
    cust_data = {"communication_opt_out": False}
    merchant_policy = {"high_value_threshold": 10000.0, "max_retries": 2, "min_ai_confidence": 0.70, "min_recovery_score": 15.0}

    result = DeterministicPolicyEngine.evaluate(proposal, tx_data, cust_data, merchant_policy, recovery_score=20.0)
    assert result.decision == PolicyDecision.STOPPED
    assert "max retry limit" in result.reason.lower()


def test_policy_escalates_high_value_transactions():
    proposal = AgentDiagnosticOutput(
        diagnosis="High value B2B transaction failed.",
        recovery_strategy="DELAYED_RETRY",
        confidence=0.92,
        reason_codes=["TRANSIENT_FAILURE"],
        requires_human_approval=False,
        proposed_action=ProposedActionSpec(type="RETRY_PAYMENT", delay_minutes=30),
    )
    tx_data = {"amount": 45000.0, "attempt_number": 1, "status": "FAILED"} # Exceeds 10000 limit
    cust_data = {"communication_opt_out": False}
    merchant_policy = {"high_value_threshold": 10000.0, "max_retries": 2, "min_ai_confidence": 0.70, "min_recovery_score": 15.0}

    result = DeterministicPolicyEngine.evaluate(proposal, tx_data, cust_data, merchant_policy, recovery_score=80.0)
    assert result.decision == PolicyDecision.ESCALATED_HUMAN_APPROVAL
    assert result.requires_human_approval is True
    assert "high-value" in result.reason.lower()


def test_policy_escalates_low_confidence_decisions():
    proposal = AgentDiagnosticOutput(
        diagnosis="Ambiguous failure reason.",
        recovery_strategy="DELAYED_RETRY",
        confidence=0.55, # Below 0.70 threshold
        reason_codes=["UNCERTAIN_FAILURE"],
        requires_human_approval=False,
        proposed_action=ProposedActionSpec(type="RETRY_PAYMENT", delay_minutes=60),
    )
    tx_data = {"amount": 3000.0, "attempt_number": 1, "status": "FAILED"}
    cust_data = {"communication_opt_out": False}
    merchant_policy = {"high_value_threshold": 10000.0, "max_retries": 2, "min_ai_confidence": 0.70, "min_recovery_score": 15.0}

    result = DeterministicPolicyEngine.evaluate(proposal, tx_data, cust_data, merchant_policy, recovery_score=20.0)
    assert result.decision == PolicyDecision.ESCALATED_HUMAN_APPROVAL
    assert result.requires_human_approval is True
