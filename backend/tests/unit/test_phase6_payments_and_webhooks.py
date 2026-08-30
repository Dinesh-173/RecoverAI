import json
import hmac
import hashlib
import pytest
from httpx import AsyncClient

from backend.app.core.security import verify_razorpay_webhook_signature, hash_identifier
from backend.app.core.exceptions import WebhookSignatureException, IdempotencyViolationException, PolicyViolationException
from backend.app.providers.payments import get_payment_provider, RazorpayTestAdapter, SimulationPaymentAdapter
from backend.app.workers.event_processor import WebhookEventProcessor
from backend.app.services.recovery_service import RecoveryService
from backend.app.models.merchant import Merchant
from backend.app.models.merchant_policy import MerchantPolicy
from backend.app.models.customer import Customer
from backend.app.models.transaction import Transaction
from backend.app.models.recovery_case import RecoveryCase
from backend.app.models.webhook_event import WebhookEvent
from backend.app.models.audit_log import AuditLog
from sqlalchemy import select


# =====================================================================
# 1. WEBHOOK SIGNATURE VERIFICATION TESTS
# =====================================================================

@pytest.mark.asyncio
async def test_webhook_signature_valid_accepted(client: AsyncClient):
    payload = {"event": "payment.failed", "payload": {"payment": {"entity": {"id": "pay_val_01", "amount": 1000}}}}
    raw_body = json.dumps(payload).encode("utf-8")
    secret = "mockwebhooksecret12345"
    sig = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()

    resp = await client.post(
        "/webhooks/razorpay",
        content=raw_body,
        headers={"x-razorpay-signature": sig, "x-razorpay-event-id": "evt_sig_val_01", "content-type": "application/json"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ACCEPTED"
    assert data["event_id"] == "evt_sig_val_01"


@pytest.mark.asyncio
async def test_webhook_signature_missing_header_rejected(client: AsyncClient):
    payload = {"event": "payment.failed"}
    raw_body = json.dumps(payload).encode("utf-8")

    resp = await client.post(
        "/webhooks/razorpay",
        content=raw_body,
        headers={"x-razorpay-event-id": "evt_missing_sig", "content-type": "application/json"}
    )
    assert resp.status_code == 400
    data = resp.json()
    assert data["error"]["code"] == "INVALID_WEBHOOK_SIGNATURE"


@pytest.mark.asyncio
async def test_webhook_signature_tampered_payload_rejected(client: AsyncClient):
    payload = {"event": "payment.failed"}
    raw_body = json.dumps(payload).encode("utf-8")
    secret = "mockwebhooksecret12345"
    bad_sig = hmac.new(secret.encode("utf-8"), b"tampered_body", hashlib.sha256).hexdigest()

    resp = await client.post(
        "/webhooks/razorpay",
        content=raw_body,
        headers={"x-razorpay-signature": bad_sig, "x-razorpay-event-id": "evt_bad_sig", "content-type": "application/json"}
    )
    assert resp.status_code == 400
    data = resp.json()
    assert data["error"]["code"] == "INVALID_WEBHOOK_SIGNATURE"


# =====================================================================
# 2. WEBHOOK DEDUPLICATION & IDEMPOTENCY TESTS
# =====================================================================

@pytest.mark.asyncio
async def test_webhook_duplicate_event_id_ignored(client: AsyncClient):
    event_id = "evt_dedup_99"
    payload = {"event": "payment.failed", "payload": {"payment": {"entity": {"id": "pay_dedup_01"}}}}
    raw_body = json.dumps(payload).encode("utf-8")
    secret = "mockwebhooksecret12345"
    sig = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()

    # Delivery 1: ACCEPTED
    res1 = await client.post(
        "/webhooks/razorpay",
        content=raw_body,
        headers={"x-razorpay-signature": sig, "x-razorpay-event-id": event_id, "content-type": "application/json"}
    )
    assert res1.status_code == 200
    assert res1.json()["status"] == "ACCEPTED"

    # Delivery 2: DUPLICATE_IGNORED
    res2 = await client.post(
        "/webhooks/razorpay",
        content=raw_body,
        headers={"x-razorpay-signature": sig, "x-razorpay-event-id": event_id, "content-type": "application/json"}
    )
    assert res2.status_code == 200
    assert res2.json()["status"] == "DUPLICATE_IGNORED"


# =====================================================================
# 3. ASYNCHRONOUS EVENT PROCESSOR TESTS
# =====================================================================

@pytest.mark.asyncio
async def test_event_processor_payment_failed_triggers_recovery(db_session):
    merchant = Merchant(id="mer_p6_01", name="P6 Merchant")
    customer = Customer(id="cust_p6_01", merchant_id="mer_p6_01", name="P6 Customer", email_hash=hash_identifier("p6@user.com"))
    tx = Transaction(
        id="tx_p6_01",
        merchant_id="mer_p6_01",
        customer=customer,
        amount=1500.0,
        payment_method="CARD",
        status="PENDING",
        external_transaction_id="pay_p6_failed_100",
    )
    db_session.add(merchant)
    db_session.add(customer)
    db_session.add(tx)
    await db_session.commit()

    webhook_evt = WebhookEvent(
        razorpay_event_id="evt_p6_01",
        event_type="payment.failed",
        payload_hash="hash_p6_01",
        payload_json={
            "event": "payment.failed",
            "payload": {
                "payment": {
                    "entity": {
                        "id": "pay_p6_failed_100",
                        "error_code": "GATEWAY_ERROR",
                        "error_description": "Issuer timeout",
                    }
                }
            }
        },
        status="RECEIVED",
    )
    db_session.add(webhook_evt)
    await db_session.commit()

    # Process event asynchronously
    await WebhookEventProcessor.process_event(db_session, webhook_evt.id)

    # Verify event status is PROCESSED
    evt_stmt = select(WebhookEvent).where(WebhookEvent.id == webhook_evt.id)
    evt_res = await db_session.execute(evt_stmt)
    updated_evt = evt_res.scalar_one()
    assert updated_evt.status == "PROCESSED"

    # Verify transaction status updated to FAILED
    tx_stmt = select(Transaction).where(Transaction.id == tx.id)
    tx_res = await db_session.execute(tx_stmt)
    updated_tx = tx_res.scalar_one()
    assert updated_tx.status == "FAILED"
    assert updated_tx.failure_code == "GATEWAY_ERROR"

    # Verify RecoveryCase was created
    stmt = select(RecoveryCase).where(RecoveryCase.transaction_id == tx.id)
    res = await db_session.execute(stmt)
    case = res.scalar_one_or_none()
    assert case is not None
    assert case.status in ["SCHEDULED", "EXECUTING", "WAITING_APPROVAL", "STOPPED"]


@pytest.mark.asyncio
async def test_event_processor_payment_captured_updates_status(db_session):
    merchant = Merchant(id="mer_p6_02", name="P6 Merchant 2")
    customer = Customer(id="cust_p6_02", merchant_id="mer_p6_02", name="P6 Cust 2", email_hash=hash_identifier("p6_2@user.com"))
    tx = Transaction(
        id="tx_p6_02",
        merchant_id="mer_p6_02",
        customer=customer,
        amount=3000.0,
        payment_method="UPI",
        status="PENDING",
        external_transaction_id="pay_p6_captured_200",
    )
    db_session.add(merchant)
    db_session.add(customer)
    db_session.add(tx)
    await db_session.commit()

    webhook_evt = WebhookEvent(
        razorpay_event_id="evt_p6_02",
        event_type="payment.captured",
        payload_hash="hash_p6_02",
        payload_json={"event": "payment.captured", "payload": {"payment": {"entity": {"id": "pay_p6_captured_200"}}}},
        status="RECEIVED",
    )
    db_session.add(webhook_evt)
    await db_session.commit()

    await WebhookEventProcessor.process_event(db_session, webhook_evt.id)

    tx_stmt = select(Transaction).where(Transaction.id == tx.id)
    tx_res = await db_session.execute(tx_stmt)
    updated_tx = tx_res.scalar_one()
    assert updated_tx.status == "CAPTURED"


# =====================================================================
# 4. PAYMENT ADAPTER & FACTORY TESTS
# =====================================================================

def test_get_payment_provider_factory():
    provider_sim = get_payment_provider(force_simulation=True)
    assert isinstance(provider_sim, SimulationPaymentAdapter)


@pytest.mark.asyncio
async def test_simulation_adapter_execution():
    adapter = SimulationPaymentAdapter()

    res_link = await adapter.create_payment_link(
        amount=2500.0,
        currency="INR",
        description="Test link",
        customer_name="Test User",
        customer_email="test@example.com",
        reference_id="ref_sim_01",
    )
    assert res_link["status"] == "SUCCESS"
    assert res_link["is_simulation"] is True
    assert "DEMO / SIMULATION ONLY" in res_link["notice"]

    res_exec = await adapter.execute_bounded_recovery(
        transaction_id="tx_test_100",
        action_type="RETRY_PAYMENT",
        amount=2500.0,
        currency="INR",
        customer_info={"name": "Test User", "email": "test@example.com"},
    )
    assert res_exec["status"] == "SUCCESS"
    assert res_exec["provider"] == "SIMULATION_ADAPTER"


# =====================================================================
# 5. ACTION EXECUTION & CUSTOMER STATS INTEGRATION
# =====================================================================

@pytest.mark.asyncio
async def test_execute_action_updates_customer_stats_and_audit(db_session):
    merchant = Merchant(id="mer_p6_03", name="P6 Merchant 3")
    customer = Customer(
        id="cust_p6_03",
        merchant_id="mer_p6_03",
        name="P6 Cust 3",
        email_hash=hash_identifier("p6_3@user.com"),
        successful_payment_count=1,
        total_lifetime_value=1000.0,
    )
    tx = Transaction(
        id="tx_p6_03",
        merchant_id="mer_p6_03",
        customer=customer,
        amount=4000.0,
        payment_method="UPI",
        status="FAILED",
        failure_code="GATEWAY_ERROR",
    )
    rec_case = RecoveryCase(
        id="case_p6_03",
        transaction=tx,
        status="EXECUTING",
        recommended_action="RETRY_PAYMENT",
        diagnosis="Transient bank downtime.",
    )
    db_session.add(merchant)
    db_session.add(customer)
    db_session.add(tx)
    db_session.add(rec_case)
    await db_session.commit()

    # Execute recovery action in simulation mode
    action_rec = await RecoveryService.execute_action(
        db=db_session,
        case_id="case_p6_03",
        correlation_id="corr_p6_exec_300",
        force_simulation=True,
    )

    assert action_rec.status == "SUCCESS"
    assert action_rec.action_type == "RETRY_PAYMENT"

    # Verify case, transaction, and customer updated via select queries
    case_res = await db_session.execute(select(RecoveryCase).where(RecoveryCase.id == "case_p6_03"))
    updated_case = case_res.scalar_one()

    tx_res = await db_session.execute(select(Transaction).where(Transaction.id == "tx_p6_03"))
    updated_tx = tx_res.scalar_one()

    cust_res = await db_session.execute(select(Customer).where(Customer.id == "cust_p6_03"))
    updated_cust = cust_res.scalar_one()

    assert updated_case.status == "RECOVERED"
    assert updated_tx.status == "CAPTURED"
    assert updated_cust.successful_payment_count == 2
    assert updated_cust.total_lifetime_value == 5000.0  # 1000 + 4000

    # Verify Audit Log entry created
    stmt_audit = select(AuditLog).where(AuditLog.entity_id == action_rec.id)
    res_audit = await db_session.execute(stmt_audit)
    audit = res_audit.scalar_one_or_none()
    assert audit is not None
    assert audit.action == "EXECUTE_RETRY_PAYMENT"
    assert audit.correlation_id == "corr_p6_exec_300"


@pytest.mark.asyncio
async def test_execute_action_idempotency_guard(db_session):
    merchant = Merchant(id="mer_p6_04", name="P6 Merchant 4")
    customer = Customer(id="cust_p6_04", merchant_id="mer_p6_04", name="P6 Cust 4", email_hash=hash_identifier("p6_4@user.com"))
    tx = Transaction(id="tx_p6_04", merchant_id="mer_p6_04", customer=customer, amount=1000.0, status="CAPTURED")
    rec_case = RecoveryCase(id="case_p6_04", transaction=tx, status="RECOVERED", recommended_action="RETRY_PAYMENT")

    db_session.add(merchant)
    db_session.add(customer)
    db_session.add(tx)
    db_session.add(rec_case)
    await db_session.commit()

    # Attempting to execute on terminal RECOVERED case must raise PolicyViolationException
    with pytest.raises(PolicyViolationException, match="already in terminal status"):
        await RecoveryService.execute_action(db=db_session, case_id="case_p6_04", force_simulation=True)
