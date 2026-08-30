import pytest
from httpx import AsyncClient
from backend.app.models.merchant import Merchant
from backend.app.models.merchant_policy import MerchantPolicy
from backend.app.models.customer import Customer
from backend.app.models.transaction import Transaction
from backend.app.models.recovery_case import RecoveryCase
from backend.app.core.security import hash_identifier


@pytest.mark.asyncio
async def test_health_check_live_db_ping(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "HEALTHY"
    assert data["service"] == "RecoverAI Agent Engine"
    assert "dependencies" in data
    assert data["dependencies"]["database"] == "HEALTHY"


@pytest.mark.asyncio
async def test_standardized_error_format_resource_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/recovery-cases/case_non_existent_9999")
    assert resp.status_code == 404
    data = resp.json()
    assert "error" in data
    assert data["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert "request_id" in data["error"]
    assert "was not found" in data["error"]["message"]


@pytest.mark.asyncio
async def test_standardized_error_format_validation_error(client: AsyncClient):
    resp = await client.get("/api/v1/transactions?limit=-5")
    assert resp.status_code == 422
    data = resp.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "request_id" in data["error"]
    assert "details" in data["error"]


@pytest.mark.asyncio
async def test_correlation_id_middleware_propagation(client: AsyncClient):
    custom_corr_id = "corr_custom_test_999"
    resp = await client.get(
        "/api/v1/recovery-cases/case_non_existent_888",
        headers={"x-correlation-id": custom_corr_id}
    )
    assert resp.headers.get("x-correlation-id") == custom_corr_id
    data = resp.json()
    assert data["error"]["request_id"] == custom_corr_id


@pytest.mark.asyncio
async def test_rbac_viewer_blocked_from_modifications(client: AsyncClient, db_session):
    # Setup test case
    merchant = Merchant(
        id="mer_rbac_01",
        name="RBAC Merchant",
        policy=MerchantPolicy(high_value_threshold=5000.0),
    )
    customer = Customer(
        id="cust_rbac_01",
        merchant_id="mer_rbac_01",
        name="RBAC User",
        email_hash=hash_identifier("rbac@user.com"),
    )
    tx = Transaction(
        id="tx_rbac_01",
        merchant_id="mer_rbac_01",
        customer=customer,
        amount=15000.0,
        status="FAILED",
    )
    case = RecoveryCase(
        id="case_rbac_01",
        transaction_id="tx_rbac_01",
        status="WAITING_APPROVAL",
        requires_human_approval=True,
        recommended_action="RETRY_PAYMENT",
    )
    db_session.add(merchant)
    db_session.add(customer)
    db_session.add(tx)
    db_session.add(case)
    await db_session.commit()

    headers = {"X-User-Role": "VIEWER"}

    # VIEWER blocked from approve
    resp_app = await client.post("/api/v1/recovery-cases/case_rbac_01/approve", headers=headers)
    assert resp_app.status_code == 403
    assert resp_app.json()["error"]["code"] == "UNAUTHORIZED_APPROVAL"

    # VIEWER blocked from reject
    resp_rej = await client.post("/api/v1/recovery-cases/case_rbac_01/reject", headers=headers)
    assert resp_rej.status_code == 403
    assert resp_rej.json()["error"]["code"] == "UNAUTHORIZED_APPROVAL"

    # VIEWER blocked from analyze
    resp_anz = await client.post("/api/v1/recovery-cases/case_rbac_01/analyze", headers=headers)
    assert resp_anz.status_code == 403
    assert resp_anz.json()["error"]["code"] == "FORBIDDEN_OPERATION"

    # VIEWER blocked from execute
    resp_exc = await client.post("/api/v1/recovery-cases/case_rbac_01/execute", headers=headers)
    assert resp_exc.status_code == 403
    assert resp_exc.json()["error"]["code"] == "FORBIDDEN_OPERATION"

    # VIEWER blocked from simulation
    resp_sim = await client.post("/api/v1/simulation/run", headers=headers)
    assert resp_sim.status_code == 403
    assert resp_sim.json()["error"]["code"] == "FORBIDDEN_OPERATION"


@pytest.mark.asyncio
async def test_rbac_operator_blocked_from_approval(client: AsyncClient, db_session):
    headers = {"X-User-Role": "MERCHANT_OPERATOR"}

    # OPERATOR blocked from approve
    resp_app = await client.post("/api/v1/recovery-cases/case_rbac_01/approve", headers=headers)
    assert resp_app.status_code == 403
    assert resp_app.json()["error"]["code"] == "UNAUTHORIZED_APPROVAL"

    # OPERATOR blocked from reject
    resp_rej = await client.post("/api/v1/recovery-cases/case_rbac_01/reject", headers=headers)
    assert resp_rej.status_code == 403
    assert resp_rej.json()["error"]["code"] == "UNAUTHORIZED_APPROVAL"


@pytest.mark.asyncio
async def test_rbac_admin_and_operator_permitted_operations(client: AsyncClient, db_session):
    # OPERATOR permitted to run simulation
    op_headers = {"X-User-Role": "MERCHANT_OPERATOR"}
    resp_sim = await client.post(
        "/api/v1/simulation/run",
        json={"scenario_name": "predefined_5_scenarios", "batch_size": 5},
        headers=op_headers,
    )
    assert resp_sim.status_code == 200

    # Setup test case for approval
    merchant = Merchant(
        id="mer_rbac_02",
        name="RBAC Admin Merchant",
        policy=MerchantPolicy(high_value_threshold=5000.0),
    )
    customer = Customer(
        id="cust_rbac_02",
        merchant_id="mer_rbac_02",
        name="RBAC Admin User",
        email_hash=hash_identifier("rbac_admin@user.com"),
    )
    tx = Transaction(
        id="tx_rbac_02",
        merchant_id="mer_rbac_02",
        customer=customer,
        amount=15000.0,
        status="FAILED",
    )
    case = RecoveryCase(
        id="case_rbac_02",
        transaction_id="tx_rbac_02",
        status="WAITING_APPROVAL",
        requires_human_approval=True,
        recommended_action="RETRY_PAYMENT",
    )
    db_session.add(merchant)
    db_session.add(customer)
    db_session.add(tx)
    db_session.add(case)
    await db_session.commit()

    # ADMIN permitted to approve
    admin_headers = {"X-User-Role": "MERCHANT_ADMIN"}
    resp_app = await client.post("/api/v1/recovery-cases/case_rbac_02/approve", headers=admin_headers)
    assert resp_app.status_code == 200
    assert resp_app.json()["status"] == "APPROVED_AND_EXECUTED"


@pytest.mark.asyncio
async def test_rbac_viewer_allowed_read_only(client: AsyncClient):
    headers = {"X-User-Role": "VIEWER"}

    resp_tx = await client.get("/api/v1/transactions", headers=headers)
    assert resp_tx.status_code == 200

    resp_cs = await client.get("/api/v1/recovery-cases", headers=headers)
    assert resp_cs.status_code == 200

    resp_db = await client.get("/api/v1/dashboard/metrics", headers=headers)
    assert resp_db.status_code == 200

    resp_al = await client.get("/api/v1/audit-logs", headers=headers)
    assert resp_al.status_code == 200


@pytest.mark.asyncio
async def test_rbac_invalid_and_malformed_roles(client: AsyncClient):
    # 1. Lowercase valid role is normalized & accepted
    resp_low = await client.get("/api/v1/transactions", headers={"X-User-Role": "viewer"})
    assert resp_low.status_code == 200

    # 2. Invalid role is rejected with 403
    resp_inv = await client.get("/api/v1/transactions", headers={"X-User-Role": "INVALID_HACKER_ROLE"})
    assert resp_inv.status_code == 403
    assert "error" in resp_inv.json()
    assert resp_inv.json()["error"]["code"] == "FORBIDDEN_OPERATION"


from unittest.mock import patch

@pytest.mark.asyncio
async def test_health_check_db_failure_returns_unhealthy(client: AsyncClient):
    with patch("sqlalchemy.ext.asyncio.AsyncSession.execute", side_effect=Exception("Database connection lost")):
        resp = await client.get("/health")
        assert resp.status_code == 503
        data = resp.json()
        assert data["status"] == "UNHEALTHY"
        assert data["dependencies"]["database"] == "UNHEALTHY"
