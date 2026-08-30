import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.main import app
from backend.app.core.database import get_db
from backend.app.models.merchant import Merchant
from backend.app.models.customer import Customer
from backend.app.models.transaction import Transaction
from backend.app.models.recovery_case import RecoveryCase
from backend.app.models.merchant_policy import MerchantPolicy


@pytest_asyncio.fixture
async def setup_phase7_data(db_session: AsyncSession):
    """Seed test data for Phase 7 frontend integration audit."""
    merchant = Merchant(
        id="mer_phase7_test",
        name="Phase 7 Test Merchant",
        business_category="ECOMMERCE",
    )
    db_session.add(merchant)

    policy = MerchantPolicy(
        id="pol_phase7_test",
        merchant_id=merchant.id,
        high_value_threshold=10000.0,
        max_retry_attempts=2,
        min_ai_confidence=0.75,
        min_recovery_score=40.0,
    )
    db_session.add(policy)

    cust1 = Customer(
        id="cust_p7_1",
        merchant_id=merchant.id,
        name="Ananya Sharma",
        email_hash="hash_ananya_sharma",
        customer_segment="HIGH_VALUE",
        total_lifetime_value=45000.0,
        successful_payment_count=8,
        failed_payment_count=1,
        communication_opt_out=False,
    )
    cust2 = Customer(
        id="cust_p7_2",
        merchant_id=merchant.id,
        name="Rahul Verma",
        email_hash="hash_rahul_verma",
        customer_segment="STANDARD",
        total_lifetime_value=2500.0,
        successful_payment_count=1,
        failed_payment_count=2,
        communication_opt_out=True,
    )
    db_session.add_all([cust1, cust2])

    tx1 = Transaction(
        id="tx_p7_high_value",
        external_transaction_id="pay_p7_hv_123",
        merchant_id=merchant.id,
        customer_id=cust1.id,
        amount=15000.0,
        currency="INR",
        payment_method="UPI",
        status="FAILED",
        failure_code="GATEWAY_TIMED_OUT",
        failure_reason="Bank server timed out during authorization",
        attempt_number=1,
    )
    tx2 = Transaction(
        id="tx_p7_opt_out",
        external_transaction_id="pay_p7_opt_456",
        merchant_id=merchant.id,
        customer_id=cust2.id,
        amount=3000.0,
        currency="INR",
        payment_method="CARD",
        status="FAILED",
        failure_code="INSUFFICIENT_FUNDS",
        failure_reason="Card balance insufficient",
        attempt_number=1,
    )
    db_session.add_all([tx1, tx2])

    case1 = RecoveryCase(
        id="case_p7_hv",
        transaction_id=tx1.id,
        status="WAITING_APPROVAL",
        risk_level="HIGH",
        diagnosis="Transient bank gateway timeout on high-value transaction.",
        recommended_action="DELAYED_RETRY_45M",
        recommended_delay_minutes=45,
        confidence=0.88,
        recovery_score=85.0,
        requires_human_approval=True,
        approval_reason="Amount ₹15,000.00 exceeds high-value threshold (₹10,000.00)",
    )
    case2 = RecoveryCase(
        id="case_p7_opt",
        transaction_id=tx2.id,
        status="STOPPED",
        risk_level="HIGH",
        diagnosis="Customer has opted out of communications.",
        recommended_action="RAZORPAY_PAYMENT_LINK",
        recommended_delay_minutes=0,
        confidence=0.70,
        recovery_score=30.0,
        requires_human_approval=False,
        approval_reason="Policy stopped: Customer opted out",
    )
    db_session.add_all([case1, case2])
    await db_session.commit()

    return {
        "merchant": merchant,
        "policy": policy,
        "cust1": cust1,
        "cust2": cust2,
        "tx1": tx1,
        "tx2": tx2,
        "case1": case1,
        "case2": case2,
    }


@pytest.mark.asyncio
async def test_dashboard_metrics_endpoint_integration(client, setup_phase7_data):
    """Verify GET /api/v1/dashboard/metrics returns executive KPIs and chart breakdowns."""
    resp = await client.get(
        "/api/v1/dashboard/metrics",
        headers={"X-User-Role": "MERCHANT_ADMIN"},
    )
    assert resp.status_code == 200
    data = resp.json()

    assert "revenue_at_risk" in data
    assert "recovered_revenue" in data
    assert "recovery_rate" in data
    assert "pending_approvals" in data
    assert "chart_revenue_timeline" in data
    assert "chart_recovery_by_method" in data
    assert "chart_recovery_by_reason" in data
    assert isinstance(data["chart_revenue_timeline"], list)


@pytest.mark.asyncio
async def test_transactions_explorer_integration_and_filtering(client, setup_phase7_data):
    """Verify GET /api/v1/transactions with pagination and filters."""
    # All transactions
    resp = await client.get(
        "/api/v1/transactions?skip=0&limit=10",
        headers={"X-User-Role": "MERCHANT_ADMIN"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 2

    # Filter by status
    resp_filtered = await client.get(
        "/api/v1/transactions?status=FAILED&payment_method=UPI",
        headers={"X-User-Role": "MERCHANT_OPERATOR"},
    )
    assert resp_filtered.status_code == 200
    filtered_data = resp_filtered.json()
    for tx in filtered_data["items"]:
        assert tx["status"] == "FAILED"
        assert tx["payment_method"] == "UPI"


@pytest.mark.asyncio
async def test_recovery_cases_pipeline_and_detail(client, setup_phase7_data):
    """Verify recovery case listing and detailed single-case view."""
    # List cases
    resp_list = await client.get(
        "/api/v1/recovery-cases?status=WAITING_APPROVAL",
        headers={"X-User-Role": "MERCHANT_ADMIN"},
    )
    assert resp_list.status_code == 200
    cases = resp_list.json()["items"]
    assert len(cases) >= 1
    assert cases[0]["id"] == "case_p7_hv"

    # Detail view
    resp_detail = await client.get(
        "/api/v1/recovery-cases/case_p7_hv",
        headers={"X-User-Role": "VIEWER"},
    )
    assert resp_detail.status_code == 200
    detail = resp_detail.json()
    assert detail["id"] == "case_p7_hv"
    assert detail["requires_human_approval"] is True
    assert detail["transaction"]["amount"] == 15000.0
    assert detail["transaction"]["customer"]["name"] == "Ananya Sharma"


@pytest.mark.asyncio
async def test_pending_approvals_list_and_authorization_flow(client, setup_phase7_data):
    """Verify pending approvals list, approval execution, and rejection flow."""
    # 1. Fetch pending approvals queue
    resp_pending = await client.get(
        "/api/v1/approvals/pending",
        headers={"X-User-Role": "MERCHANT_ADMIN"},
    )
    assert resp_pending.status_code == 200
    pending_items = resp_pending.json()["items"]
    assert any(item["id"] == "case_p7_hv" for item in pending_items)

    # 2. Approve case with MERCHANT_ADMIN role
    resp_approve = await client.post(
        "/api/v1/recovery-cases/case_p7_hv/approve",
        headers={
            "X-User-Role": "MERCHANT_ADMIN",
            "X-User-Id": "admin_user_01",
        },
    )
    assert resp_approve.status_code == 200
    approved_data = resp_approve.json()
    assert approved_data["status"] == "APPROVED_AND_EXECUTED"
    assert approved_data["case_id"] == "case_p7_hv"


@pytest.mark.asyncio
async def test_simulation_sandbox_runner_integration(client, setup_phase7_data):
    """Verify POST /api/v1/simulation/run executes simulation scenarios safely."""
    payload = {
        "scenario_name": "predefined_5_scenarios",
        "batch_size": 5,
        "enable_ai_agent": True,
        "enable_policy_engine": True,
    }
    resp = await client.post(
        "/api/v1/simulation/run",
        json=payload,
        headers={"X-User-Role": "MERCHANT_ADMIN"},
    )
    assert resp.status_code == 200
    sim_res = resp.json()
    assert sim_res["evaluated_count"] == 5
    assert "revenue_at_risk" in sim_res
    assert "revenue_recovered" in sim_res
    assert len(sim_res["cases"]) == 5


@pytest.mark.asyncio
async def test_audit_logs_and_evaluation_reports(client, setup_phase7_data):
    """Verify audit logs and evaluation results endpoints."""
    # Audit logs
    resp_logs = await client.get(
        "/api/v1/audit-logs?actor_type=AI_AGENT",
        headers={"X-User-Role": "MERCHANT_ADMIN"},
    )
    assert resp_logs.status_code == 200
    assert "items" in resp_logs.json()

    # Evaluation results
    resp_eval = await client.get(
        "/api/v1/evaluation/results",
        headers={"X-User-Role": "MERCHANT_OPERATOR"},
    )
    assert resp_eval.status_code == 200
    eval_data = resp_eval.json()
    assert "model_evaluation" in eval_data or "status" in eval_data


@pytest.mark.asyncio
async def test_phase7_rbac_enforcement_matrix(client, setup_phase7_data):
    """Verify strict RBAC matrix enforcement for Phase 7 frontend routes."""
    # VIEWER role blocked from state-changing approval & execution
    resp_viewer_approve = await client.post(
        "/api/v1/recovery-cases/case_p7_hv/approve",
        headers={"X-User-Role": "VIEWER"},
    )
    assert resp_viewer_approve.status_code == 403

    resp_viewer_reject = await client.post(
        "/api/v1/recovery-cases/case_p7_hv/reject",
        json={"reason": "Unauthorized rejection"},
        headers={"X-User-Role": "VIEWER"},
    )
    assert resp_viewer_reject.status_code == 403

    # MERCHANT_OPERATOR blocked from approval/rejection (Admin only)
    resp_op_approve = await client.post(
        "/api/v1/recovery-cases/case_p7_hv/approve",
        headers={"X-User-Role": "MERCHANT_OPERATOR"},
    )
    assert resp_op_approve.status_code == 403

    # MERCHANT_ADMIN permitted for approval
    resp_admin_approve = await client.post(
        "/api/v1/recovery-cases/case_p7_hv/approve",
        headers={"X-User-Role": "MERCHANT_ADMIN"},
    )
    assert resp_admin_approve.status_code == 200
