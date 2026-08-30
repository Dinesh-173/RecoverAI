import time
import uuid
import random
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.core.database import get_db
from backend.app.models.merchant import Merchant
from backend.app.models.merchant_policy import MerchantPolicy
from backend.app.models.customer import Customer
from backend.app.models.transaction import Transaction
from backend.app.models.recovery_case import RecoveryCase
from backend.app.services.recovery_service import RecoveryService
from backend.app.schemas.schemas import SimulationRunRequest, SimulationRunResponse
from backend.app.core.security import hash_identifier

router = APIRouter(prefix="/simulation", tags=["Simulation & Demo"])


@router.post("/run")
async def run_recovery_simulation(
    request: SimulationRunRequest = SimulationRunRequest(),
    db: AsyncSession = Depends(get_db),
):
    """
    Executes a batch recovery simulation or predefined scenarios.
    1. Selects / seeds batch transactions
    2. Runs ML risk scoring
    3. Runs AI diagnostic agent
    4. Applies deterministic policy guardrails
    5. Executes simulation payment adapter
    6. Returns measurable revenue delta & audit trail
    """
    start_time = time.time()
    batch_id = f"sim_batch_{uuid.uuid4().hex[:8]}"

    # Ensure demo merchant exists
    stmt = select(Merchant).limit(1)
    res = await db.execute(stmt)
    merchant = res.scalar_one_or_none()
    if not merchant:
        merchant = Merchant(
            id="mer_demo_razorpay",
            name="Apex Digital Retail",
            business_category="ECOMMERCE",
            currency="INR",
            policy=MerchantPolicy(
                max_retry_attempts=2,
                high_value_threshold=10000.0,
                min_recovery_score=15.0,
                min_ai_confidence=0.70,
                contact_cooldown_minutes=60,
                max_contact_attempts=2,
            ),
        )
        db.add(merchant)
        await db.commit()
        await db.refresh(merchant)

    # Predefined Scenarios if requested
    scenario_txs = []
    if request.scenario_name == "predefined_5_scenarios":
        # Scenario 1: High-Value + Temporary Gateway Error + High LTV
        c1 = Customer(
            id=f"cust_vip_{uuid.uuid4().hex[:6]}",
            merchant_id=merchant.id,
            name="Vikram Aditya (Enterprise)",
            email_hash=hash_identifier("vikram@enterprise.corp"),
            customer_segment="VIP",
            successful_payment_count=24,
            failed_payment_count=1,
            total_lifetime_value=125000.0,
            communication_opt_out=False,
        )
        t1 = Transaction(
            id=f"tx_s1_{uuid.uuid4().hex[:6]}",
            external_transaction_id=f"pay_s1_{uuid.uuid4().hex[:8]}",
            merchant_id=merchant.id,
            customer=c1,
            amount=45000.0, # Exceeds high-value threshold
            currency="INR",
            payment_method="NETBANKING",
            status="FAILED",
            failure_code="GATEWAY_ERROR",
            failure_reason="HDFC netbanking gateway timeout",
            attempt_number=1,
        )
        scenario_txs.append(t1)

        # Scenario 2: Low-Value + Temporary Failure + Regular Customer
        c2 = Customer(
            id=f"cust_std_{uuid.uuid4().hex[:6]}",
            merchant_id=merchant.id,
            name="Ananya Sharma",
            email_hash=hash_identifier("ananya@gmail.com"),
            customer_segment="STANDARD",
            successful_payment_count=6,
            failed_payment_count=0,
            total_lifetime_value=4200.0,
            communication_opt_out=False,
        )
        t2 = Transaction(
            id=f"tx_s2_{uuid.uuid4().hex[:6]}",
            external_transaction_id=f"pay_s2_{uuid.uuid4().hex[:8]}",
            merchant_id=merchant.id,
            customer=c2,
            amount=1499.0,
            currency="INR",
            payment_method="UPI",
            status="FAILED",
            failure_code="NETWORK_TIMEOUT",
            failure_reason="UPI NPCI connection timeout",
            attempt_number=1,
        )
        scenario_txs.append(t2)

        # Scenario 3: Repeated Failure Exceeded (Attempt 3)
        c3 = Customer(
            id=f"cust_rep_{uuid.uuid4().hex[:6]}",
            merchant_id=merchant.id,
            name="Rohan Verma",
            email_hash=hash_identifier("rohan@yahoo.com"),
            customer_segment="STANDARD",
            successful_payment_count=1,
            failed_payment_count=3,
            total_lifetime_value=999.0,
            communication_opt_out=False,
        )
        t3 = Transaction(
            id=f"tx_s3_{uuid.uuid4().hex[:6]}",
            external_transaction_id=f"pay_s3_{uuid.uuid4().hex[:8]}",
            merchant_id=merchant.id,
            customer=c3,
            amount=2999.0,
            currency="INR",
            payment_method="CARD",
            status="FAILED",
            failure_code="INSUFFICIENT_FUNDS",
            failure_reason="Card declined by issuer due to insufficient balance",
            attempt_number=3, # Exceeds max retries
        )
        scenario_txs.append(t3)

        # Scenario 4: Customer Opted Out of Communications
        c4 = Customer(
            id=f"cust_opt_{uuid.uuid4().hex[:6]}",
            merchant_id=merchant.id,
            name="Pooja Mehta",
            email_hash=hash_identifier("pooja@outlook.com"),
            customer_segment="STANDARD",
            successful_payment_count=3,
            failed_payment_count=1,
            total_lifetime_value=6500.0,
            communication_opt_out=True, # Active opt out
        )
        t4 = Transaction(
            id=f"tx_s4_{uuid.uuid4().hex[:6]}",
            external_transaction_id=f"pay_s4_{uuid.uuid4().hex[:8]}",
            merchant_id=merchant.id,
            customer=c4,
            amount=3499.0,
            currency="INR",
            payment_method="UPI",
            status="FAILED",
            failure_code="USER_DROPPED",
            failure_reason="Payment authorization abandoned",
            attempt_number=1,
        )
        scenario_txs.append(t4)

        # Scenario 5: Security / Fraud Block
        c5 = Customer(
            id=f"cust_frd_{uuid.uuid4().hex[:6]}",
            merchant_id=merchant.id,
            name="Suspicious Account",
            email_hash=hash_identifier("anon_999@temp.mail"),
            customer_segment="AT_RISK",
            successful_payment_count=0,
            failed_payment_count=5,
            total_lifetime_value=0.0,
            communication_opt_out=False,
        )
        t5 = Transaction(
            id=f"tx_s5_{uuid.uuid4().hex[:6]}",
            external_transaction_id=f"pay_s5_{uuid.uuid4().hex[:8]}",
            merchant_id=merchant.id,
            customer=c5,
            amount=18500.0,
            currency="INR",
            payment_method="CARD",
            status="FAILED",
            failure_code="FRAUD_SECURITY_BLOCK",
            failure_reason="Issuer risk block: High velocity fraud score",
            attempt_number=1,
        )
        scenario_txs.append(t5)

        for tx in scenario_txs:
            db.add(tx.customer)
            db.add(tx)
        await db.commit()

    else:
        # Load up to batch_size unprocessed failed transactions
        stmt_failed = select(Transaction).where(Transaction.status == "FAILED").limit(request.batch_size)
        res_failed = await db.execute(stmt_failed)
        scenario_txs = list(res_failed.scalars().all())

    # Process all selected transactions through RecoverAI pipeline
    evaluated_count = len(scenario_txs)
    revenue_at_risk = 0.0
    revenue_recovered = 0.0
    recovered_count = 0
    escalated_count = 0
    stopped_count = 0
    cases_summary = []

    for tx in scenario_txs:
        revenue_at_risk += tx.amount
        corr_id = f"{batch_id}_{tx.id[:8]}"

        # Analyze
        case = await RecoveryService.analyze_transaction(
            db=db,
            transaction_id=tx.id,
            correlation_id=corr_id,
            force_simulation=True,
        )

        # Check outcome
        if case.status == "WAITING_APPROVAL":
            escalated_count += 1
            action_status = "ESCALATED_TO_HUMAN"
        elif case.status == "STOPPED":
            stopped_count += 1
            action_status = "STOPPED_BY_POLICY"
        else:
            # Auto-executable approved action in simulation
            action_record = await RecoveryService.execute_action(
                db=db,
                case_id=case.id,
                correlation_id=corr_id,
                force_simulation=True,
            )
            revenue_recovered += tx.amount
            recovered_count += 1
            action_status = action_record.status

        cases_summary.append({
            "case_id": case.id,
            "transaction_id": tx.id,
            "amount": tx.amount,
            "failure_code": tx.failure_code,
            "diagnosis": case.diagnosis,
            "recommended_action": case.recommended_action,
            "confidence": case.confidence,
            "recovery_score": case.recovery_score,
            "case_status": case.status,
            "action_status": action_status,
        })

    # Baseline comparison (32.78% rate)
    baseline_recovered = revenue_at_risk * 0.3278
    val_add = ((revenue_recovered - baseline_recovered) / baseline_recovered * 100.0) if baseline_recovered > 0 else 0.0
    duration_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "batch_id": batch_id,
        "evaluated_count": evaluated_count,
        "recovered_count": recovered_count,
        "escalated_count": escalated_count,
        "stopped_count": stopped_count,
        "revenue_at_risk": round(revenue_at_risk, 2),
        "revenue_recovered": round(revenue_recovered, 2),
        "recovery_rate": round((revenue_recovered / revenue_at_risk * 100.0) if revenue_at_risk > 0 else 0.0, 2),
        "baseline_recovered_revenue": round(baseline_recovered, 2),
        "value_add_percentage": round(val_add, 2),
        "execution_duration_ms": duration_ms,
        "cases": cases_summary,
    }
