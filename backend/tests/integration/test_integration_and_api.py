import pytest
import hmac
import hashlib
import json
from httpx import AsyncClient
from backend.app.models.merchant import Merchant
from backend.app.models.customer import Customer
from backend.app.models.transaction import Transaction
from backend.app.core.security import hash_identifier


@pytest.mark.asyncio
async def test_health_check_endpoint(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "HEALTHY"
    assert data["service"] == "RecoverAI Agent Engine"


@pytest.mark.asyncio
async def test_dashboard_metrics_endpoint(client: AsyncClient, db_session):
    resp = await client.get("/api/v1/dashboard/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert "revenue_at_risk" in data
    assert "recovered_revenue" in data
    assert "recovery_rate" in data
    assert "baseline_recovered_revenue" in data


@pytest.mark.asyncio
async def test_webhook_signature_and_idempotency(client: AsyncClient, db_session):
    event_id = "evt_test_unique_998877"
    payload = {
        "event": "payment.failed",
        "event_id": event_id,
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_test_failed_123",
                    "amount": 250000,
                    "currency": "INR",
                    "error_code": "GATEWAY_ERROR",
                    "error_description": "Bank timeout",
                }
            }
        }
    }
    raw_body = json.dumps(payload).encode("utf-8")
    secret = "mockwebhooksecret12345"
    sig = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()

    # 1. First Delivery: ACCEPTED
    resp1 = await client.post(
        "/webhooks/razorpay",
        content=raw_body,
        headers={"x-razorpay-signature": sig, "x-razorpay-event-id": event_id, "content-type": "application/json"}
    )
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["status"] == "ACCEPTED"
    assert data1["event_id"] == event_id

    # 2. Duplicate Delivery (Idempotency Test): DUPLICATE_IGNORED
    resp2 = await client.post(
        "/webhooks/razorpay",
        content=raw_body,
        headers={"x-razorpay-signature": sig, "x-razorpay-event-id": event_id, "content-type": "application/json"}
    )
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["status"] == "DUPLICATE_IGNORED"


@pytest.mark.asyncio
async def test_simulation_batch_runner_predefined_scenarios(client: AsyncClient, db_session):
    resp = await client.post(
        "/api/v1/simulation/run",
        json={"scenario_name": "predefined_5_scenarios", "batch_size": 5}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["evaluated_count"] == 5
    assert data["revenue_at_risk"] > 0
    assert "recovery_rate" in data
    assert "cases" in data
    assert len(data["cases"]) == 5


@pytest.mark.asyncio
async def test_end_to_end_recovery_lifecycle(client: AsyncClient, db_session):
    # 1. Create Merchant & Customer & Failed Transaction
    merchant = Merchant(id="mer_test_01", name="Test Merchant", high_value_threshold=10000.0)
    customer = Customer(
        id="cust_test_01",
        merchant_id="mer_test_01",
        name="Test User",
        email_hash=hash_identifier("test@user.com"),
        successful_payment_count=5,
        total_lifetime_value=15000.0,
    )
    tx = Transaction(
        id="tx_e2e_01",
        external_transaction_id="pay_e2e_01",
        merchant_id="mer_test_01",
        customer=customer,
        amount=1999.0,
        currency="INR",
        payment_method="UPI",
        status="FAILED",
        failure_code="GATEWAY_ERROR",
        failure_reason="Bank network timeout",
    )
    db_session.add(merchant)
    db_session.add(customer)
    db_session.add(tx)
    await db_session.commit()

    # 2. Trigger Analysis via API
    # Create preliminary case
    resp_cases = await client.get("/api/v1/transactions/tx_e2e_01")
    assert resp_cases.status_code == 200

    from backend.app.services.recovery_service import RecoveryService
    case = await RecoveryService.analyze_transaction(db_session, "tx_e2e_01", correlation_id="test_corr_01")
    assert case.status in ["SCHEDULED", "EXECUTING", "OPEN"]
    assert case.recommended_action == "RETRY_PAYMENT"

    # 3. Execute recovery action
    action = await RecoveryService.execute_action(db_session, case.id, correlation_id="test_corr_01", force_simulation=True)
    assert action.status == "SUCCESS"
    assert case.status == "RECOVERED"

    # 4. Verify Audit Log was recorded
    resp_audit = await client.get("/api/v1/audit-logs")
    assert resp_audit.status_code == 200
    aud_data = resp_audit.json()
    assert aud_data["count"] >= 1
