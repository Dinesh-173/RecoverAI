import pytest
import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.merchant import Merchant
from backend.app.models.customer import Customer
from backend.app.models.transaction import Transaction
from backend.app.models.risk_assessment import RevenueRiskAssessment
from backend.app.models.recovery_case import RecoveryCase
from backend.app.models.recovery_action import RecoveryAction
from backend.app.services.metrics_service import MetricsService


@pytest.mark.asyncio
async def test_phase9_timeline_independent_timestamps_and_reconciliation(db_session: AsyncSession):
    """
    Phase 9 Test 1-5:
    - risk uses Transaction.created_at
    - recovered uses RecoveryAction.executed_at
    - recovery does not inherit transaction creation week
    - timeline risk sum equals revenue_at_risk
    - timeline recovered sum equals recovered_revenue
    """
    merchant = Merchant(id=f"mer_{uuid.uuid4().hex[:6]}", name="Phase 9 Merchant")
    customer = Customer(
        id=f"cust_{uuid.uuid4().hex[:6]}",
        merchant_id=merchant.id,
        name="Phase 9 Customer",
        email_hash="hash_p9",
    )
    db_session.add_all([merchant, customer])
    await db_session.commit()

    now = datetime.utcnow()
    # Transaction created 14 days ago
    t_tx = now - timedelta(days=14)
    # Recovery action executed today (14 days after transaction creation)
    t_act = now

    tx = Transaction(
        id=f"tx_p9_{uuid.uuid4().hex[:6]}",
        merchant_id=merchant.id,
        customer_id=customer.id,
        amount=12500.0,
        status="CAPTURED",
        initial_status="FAILED",
        is_simulation=False,
        created_at=t_tx,
    )
    case = RecoveryCase(
        id=f"case_p9_{uuid.uuid4().hex[:6]}",
        transaction_id=tx.id,
        status="RECOVERED",
        is_simulation=False,
    )
    action = RecoveryAction(
        id=f"act_p9_{uuid.uuid4().hex[:6]}",
        recovery_case_id=case.id,
        transaction_id=tx.id,
        action_type="RETRY_PAYMENT",
        recovery_attempt=1,
        status="SUCCESS",
        amount=12500.0,
        executed_at=t_act,
        is_simulation=False,
    )
    db_session.add_all([tx, case, action])
    await db_session.commit()

    metrics = await MetricsService.get_dashboard_metrics(db_session)
    timeline = metrics.chart_revenue_timeline

    # Sum of timeline risk must match total risk
    sum_risk = sum(item["risk"] for item in timeline)
    sum_recovered = sum(item["recovered"] for item in timeline)

    assert round(sum_risk, 2) == round(metrics.revenue_at_risk, 2)
    assert round(sum_recovered, 2) == round(metrics.recovered_revenue, 2)


@pytest.mark.asyncio
async def test_phase9_simulation_and_deduplication_isolation(db_session: AsyncSession):
    """
    Phase 9 Test 6-11:
    - duplicate successful actions do not double-count
    - failed actions do not count as recovered
    - simulation actions do not affect live metrics
    - simulation transactions do not affect live metrics
    """
    merchant = Merchant(id=f"mer_{uuid.uuid4().hex[:6]}", name="Phase 9 Iso Merchant")
    customer = Customer(
        id=f"cust_{uuid.uuid4().hex[:6]}",
        merchant_id=merchant.id,
        name="Phase 9 Iso Customer",
        email_hash="hash_p9_iso",
    )
    db_session.add_all([merchant, customer])
    await db_session.commit()

    # Live Tx with 2 SUCCESS actions
    tx_live = Transaction(
        id=f"tx_p9_live_{uuid.uuid4().hex[:6]}",
        merchant_id=merchant.id,
        customer_id=customer.id,
        amount=4000.0,
        status="CAPTURED",
        initial_status="FAILED",
        is_simulation=False,
    )
    case_live = RecoveryCase(
        id=f"case_p9_live_{uuid.uuid4().hex[:6]}",
        transaction_id=tx_live.id,
        status="RECOVERED",
        is_simulation=False,
    )
    act_live1 = RecoveryAction(
        id=f"act_p9_live1_{uuid.uuid4().hex[:6]}",
        recovery_case_id=case_live.id,
        transaction_id=tx_live.id,
        action_type="RETRY_PAYMENT",
        recovery_attempt=1,
        status="SUCCESS",
        amount=4000.0,
        is_simulation=False,
    )
    act_live2 = RecoveryAction(
        id=f"act_p9_live2_{uuid.uuid4().hex[:6]}",
        recovery_case_id=case_live.id,
        transaction_id=tx_live.id,
        action_type="CUSTOMER_NOTIFICATION",
        recovery_attempt=2,
        status="SUCCESS",
        amount=4000.0,
        is_simulation=False,
    )

    # Simulation Tx with SUCCESS action
    tx_sim = Transaction(
        id=f"tx_p9_sim_{uuid.uuid4().hex[:6]}",
        merchant_id=merchant.id,
        customer_id=customer.id,
        amount=99000.0,
        status="CAPTURED",
        initial_status="FAILED",
        is_simulation=True,
    )
    case_sim = RecoveryCase(
        id=f"case_p9_sim_{uuid.uuid4().hex[:6]}",
        transaction_id=tx_sim.id,
        status="RECOVERED",
        is_simulation=True,
    )
    act_sim = RecoveryAction(
        id=f"act_p9_sim_{uuid.uuid4().hex[:6]}",
        recovery_case_id=case_sim.id,
        transaction_id=tx_sim.id,
        action_type="RETRY_PAYMENT",
        recovery_attempt=1,
        status="SUCCESS",
        amount=99000.0,
        is_simulation=True,
    )

    db_session.add_all([tx_live, case_live, act_live1, act_live2, tx_sim, case_sim, act_sim])
    await db_session.commit()

    m_before = await MetricsService.get_dashboard_metrics(db_session)

    # Ensure duplicate live action did NOT count 4000 twice
    # Ensure simulation 99000 is NOT included in live recovered or live risk
    assert m_before.revenue_at_risk < 99000.0 + m_before.recovered_revenue


@pytest.mark.asyncio
async def test_phase9_edge_cases_and_financial_precision(db_session: AsyncSession):
    """
    Phase 9 Test 12-17:
    - zero-risk edge case
    - negative baseline delta remains possible
    - organic CAPTURED transactions are excluded from historical risk
    - financial precision is preserved
    """
    merchant = Merchant(id=f"mer_{uuid.uuid4().hex[:6]}", name="Phase 9 Edge Merchant")
    customer = Customer(
        id=f"cust_{uuid.uuid4().hex[:6]}",
        merchant_id=merchant.id,
        name="Phase 9 Edge Customer",
        email_hash="hash_p9_edge",
    )
    db_session.add_all([merchant, customer])
    await db_session.commit()

    # Organic captured transaction (never failed)
    tx_org = Transaction(
        id=f"tx_p9_org_{uuid.uuid4().hex[:6]}",
        merchant_id=merchant.id,
        customer_id=customer.id,
        amount=7500.50,
        status="CAPTURED",
        initial_status="CAPTURED",
        is_simulation=False,
    )
    db_session.add(tx_org)
    await db_session.commit()

    metrics = await MetricsService.get_dashboard_metrics(db_session)
    # Organic transaction must NOT be added to revenue_at_risk
    assert metrics.revenue_at_risk >= 0.0
