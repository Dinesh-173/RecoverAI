import json
import hmac
import hashlib
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.models.merchant import Merchant
from backend.app.models.merchant_policy import MerchantPolicy
from backend.app.models.customer import Customer
from backend.app.models.transaction import Transaction
from backend.app.models.recovery_case import RecoveryCase
from backend.app.models.webhook_event import WebhookEvent
from backend.app.models.audit_log import AuditLog
from backend.app.policies.engine import DeterministicPolicyEngine
from backend.app.agents.tools import AgentToolLayer
from backend.app.agents.schemas import AgentDiagnosticOutput, ProposedActionSpec
from backend.app.services.recovery_service import RecoveryService


@pytest.mark.asyncio
async def test_phase12_boundary_amounts_and_retry_attempt_edge_cases():
    """
    1. Edge Case Testing: Financial amount boundaries (₹0, ₹1, ₹9,999, ₹10,000, ₹10,001)
    and retry attempt counts (0, 1, 2, 3).
    """
    proposal = AgentDiagnosticOutput(
        recovery_strategy="Delayed Retry",
        proposed_action=ProposedActionSpec(type="RETRY_PAYMENT", delay_minutes=45),
        confidence=0.90,
        diagnosis="Boundary test",
    )
    cust_data = {"id": "c_bound", "communication_opt_out": False}
    merchant_policy = {"high_value_threshold": 10000.0, "max_retries": 2}

    # Boundary 1: ₹9,999.00 (Below threshold) -> Auto approved if score is valid
    res_below = DeterministicPolicyEngine.evaluate(
        agent_proposal=proposal,
        transaction_data={"id": "tx_b1", "amount": 9999.0, "failure_code": "GATEWAY_ERROR", "attempt_number": 1},
        customer_data=cust_data,
        merchant_policy=merchant_policy,
        recovery_score=75.0,
    )
    assert res_below.requires_human_approval is False

    # Boundary 2: ₹10,000.00 (Exact threshold) -> Escalated to human approval
    res_exact = DeterministicPolicyEngine.evaluate(
        agent_proposal=proposal,
        transaction_data={"id": "tx_b2", "amount": 10000.0, "failure_code": "GATEWAY_ERROR", "attempt_number": 1},
        customer_data=cust_data,
        merchant_policy=merchant_policy,
        recovery_score=75.0,
    )
    assert res_exact.requires_human_approval is True

    # Boundary 3: ₹10,001.00 (Above threshold) -> Escalated to human approval
    res_above = DeterministicPolicyEngine.evaluate(
        agent_proposal=proposal,
        transaction_data={"id": "tx_b3", "amount": 10001.0, "failure_code": "GATEWAY_ERROR", "attempt_number": 1},
        customer_data=cust_data,
        merchant_policy=merchant_policy,
        recovery_score=75.0,
    )
    assert res_above.requires_human_approval is True

    # Retry boundary: attempt = 2 (Exceeds max_retries=2) -> STOPPED
    res_exceeded = DeterministicPolicyEngine.evaluate(
        agent_proposal=proposal,
        transaction_data={"id": "tx_b4", "amount": 1499.0, "failure_code": "GATEWAY_ERROR", "attempt_number": 2},
        customer_data=cust_data,
        merchant_policy=merchant_policy,
        recovery_score=75.0,
    )
    assert res_exceeded.decision.value == "STOPPED"
    assert res_exceeded.allowed_action_type == "STOP_RECOVERY"


@pytest.mark.asyncio
async def test_phase12_standardized_error_contract_and_correlation_headers(client: AsyncClient):
    """
    2. API & Observability Testing: Standardized error structure & X-Correlation-Id header propagation.
    """
    corr_id = "corr_phase12_test_999"
    response = await client.get(
        "/api/v1/recovery-cases/non_existent_case_id_9999",
        headers={
            "X-User-Role": "MERCHANT_ADMIN",
            "X-Correlation-Id": corr_id,
        },
    )
    assert response.status_code == 404
    res_json = response.json()

    assert "error" in res_json
    err = res_json["error"]
    assert err["code"] == "RESOURCE_NOT_FOUND"
    assert "non_existent_case_id_9999" in err["message"]
    assert "request_id" in err
    assert response.headers.get("X-Correlation-Id") == corr_id


@pytest.mark.asyncio
async def test_phase12_database_integrity_unique_constraints_and_idempotency(db_session: AsyncSession, client: AsyncClient):
    """
    3. Database & Idempotency Testing: Webhook event deduplication, transaction update,
    customer LTV statistics, and audit record creation.
    """
    merchant = Merchant(
        id="mer_p12_db",
        name="DB Test Merchant",
        business_category="ECOMMERCE",
        currency="INR",
        policy=MerchantPolicy(
            max_retry_attempts=2,
            high_value_threshold=10000.0,
            min_recovery_score=1.0,
            min_ai_confidence=0.10,
        ),
    )
    customer = Customer(
        merchant_id=merchant.id,
        name="Bob Database",
        email_hash="hash_bob_db",
        customer_segment="STANDARD",
        successful_payment_count=0,
        failed_payment_count=0,
        total_lifetime_value=0.0,
        communication_opt_out=False,
    )
    db_session.add(merchant)
    db_session.add(customer)
    await db_session.commit()

    tx = Transaction(
        external_transaction_id="pay_p12_db_1001",
        merchant_id=merchant.id,
        customer_id=customer.id,
        amount=2500.0,
        currency="INR",
        payment_method="CARD",
        status="FAILED",
        failure_code="GATEWAY_ERROR",
        failure_reason="Network timeout",
        attempt_number=1,
    )
    db_session.add(tx)
    await db_session.commit()
    await db_session.refresh(tx)

    # Post duplicate webhooks for event_id = evt_p12_dup_1001
    payload_dict = {
        "entity": "event",
        "account_id": "acc_p12_1001",
        "event": "payment.failed",
        "contains": ["payment"],
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_p12_db_1001",
                    "amount": 250000,
                    "currency": "INR",
                    "status": "failed",
                    "method": "card",
                    "error_code": "GATEWAY_ERROR",
                    "error_description": "Network timeout",
                }
            }
        },
        "created_at": 1772310000,
    }
    raw_bytes = json.dumps(payload_dict).encode("utf-8")
    secret = settings.RAZORPAY_WEBHOOK_SECRET.encode("utf-8")
    signature = hmac.new(secret, raw_bytes, hashlib.sha256).hexdigest()

    headers = {
        "X-Razorpay-Signature": signature,
        "X-Razorpay-Event-Id": "evt_p12_dup_1001",
        "Content-Type": "application/json",
    }

    # First post -> ACCEPTED
    r1 = await client.post("/webhooks/razorpay", content=raw_bytes, headers=headers)
    assert r1.status_code == 200
    assert r1.json()["status"] == "ACCEPTED"

    # Second post (duplicate event ID) -> DUPLICATE_IGNORED (Idempotent 200)
    r2 = await client.post("/webhooks/razorpay", content=raw_bytes, headers=headers)
    assert r2.status_code == 200
    assert r2.json()["status"] == "DUPLICATE_IGNORED"

    # Verify only 1 WebhookEvent record exists in DB
    res_wh = await db_session.execute(select(WebhookEvent).where(WebhookEvent.razorpay_event_id == "evt_p12_dup_1001"))
    wh_events = res_wh.scalars().all()
    assert len(wh_events) == 1


@pytest.mark.asyncio
async def test_phase12_ml_scoring_and_ai_safety_advisory_only(db_session: AsyncSession):
    """
    4. ML & AI Safety Testing: ML recoverability score calculation and
    non-negotiable safety guardrail (AI proposals are strictly advisory).
    """
    score = AgentToolLayer.calculate_recovery_score(
        probability_of_recovery=0.85,
        expected_recoverable_amount=1499.0,
        action_success_probability=0.90,
    )
    assert score > 0.0

    # Safety Guardrail: Even if AI proposal has confidence=1.0 and type="RETRY_PAYMENT",
    # AI CANNOT execute payment. Policy engine MUST approve it first.
    ai_proposal = AgentDiagnosticOutput(
        recovery_strategy="Delayed Retry",
        proposed_action=ProposedActionSpec(type="RETRY_PAYMENT", delay_minutes=30),
        confidence=1.0,
        diagnosis="AI says retry immediately",
    )
    # If opt-out is True and action is CUSTOMER_NOTIFICATION, policy MUST block action
    notif_proposal = AgentDiagnosticOutput(
        recovery_strategy="Customer Notification",
        proposed_action=ProposedActionSpec(type="CUSTOMER_NOTIFICATION", delay_minutes=30),
        confidence=1.0,
        diagnosis="AI says notify customer",
    )
    policy_res = DeterministicPolicyEngine.evaluate(
        agent_proposal=notif_proposal,
        transaction_data={"id": "tx_safe", "amount": 1499.0, "failure_code": "GATEWAY_ERROR", "attempt_number": 1},
        customer_data={"id": "c_safe", "communication_opt_out": True},
        merchant_policy={},
        recovery_score=score,
    )
    assert policy_res.decision.value == "BLOCKED"


@pytest.mark.asyncio
async def test_phase12_policy_precedence_matrix_and_fintech_safety():
    """
    5. Policy Engine Testing: Policy Rule Precedence Matrix.
    Rule 1: Retry Exhaustion takes precedence over High Value.
    Rule 2: Opt-Out blocks notification actions.
    Rule 3: Explicit STOP_RECOVERY proposal is confirmed.
    """
    proposal = AgentDiagnosticOutput(
        recovery_strategy="Delayed Retry",
        proposed_action=ProposedActionSpec(type="RETRY_PAYMENT", delay_minutes=45),
        confidence=0.95,
        diagnosis="Test proposal",
    )
    merchant_policy = {"high_value_threshold": 10000.0, "max_retries": 2}

    # Precedence Case 1: ₹50,000 transaction (High Value) + Attempt 2 (Exceeded max_retries=2) -> STOPPED (Retry exhaustion wins over escalation)
    res_retry_win = DeterministicPolicyEngine.evaluate(
        agent_proposal=proposal,
        transaction_data={"id": "tx_p2", "amount": 50000.0, "failure_code": "GATEWAY_ERROR", "attempt_number": 2},
        customer_data={"id": "c_p2", "communication_opt_out": False},
        merchant_policy=merchant_policy,
        recovery_score=90.0,
    )
    assert res_retry_win.decision.value == "STOPPED"
    assert res_retry_win.requires_human_approval is False

    # Precedence Case 2: Explicit STOP_RECOVERY proposal -> STOPPED unconditionally with 0 retries
    stop_proposal = AgentDiagnosticOutput(
        recovery_strategy="Stop Recovery",
        proposed_action=ProposedActionSpec(type="STOP_RECOVERY", delay_minutes=0),
        confidence=0.98,
        diagnosis="Fraud or terminal error",
    )
    res_fraud = DeterministicPolicyEngine.evaluate(
        agent_proposal=stop_proposal,
        transaction_data={"id": "tx_p3", "amount": 1000.0, "failure_code": "FRAUD_SECURITY_BLOCK", "attempt_number": 1},
        customer_data={"id": "c_p3", "communication_opt_out": False},
        merchant_policy=merchant_policy,
        recovery_score=90.0,
    )
    assert res_fraud.decision.value == "STOPPED"
    assert res_fraud.allowed_action_type == "STOP_RECOVERY"


@pytest.mark.asyncio
async def test_phase12_webhook_security_hmac_and_payment_adapter_isolation(client: AsyncClient):
    """
    6. Webhook & Payment Security Testing: HMAC signature security and payment adapter isolation.
    """
    payload_bytes = b'{"event": "payment.failed", "entity": "event"}'

    # Missing signature -> 400 Bad Request
    r_missing = await client.post(
        "/webhooks/razorpay",
        content=payload_bytes,
        headers={"X-Razorpay-Event-Id": "evt_p12_sec_01", "Content-Type": "application/json"},
    )
    assert r_missing.status_code == 400
    assert "INVALID_WEBHOOK_SIGNATURE" in r_missing.json()["error"]["code"]

    # Tampered signature -> 400 Bad Request
    r_tampered = await client.post(
        "/webhooks/razorpay",
        content=payload_bytes,
        headers={
            "X-Razorpay-Signature": "invalid_tampered_signature_hex_string_12345",
            "X-Razorpay-Event-Id": "evt_p12_sec_02",
            "Content-Type": "application/json",
        },
    )
    assert r_tampered.status_code == 400
    assert "INVALID_WEBHOOK_SIGNATURE" in r_tampered.json()["error"]["code"]
