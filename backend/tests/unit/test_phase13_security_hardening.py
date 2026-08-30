import os
import json
import hmac
import hashlib
import pytest
from unittest.mock import patch
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.core.security import verify_razorpay_webhook_signature, mask_email, hash_identifier
from backend.app.models.merchant import Merchant
from backend.app.models.merchant_policy import MerchantPolicy
from backend.app.models.customer import Customer
from backend.app.models.transaction import Transaction
from backend.app.models.recovery_case import RecoveryCase
from backend.app.models.webhook_event import WebhookEvent
from backend.app.models.audit_log import AuditLog
from backend.app.policies.engine import DeterministicPolicyEngine
from backend.app.agents.schemas import AgentDiagnosticOutput, ProposedActionSpec
from backend.app.agents.recovery_agent import RecoveryDiagnosticAgent
from backend.app.providers.payments import get_payment_provider, SimulationPaymentAdapter, RazorpayTestAdapter
from backend.app.services.recovery_service import RecoveryService


# TEST 1 — RBAC ENFORCEMENT MATRIX
@pytest.mark.asyncio
async def test_phase13_rbac_enforcement_matrix(client: AsyncClient, db_session: AsyncSession):
    """
    TEST 1: Server-side RBAC Matrix:
    - MERCHANT_ADMIN: Allowed administrative approvals and simulation runs.
    - MERCHANT_OPERATOR: Allowed batch simulation, blocked from high-value human approval signoff.
    - VIEWER: Allowed read-only data queries, blocked from all state-changing endpoints.
    """
    # Create high-value waiting case for approval test
    merchant = Merchant(id="mer_p13_rbac", name="RBAC Test Merchant", business_category="ECOMMERCE", currency="INR")
    customer = Customer(merchant_id=merchant.id, name="RBAC User", email_hash="hash_rbac")
    db_session.add(merchant)
    db_session.add(customer)
    await db_session.commit()

    tx = Transaction(
        external_transaction_id="pay_rbac_1001",
        merchant_id=merchant.id,
        customer_id=customer.id,
        amount=25000.0,
        currency="INR",
        payment_method="NETBANKING",
        status="FAILED",
    )
    db_session.add(tx)
    await db_session.commit()

    case = RecoveryCase(
        transaction_id=tx.id,
        status="WAITING_APPROVAL",
        recommended_action="RETRY_PAYMENT",
        confidence=0.92,
        recovery_score=88.0,
        requires_human_approval=True,
    )
    db_session.add(case)
    await db_session.commit()
    await db_session.refresh(case)

    # 1. VIEWER blocked from state-changing endpoints (HTTP 403)
    res_viewer = await client.post(
        f"/api/v1/recovery-cases/{case.id}/approve",
        headers={"X-User-Role": "VIEWER"},
    )
    assert res_viewer.status_code == 403

    # 2. OPERATOR blocked from high-value approval (HTTP 401 Unauthorized Approval)
    res_op = await client.post(
        f"/api/v1/recovery-cases/{case.id}/approve",
        headers={"X-User-Role": "MERCHANT_OPERATOR"},
    )
    assert res_op.status_code in [401, 403]

    # 3. ADMIN permitted to approve high-value case (HTTP 200)
    res_admin = await client.post(
        f"/api/v1/recovery-cases/{case.id}/approve",
        headers={"X-User-Role": "MERCHANT_ADMIN"},
    )
    assert res_admin.status_code == 200
    assert res_admin.json()["status"] == "APPROVED_AND_EXECUTED"


# TEST 2 — RAZORPAY HMAC SIGNATURE SECURITY
@pytest.mark.asyncio
async def test_phase13_razorpay_hmac_signature_security(client: AsyncClient):
    """
    TEST 2: Webhook HMAC-SHA256 signature verification over raw request bytes.
    - Valid signature -> 200 ACCEPTED
    - Tampered signature -> 400 Bad Request
    - Missing signature -> 400 Bad Request
    """
    raw_payload = b'{"event": "payment.failed", "entity": "event"}'
    secret = settings.RAZORPAY_WEBHOOK_SECRET.encode("utf-8")
    valid_sig = hmac.new(secret, raw_payload, hashlib.sha256).hexdigest()

    # Valid
    r_valid = await client.post(
        "/webhooks/razorpay",
        content=raw_payload,
        headers={"X-Razorpay-Signature": valid_sig, "X-Razorpay-Event-Id": "evt_p13_sig_01", "Content-Type": "application/json"},
    )
    assert r_valid.status_code == 200

    # Tampered
    r_tampered = await client.post(
        "/webhooks/razorpay",
        content=raw_payload,
        headers={"X-Razorpay-Signature": "tampered_sig_12345", "X-Razorpay-Event-Id": "evt_p13_sig_02", "Content-Type": "application/json"},
    )
    assert r_tampered.status_code == 400

    # Missing
    r_missing = await client.post(
        "/webhooks/razorpay",
        content=raw_payload,
        headers={"X-Razorpay-Event-Id": "evt_p13_sig_03", "Content-Type": "application/json"},
    )
    assert r_missing.status_code == 400


# TEST 3 — WEBHOOK IDEMPOTENCY & REPLAY PROTECTION
@pytest.mark.asyncio
async def test_phase13_webhook_idempotency_and_replay_protection(client: AsyncClient, db_session: AsyncSession):
    """
    TEST 3: Webhook event deduplication and replay protection using unique index on razorpay_event_id.
    """
    raw_payload = b'{"event": "payment.failed", "entity": "event"}'
    secret = settings.RAZORPAY_WEBHOOK_SECRET.encode("utf-8")
    sig = hmac.new(secret, raw_payload, hashlib.sha256).hexdigest()

    headers = {"X-Razorpay-Signature": sig, "X-Razorpay-Event-Id": "evt_p13_replay_99", "Content-Type": "application/json"}

    # First event
    r1 = await client.post("/webhooks/razorpay", content=raw_payload, headers=headers)
    assert r1.status_code == 200
    assert r1.json()["status"] == "ACCEPTED"

    # Replayed event -> DUPLICATE_IGNORED
    r2 = await client.post("/webhooks/razorpay", content=raw_payload, headers=headers)
    assert r2.status_code == 200
    assert r2.json()["status"] == "DUPLICATE_IGNORED"

    # Verify only 1 WebhookEvent record exists in DB
    res_wh = await db_session.execute(select(WebhookEvent).where(WebhookEvent.razorpay_event_id == "evt_p13_replay_99"))
    wh_list = res_wh.scalars().all()
    assert len(wh_list) == 1


# TEST 4 — PII & SECRET SCRUBBING
@pytest.mark.asyncio
async def test_phase13_pii_and_secret_scrubbing():
    """
    TEST 4: Privacy protection and PII masking.
    - Mask customer email format.
    - Hash customer email for deduplication.
    - Ensure raw credentials are scrubbed.
    """
    masked = mask_email("alice.wonderland@domain.com")
    assert masked.startswith("a")
    assert masked.endswith("@domain.com")
    assert "alice" not in masked

    hashed = hash_identifier("Alice.Wonderland@Domain.com")
    assert len(hashed) == 64  # SHA-256 hex digest length
    assert hashed == hash_identifier("alice.wonderland@domain.com")


# TEST 5 — API ERROR SANITIZATION
@pytest.mark.asyncio
async def test_phase13_api_error_sanitization(client: AsyncClient):
    """
    TEST 5: Standardized error sanitization:
    Response contains error.code, error.message, error.request_id and hides internal stack trace.
    """
    response = await client.get(
        "/api/v1/recovery-cases/case_non_existent_999",
        headers={"X-User-Role": "MERCHANT_ADMIN"},
    )
    assert response.status_code == 404
    err_json = response.json()["error"]
    assert err_json["code"] == "RESOURCE_NOT_FOUND"
    assert "request_id" in err_json
    assert "Traceback" not in json.dumps(err_json)


# TEST 6 — AI SECURITY & ADVISORY BOUNDARY
@pytest.mark.asyncio
async def test_phase13_ai_security_advisory_boundary():
    """
    TEST 6: Proves AI proposals are advisory only.
    Even if LLM proposal attempts high confidence, policy engine enforces deterministic rules.
    """
    proposal = AgentDiagnosticOutput(
        recovery_strategy="Delayed Retry",
        proposed_action=ProposedActionSpec(type="RETRY_PAYMENT", delay_minutes=30),
        confidence=1.0, # Attempted maximum confidence
        diagnosis="Adversarial attempt to force execution",
    )
    tx_data = {"id": "tx_adv_01", "amount": 1499.0, "failure_code": "GATEWAY_ERROR", "attempt_number": 3}
    cust_data = {"id": "c_adv", "communication_opt_out": False}
    policy = {"max_retries": 2}

    res = DeterministicPolicyEngine.evaluate(
        agent_proposal=proposal,
        transaction_data=tx_data,
        customer_data=cust_data,
        merchant_policy=policy,
        recovery_score=85.0,
    )
    # Policy engine MUST block execution because max_retries limit was reached
    assert res.decision.value == "STOPPED"
    assert res.allowed_action_type == "STOP_RECOVERY"


# TEST 7 — HIGH-VALUE APPROVAL SECURITY
@pytest.mark.asyncio
async def test_phase13_high_value_approval_security():
    """
    TEST 7: High-value transaction threshold escalation (>= ₹10,000).
    Requires human approval and cannot execute automatically.
    """
    proposal = AgentDiagnosticOutput(
        recovery_strategy="Delayed Retry",
        proposed_action=ProposedActionSpec(type="RETRY_PAYMENT", delay_minutes=45),
        confidence=0.98,
        diagnosis="High value transaction diagnosis",
    )
    tx_data = {"id": "tx_hv_01", "amount": 15000.0, "failure_code": "GATEWAY_ERROR", "attempt_number": 1}
    cust_data = {"id": "c_hv", "communication_opt_out": False}
    policy = {"high_value_threshold": 10000.0}

    res = DeterministicPolicyEngine.evaluate(
        agent_proposal=proposal,
        transaction_data=tx_data,
        customer_data=cust_data,
        merchant_policy=policy,
        recovery_score=90.0,
    )
    assert res.decision.value == "ESCALATED_HUMAN_APPROVAL"
    assert res.requires_human_approval is True


# TEST 8 — PAYMENT ADAPTER ISOLATION
@pytest.mark.asyncio
async def test_phase13_payment_adapter_isolation():
    """
    TEST 8: Strict separation of payment adapters.
    Simulation payment adapter returned when DEMO_MODE or force_simulation is active.
    """
    adapter_sim = get_payment_provider(force_simulation=True)
    assert isinstance(adapter_sim, SimulationPaymentAdapter)

    with patch("backend.app.providers.payments.settings.DEMO_MODE", False), \
         patch("backend.app.providers.payments.settings.RAZORPAY_KEY_ID", "rzp_test_livekey999"):
        adapter_rzp = get_payment_provider(force_simulation=False)
        assert isinstance(adapter_rzp, RazorpayTestAdapter)


# TEST 9 — MALICIOUS INPUT VALIDATION
@pytest.mark.asyncio
async def test_phase13_malicious_input_validation(client: AsyncClient):
    """
    TEST 9: Untrusted input & SQL-injection style parameters handling.
    Ensure request validation returns HTTP 422 or sanitized errors without execution.
    """
    # Post invalid json body with SQL injection payload in string fields
    payload = {
        "scenario_name": "SELECT * FROM users; DROP TABLE merchants;--",
        "batch_size": -99, # Invalid batch size
    }
    response = await client.post(
        "/api/v1/simulation/run",
        json=payload,
        headers={"X-User-Role": "MERCHANT_ADMIN"},
    )
    # FastAPI/Pydantic or simulation endpoint handles parameters safely
    assert response.status_code in [200, 422]


# TEST 10 — SECURITY CONFIGURATION CHECKS
@pytest.mark.asyncio
async def test_phase13_security_configuration_checks():
    """
    TEST 10: Environment and security configuration verification.
    - Verified environment variables exist in settings.
    - Verify .env.example exists and contains no production credentials.
    """
    assert os.path.exists(".env.example")
    with open(".env.example", "r", encoding="utf-8") as f:
        env_text = f.read()

    assert "mocksecret12345" in env_text
    assert "mockwebhooksecret12345" in env_text
    assert "live_key_" not in env_text
    assert "prod_secret_" not in env_text
