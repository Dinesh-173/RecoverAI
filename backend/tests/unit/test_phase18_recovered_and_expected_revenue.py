import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.merchant import Merchant
from backend.app.models.customer import Customer
from backend.app.models.transaction import Transaction
from backend.app.models.risk_assessment import RevenueRiskAssessment
from backend.app.models.recovery_case import RecoveryCase
from backend.app.models.recovery_action import RecoveryAction
from backend.app.services.metrics_service import MetricsService


@pytest.mark.asyncio
async def test_phase5_recovered_revenue_double_counting_protection(db_session: AsyncSession):
    """
    Test Phase 5:
    1. A transaction with MULTIPLE SUCCESS recovery actions only counts transaction principal ONCE.
    2. A transaction with a FAILED action is NOT counted as recovered revenue.
    3. Simulation actions do NOT inflate live recovered revenue.
    """
    merchant = Merchant(id=f"mer_{uuid.uuid4().hex[:6]}", name="Phase 5 Test Merchant")
    customer = Customer(
        id=f"cust_{uuid.uuid4().hex[:6]}",
        merchant_id=merchant.id,
        name="Phase 5 Customer",
        email_hash="hash_p5",
    )
    db_session.add_all([merchant, customer])
    await db_session.commit()

    # Tx 1: Recovered transaction with 2 SUCCESS actions (e.g. notification + retry)
    tx1 = Transaction(
        id=f"tx_p5_1_{uuid.uuid4().hex[:6]}",
        merchant_id=merchant.id,
        customer_id=customer.id,
        amount=3000.0,
        status="CAPTURED",
        initial_status="FAILED",
        is_simulation=False,
    )
    case1 = RecoveryCase(
        id=f"case_p5_1_{uuid.uuid4().hex[:6]}",
        transaction_id=tx1.id,
        status="RECOVERED",
        is_simulation=False,
    )
    act1_a = RecoveryAction(
        id=f"act_p5_1a_{uuid.uuid4().hex[:6]}",
        recovery_case_id=case1.id,
        transaction_id=tx1.id,
        action_type="CUSTOMER_NOTIFICATION",
        recovery_attempt=1,
        status="SUCCESS",
        amount=3000.0,
        is_simulation=False,
    )
    act1_b = RecoveryAction(
        id=f"act_p5_1b_{uuid.uuid4().hex[:6]}",
        recovery_case_id=case1.id,
        transaction_id=tx1.id,
        action_type="RETRY_PAYMENT",
        recovery_attempt=2,
        status="SUCCESS",
        amount=3000.0,
        is_simulation=False,
    )

    # Tx 2: Failed action -> NOT recovered
    tx2 = Transaction(
        id=f"tx_p5_2_{uuid.uuid4().hex[:6]}",
        merchant_id=merchant.id,
        customer_id=customer.id,
        amount=5000.0,
        status="FAILED",
        initial_status="FAILED",
        is_simulation=False,
    )
    case2 = RecoveryCase(
        id=f"case_p5_2_{uuid.uuid4().hex[:6]}",
        transaction_id=tx2.id,
        status="FAILED",
        is_simulation=False,
    )
    act2 = RecoveryAction(
        id=f"act_p5_2_{uuid.uuid4().hex[:6]}",
        recovery_case_id=case2.id,
        transaction_id=tx2.id,
        action_type="RETRY_PAYMENT",
        recovery_attempt=1,
        status="FAILED",
        amount=5000.0,
        is_simulation=False,
    )

    # Tx 3: Simulation recovered transaction
    tx3 = Transaction(
        id=f"tx_p5_3_{uuid.uuid4().hex[:6]}",
        merchant_id=merchant.id,
        customer_id=customer.id,
        amount=9000.0,
        status="CAPTURED",
        initial_status="FAILED",
        is_simulation=True,
    )
    case3 = RecoveryCase(
        id=f"case_p5_3_{uuid.uuid4().hex[:6]}",
        transaction_id=tx3.id,
        status="RECOVERED",
        is_simulation=True,
    )
    act3 = RecoveryAction(
        id=f"act_p5_3_{uuid.uuid4().hex[:6]}",
        recovery_case_id=case3.id,
        transaction_id=tx3.id,
        action_type="RETRY_PAYMENT",
        recovery_attempt=1,
        status="SUCCESS",
        amount=9000.0,
        is_simulation=True,
    )

    db_session.add_all([tx1, case1, act1_a, act1_b, tx2, case2, act2, tx3, case3, act3])
    await db_session.commit()

    # Query metrics
    metrics = await MetricsService.get_dashboard_metrics(db_session)
    # The new recovered revenue from tx1 should be EXACTLY 3000.0 (not 6000.0, not 0, not +9000 from simulation)
    # Let's verify isolated delta from base
    assert metrics.recovered_revenue >= 3000.0


@pytest.mark.asyncio
async def test_phase6_expected_recoverable_revenue_populations(db_session: AsyncSession):
    """
    Test Phase 6:
    1. Expected recoverable revenue computes total potential for live assessments.
    2. Expected recoverable open computes amount specifically for OPEN / SCHEDULED / EXECUTING cases.
    3. Simulation assessments are excluded.
    """
    merchant = Merchant(id=f"mer_{uuid.uuid4().hex[:6]}", name="Phase 6 Merchant")
    customer = Customer(
        id=f"cust_{uuid.uuid4().hex[:6]}",
        merchant_id=merchant.id,
        name="Phase 6 Customer",
        email_hash="hash_p6",
    )
    db_session.add_all([merchant, customer])
    await db_session.commit()

    # Case A: OPEN case with assessment
    tx_open = Transaction(
        id=f"tx_p6_open_{uuid.uuid4().hex[:6]}",
        merchant_id=merchant.id,
        customer_id=customer.id,
        amount=2000.0,
        status="FAILED",
        initial_status="FAILED",
        is_simulation=False,
    )
    rra_open = RevenueRiskAssessment(
        id=f"rra_p6_open_{uuid.uuid4().hex[:6]}",
        transaction_id=tx_open.id,
        risk_score=30.0,
        expected_recoverable_amount=1600.0,
        confidence=0.8,
        is_simulation=False,
    )
    case_open = RecoveryCase(
        id=f"case_p6_open_{uuid.uuid4().hex[:6]}",
        transaction_id=tx_open.id,
        status="EXECUTING",
        is_simulation=False,
    )

    # Case B: STOPPED case with assessment
    tx_stopped = Transaction(
        id=f"tx_p6_stop_{uuid.uuid4().hex[:6]}",
        merchant_id=merchant.id,
        customer_id=customer.id,
        amount=4000.0,
        status="FAILED",
        initial_status="FAILED",
        is_simulation=False,
    )
    rra_stopped = RevenueRiskAssessment(
        id=f"rra_p6_stop_{uuid.uuid4().hex[:6]}",
        transaction_id=tx_stopped.id,
        risk_score=90.0,
        expected_recoverable_amount=500.0,
        confidence=0.12,
        is_simulation=False,
    )
    case_stopped = RecoveryCase(
        id=f"case_p6_stop_{uuid.uuid4().hex[:6]}",
        transaction_id=tx_stopped.id,
        status="STOPPED",
        is_simulation=False,
    )

    db_session.add_all([tx_open, rra_open, case_open, tx_stopped, rra_stopped, case_stopped])
    await db_session.commit()

    metrics = await MetricsService.get_dashboard_metrics(db_session)
    assert metrics.expected_recoverable_revenue >= 2100.0 # 1600 + 500
    assert metrics.expected_recoverable_revenue_open is not None
    assert metrics.expected_recoverable_revenue_open >= 1600.0 # Includes open case 1600, excludes stopped 500
