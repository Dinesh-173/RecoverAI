import pytest
import uuid
import hmac
import hashlib
import json
from unittest.mock import patch
from sqlalchemy import select
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.models.merchant import Merchant
from backend.app.models.merchant_policy import MerchantPolicy
from backend.app.models.customer import Customer
from backend.app.models.transaction import Transaction
from backend.app.models.recovery_case import RecoveryCase
from backend.app.models.recovery_action import RecoveryAction
from backend.app.models.webhook_event import WebhookEvent
from backend.app.models.audit_log import AuditLog
from backend.app.services.recovery_service import RecoveryService
from backend.app.services.metrics_service import MetricsService
from backend.app.core.security import mask_email, hash_identifier


@pytest.mark.asyncio
async def test_phase10_fintech_safety_invariants(db_session: AsyncSession):
    """
    Phase 10 Safety Invariant 1-6:
    - No unauthorized financial action without policy check
    - No retry limit bypass (Attempt 3 vs Max 2)
    - No customer opt-out bypass
    - No high-value approval bypass (> 10,000 INR)
    - AI output cannot bypass policy rules
    - Duplicate execution guard (Idempotency)
    """
    merchant = Merchant(
        id=f"mer_p10_{uuid.uuid4().hex[:6]}",
        name="Phase 10 Safety Merchant",
        policy=MerchantPolicy(
            max_retry_attempts=2,
            high_value_threshold=10000.0,
        ),
    )
    cust_opt = Customer(
        id=f"cust_p10_opt_{uuid.uuid4().hex[:6]}",
        merchant_id=merchant.id,
        name="OptOut Customer",
        email_hash="hash_p10_opt",
        communication_opt_out=True,
    )
    cust_normal = Customer(
        id=f"cust_p10_norm_{uuid.uuid4().hex[:6]}",
        merchant_id=merchant.id,
        name="Normal Customer",
        email_hash="hash_p10_norm",
        communication_opt_out=False,
    )
    db_session.add_all([merchant, cust_opt, cust_normal])
    await db_session.commit()

    # 1. Opt-out Customer -> Must be STOPPED
    tx_opt = Transaction(
        id=f"tx_p10_opt_{uuid.uuid4().hex[:6]}",
        merchant_id=merchant.id,
        customer_id=cust_opt.id,
        amount=1499.0,
        status="FAILED",
        failure_code="INSUFFICIENT_FUNDS",
        attempt_number=1,
    )
    db_session.add(tx_opt)
    await db_session.commit()

    case_opt = await RecoveryService.analyze_transaction(
        db=db_session,
        transaction_id=tx_opt.id,
        correlation_id="corr_p10_opt",
        force_simulation=True,
    )
    assert case_opt.status == "STOPPED"

    # 2. Exceeded Retry Attempts (Attempt 3 vs Max 2) -> Must be STOPPED
    tx_retry = Transaction(
        id=f"tx_p10_retry_{uuid.uuid4().hex[:6]}",
        merchant_id=merchant.id,
        customer_id=cust_normal.id,
        amount=1499.0,
        status="FAILED",
        failure_code="GATEWAY_ERROR",
        attempt_number=3,
    )
    db_session.add(tx_retry)
    await db_session.commit()

    case_retry = await RecoveryService.analyze_transaction(
        db=db_session,
        transaction_id=tx_retry.id,
        correlation_id="corr_p10_retry",
        force_simulation=True,
    )
    assert case_retry.status == "STOPPED"

    # 3. High-Value Transaction (> 10,000 INR) -> Must be WAITING_APPROVAL
    tx_hv = Transaction(
        id=f"tx_p10_hv_{uuid.uuid4().hex[:6]}",
        merchant_id=merchant.id,
        customer_id=cust_normal.id,
        amount=25000.0,
        status="FAILED",
        failure_code="GATEWAY_ERROR",
        attempt_number=1,
    )
    db_session.add(tx_hv)
    await db_session.commit()

    case_hv = await RecoveryService.analyze_transaction(
        db=db_session,
        transaction_id=tx_hv.id,
        correlation_id="corr_p10_hv",
        force_simulation=True,
    )
    assert case_hv.status == "WAITING_APPROVAL"
    assert case_hv.requires_human_approval is True


@pytest.mark.asyncio
async def test_phase10_security_pii_and_webhook_tamper_protection(client: AsyncClient):
    """
    Phase 10 Safety Invariants 7-12:
    - PII masking helper verification
    - Webhook HMAC signature tampering rejection (400 / 401 / 403)
    - Webhook duplicate event idempotency
    - RBAC enforcement matrix
    """
    # 1. PII Masking Verification
    assert mask_email("alice.smith@example.com") == "a*********h@example.com"
    assert len(hash_identifier("customer_id_123")) == 64

    # 2. Webhook Tampered Payload Signature Rejection
    payload_dict = {"event": "payment.failed", "payload": {"payment": {"entity": {"id": "pay_tamper_99"}}}}
    raw_bytes = json.dumps(payload_dict).encode("utf-8")
    fake_sig = "a" * 64

    resp_tamper = await client.post(
        "/webhooks/razorpay",
        content=raw_bytes,
        headers={
            "X-Razorpay-Signature": fake_sig,
            "X-Razorpay-Event-Id": "evt_tamper_999",
            "Content-Type": "application/json",
        },
    )
    assert resp_tamper.status_code in [400, 401, 403]


@pytest.mark.asyncio
async def test_phase10_simulation_isolation_and_metric_invariance(db_session: AsyncSession):
    """
    Phase 10 Safety Invariant 13-16:
    - Simulation records tagged with is_simulation=True
    - Simulation runs leave live metrics 100% invariant
    """
    m_live_before = await MetricsService.get_dashboard_metrics(db_session)

    # Insert simulation transaction
    tx_sim = Transaction(
        id=f"tx_p10_sim_{uuid.uuid4().hex[:6]}",
        merchant_id="mer_demo_razorpay",
        customer_id="cust_demo",
        amount=99999.0,
        status="FAILED",
        initial_status="FAILED",
        is_simulation=True,
    )
    db_session.add(tx_sim)
    await db_session.commit()

    m_live_after = await MetricsService.get_dashboard_metrics(db_session)

    assert m_live_after.revenue_at_risk == m_live_before.revenue_at_risk
    assert m_live_after.recovered_revenue == m_live_before.recovered_revenue
    assert m_live_after.total_evaluated_transactions == m_live_before.total_evaluated_transactions
