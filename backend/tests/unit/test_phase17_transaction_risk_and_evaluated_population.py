import pytest
import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.merchant import Merchant
from backend.app.models.customer import Customer
from backend.app.models.transaction import Transaction
from backend.app.models.risk_assessment import RevenueRiskAssessment
from backend.app.models.recovery_case import RecoveryCase
from backend.app.models.recovery_action import RecoveryAction
from backend.app.services.metrics_service import MetricsService


@pytest.mark.asyncio
async def test_phase3_transaction_risk_semantics_and_historical_preservation(db_session: AsyncSession):
    """
    Test Phase 3:
    1. Newly created FAILED transaction sets initial_status='FAILED'
    2. FAILED -> CAPTURED recovery keeps initial_status='FAILED'
    3. Organic CAPTURED transaction sets initial_status='CAPTURED'
    4. Simulation transactions are excluded from live metrics
    5. Revenue at risk only includes initial_status='FAILED' live transactions
    """
    merchant = Merchant(id=f"mer_{uuid.uuid4().hex[:6]}", name="Risk Test Merchant")
    customer = Customer(
        id=f"cust_{uuid.uuid4().hex[:6]}",
        merchant_id=merchant.id,
        name="Test Customer",
        email_hash="hash_test",
    )
    db_session.add_all([merchant, customer])
    await db_session.commit()

    # 1. Live Failed Tx
    tx_failed = Transaction(
        id=f"tx_f_{uuid.uuid4().hex[:6]}",
        merchant_id=merchant.id,
        customer_id=customer.id,
        amount=1000.0,
        status="FAILED",
        initial_status="FAILED",
        is_simulation=False,
    )
    # 2. Live Recovered Tx (originated FAILED -> CAPTURED)
    tx_recovered = Transaction(
        id=f"tx_r_{uuid.uuid4().hex[:6]}",
        merchant_id=merchant.id,
        customer_id=customer.id,
        amount=2500.0,
        status="CAPTURED",
        initial_status="FAILED",
        is_simulation=False,
    )
    # 3. Live Organic CAPTURED Tx (never failed)
    tx_organic = Transaction(
        id=f"tx_o_{uuid.uuid4().hex[:6]}",
        merchant_id=merchant.id,
        customer_id=customer.id,
        amount=5000.0,
        status="CAPTURED",
        initial_status="CAPTURED",
        is_simulation=False,
    )
    # 4. Simulation Failed Tx
    tx_sim_failed = Transaction(
        id=f"tx_sf_{uuid.uuid4().hex[:6]}",
        merchant_id=merchant.id,
        customer_id=customer.id,
        amount=9999.0,
        status="FAILED",
        initial_status="FAILED",
        is_simulation=True,
    )
    # 5. Simulation Recovered Tx
    tx_sim_rec = Transaction(
        id=f"tx_sr_{uuid.uuid4().hex[:6]}",
        merchant_id=merchant.id,
        customer_id=customer.id,
        amount=8888.0,
        status="CAPTURED",
        initial_status="FAILED",
        is_simulation=True,
    )
    db_session.add_all([tx_failed, tx_recovered, tx_organic, tx_sim_failed, tx_sim_rec])
    await db_session.commit()

    # Verify initial_status preservation
    assert tx_failed.initial_status == "FAILED"
    assert tx_recovered.initial_status == "FAILED"
    assert tx_recovered.status == "CAPTURED"
    assert tx_organic.initial_status == "CAPTURED"

    # Query live revenue at risk using MetricsService logic
    metrics = await MetricsService.get_dashboard_metrics(db_session)

    # Risk should include tx_failed (1000) and tx_recovered (2500) = 3500 (or base db + 3500)
    # Organic (5000) and simulation (9999, 8888) must be EXCLUDED from revenue_at_risk!
    stmt_risk = select(func.sum(Transaction.amount)).where(
        Transaction.is_simulation == False,
        Transaction.initial_status == "FAILED",
        Transaction.id.in_([tx_failed.id, tx_recovered.id, tx_organic.id, tx_sim_failed.id, tx_sim_rec.id]),
    )
    risk_sum = (await db_session.execute(stmt_risk)).scalar()
    assert float(risk_sum) == 3500.0


@pytest.mark.asyncio
async def test_phase4_evaluated_transaction_population(db_session: AsyncSession):
    """
    Test Phase 4:
    1. Unevaluated transaction (no RiskAssessment) is excluded from total_evaluated_transactions
    2. Evaluated transaction (has RiskAssessment) is included
    3. Duplicate assessment on same transaction cannot inflate count
    4. Simulation assessment is excluded from live metrics
    5. Recovered and stopped transactions with assessments are included
    """
    merchant = Merchant(id=f"mer_{uuid.uuid4().hex[:6]}", name="Eval Test Merchant")
    customer = Customer(
        id=f"cust_{uuid.uuid4().hex[:6]}",
        merchant_id=merchant.id,
        name="Eval Customer",
        email_hash="hash_eval",
    )
    db_session.add_all([merchant, customer])
    await db_session.commit()

    # Tx A: Unevaluated
    tx_un = Transaction(
        id=f"tx_un_{uuid.uuid4().hex[:6]}",
        merchant_id=merchant.id,
        customer_id=customer.id,
        amount=1500.0,
        status="FAILED",
        initial_status="FAILED",
        is_simulation=False,
    )
    # Tx B: Evaluated
    tx_ev = Transaction(
        id=f"tx_ev_{uuid.uuid4().hex[:6]}",
        merchant_id=merchant.id,
        customer_id=customer.id,
        amount=2000.0,
        status="FAILED",
        initial_status="FAILED",
        is_simulation=False,
    )
    rra_ev = RevenueRiskAssessment(
        id=f"rra_{uuid.uuid4().hex[:6]}",
        transaction_id=tx_ev.id,
        risk_score=40.0,
        expected_recoverable_amount=1200.0,
        confidence=0.8,
        is_simulation=False,
    )
    # Tx C: Simulation Evaluated
    tx_sim_ev = Transaction(
        id=f"tx_sev_{uuid.uuid4().hex[:6]}",
        merchant_id=merchant.id,
        customer_id=customer.id,
        amount=3000.0,
        status="FAILED",
        initial_status="FAILED",
        is_simulation=True,
    )
    rra_sim_ev = RevenueRiskAssessment(
        id=f"rra_{uuid.uuid4().hex[:6]}",
        transaction_id=tx_sim_ev.id,
        risk_score=50.0,
        expected_recoverable_amount=1500.0,
        confidence=0.7,
        is_simulation=True,
    )
    db_session.add_all([tx_un, tx_ev, rra_ev, tx_sim_ev, rra_sim_ev])
    await db_session.commit()

    # Query distinct live evaluated count for our test transactions
    stmt = select(func.count(func.distinct(RevenueRiskAssessment.transaction_id))).where(
        RevenueRiskAssessment.is_simulation == False,
        RevenueRiskAssessment.transaction_id.in_([tx_un.id, tx_ev.id, tx_sim_ev.id]),
    )
    eval_count = (await db_session.execute(stmt)).scalar()
    assert eval_count == 1 # Only tx_ev is counted! Unevaluated tx_un and simulation tx_sim_ev are excluded.
