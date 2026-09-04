import time
import uuid
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from backend.app.core.database import get_db
from backend.app.models.merchant import Merchant
from backend.app.models.merchant_policy import MerchantPolicy
from backend.app.models.customer import Customer
from backend.app.models.transaction import Transaction
from backend.app.models.recovery_case import RecoveryCase
from backend.app.models.recovery_action import RecoveryAction
from backend.app.models.risk_assessment import RevenueRiskAssessment
from backend.app.services.recovery_service import RecoveryService
from backend.app.schemas.schemas import SimulationRunRequest, SimulationRunResponse, CustomTransactionInput
from backend.app.core.security import hash_identifier, require_role

router = APIRouter(prefix="/simulation", tags=["Simulation & Demo"])


@router.post("/run")
async def run_recovery_simulation(
    request: SimulationRunRequest = SimulationRunRequest(),
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_role(["MERCHANT_ADMIN", "ADMIN", "MERCHANT_OPERATOR"])),
):
    """
    Executes a batch recovery simulation using predefined scenarios, synthetic batches,
    or user-provided custom transaction records with historical date preservation.
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

    scenario_txs = []
    orig_tx_ids = {}

    # 1. Custom Transaction Data Source
    if request.source == "custom" or request.custom_transactions is not None:
        custom_list = request.custom_transactions or []

        # Inclusive Date Range Filtering (start_date <= tx_date <= end_date)
        if request.start_date or request.end_date:
            filtered_list = []
            for ctx in custom_list:
                tx_dt = ctx.transaction_date or datetime.now(timezone.utc)
                if tx_dt.tzinfo is None:
                    tx_dt = tx_dt.replace(tzinfo=timezone.utc)

                if request.start_date:
                    s_dt = request.start_date
                    if s_dt.tzinfo is None:
                        s_dt = s_dt.replace(tzinfo=timezone.utc)
                    if tx_dt < s_dt:
                        continue

                if request.end_date:
                    e_dt = request.end_date
                    if e_dt.tzinfo is None:
                        e_dt = e_dt.replace(tzinfo=timezone.utc)
                    if e_dt.hour == 0 and e_dt.minute == 0 and e_dt.second == 0:
                        e_dt = e_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
                    if tx_dt > e_dt:
                        continue

                filtered_list.append(ctx)
            custom_list = filtered_list

        orig_tx_ids = {}
        for ctx in custom_list:
            tx_dt = ctx.transaction_date or datetime.now(timezone.utc)
            if tx_dt.tzinfo is None:
                tx_dt = tx_dt.replace(tzinfo=timezone.utc)

            cust_id = f"cust_sim_{uuid.uuid4().hex[:6]}"
            cust_name = ctx.customer_name or f"Customer {ctx.transaction_id}"
            cust_email = ctx.customer_email or f"{ctx.transaction_id.lower()}@example.com"

            cust = Customer(
                id=cust_id,
                merchant_id=merchant.id,
                name=cust_name,
                email_hash=hash_identifier(cust_email),
                customer_segment=ctx.customer_segment or ("AT_RISK" if ctx.risk_flag else "STANDARD"),
                communication_opt_out=ctx.customer_opt_out,
            )
            db.add(cust)
            await db.flush()

            # Format failure reason with untrusted metadata tags for prompt injection defense
            reason_text = ctx.failure_reason or f"Failure code: {ctx.failure_code}"
            if ctx.risk_flag and ctx.failure_code != "FRAUD_SECURITY_BLOCK":
                reason_text += " [Risk flag set by merchant]"
            safe_reason = f"<untrusted_metadata>{reason_text}</untrusted_metadata>"

            tx_internal_id = f"tx_{ctx.transaction_id}_{uuid.uuid4().hex[:6]}"
            orig_tx_ids[tx_internal_id] = ctx.transaction_id

            tx = Transaction(
                id=tx_internal_id,
                external_transaction_id=f"pay_sim_{ctx.transaction_id}_{uuid.uuid4().hex[:6]}",
                merchant_id=merchant.id,
                customer_id=cust.id,
                customer=cust,
                amount=float(ctx.amount),
                currency=ctx.currency,
                payment_method=ctx.payment_method,
                status="FAILED",
                initial_status="FAILED",
                is_simulation=True,
                failure_code=ctx.failure_code,
                failure_reason=safe_reason,
                attempt_number=ctx.retry_attempt,
                created_at=tx_dt,
                updated_at=tx_dt,
            )
            db.add(tx)
            scenario_txs.append(tx)

        await db.commit()

    # 2. Predefined 5 Scenarios
    elif request.scenario_name == "predefined_5_scenarios":
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
            amount=45000.0,
            currency="INR",
            payment_method="NETBANKING",
            status="FAILED",
            initial_status="FAILED",
            is_simulation=True,
            failure_code="GATEWAY_ERROR",
            failure_reason="HDFC netbanking gateway timeout",
            attempt_number=1,
        )
        scenario_txs.append(t1)

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
            initial_status="FAILED",
            is_simulation=True,
            failure_code="NETWORK_TIMEOUT",
            failure_reason="UPI NPCI connection timeout",
            attempt_number=1,
        )
        scenario_txs.append(t2)

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
            initial_status="FAILED",
            is_simulation=True,
            failure_code="INSUFFICIENT_FUNDS",
            failure_reason="Card declined by issuer due to insufficient balance",
            attempt_number=3,
        )
        scenario_txs.append(t3)

        c4 = Customer(
            id=f"cust_opt_{uuid.uuid4().hex[:6]}",
            merchant_id=merchant.id,
            name="Pooja Mehta",
            email_hash=hash_identifier("pooja@outlook.com"),
            customer_segment="STANDARD",
            successful_payment_count=3,
            failed_payment_count=1,
            total_lifetime_value=6500.0,
            communication_opt_out=True,
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
            initial_status="FAILED",
            is_simulation=True,
            failure_code="USER_DROPPED",
            failure_reason="Payment authorization abandoned",
            attempt_number=1,
        )
        scenario_txs.append(t4)

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
            initial_status="FAILED",
            is_simulation=True,
            failure_code="FRAUD_SECURITY_BLOCK",
            failure_reason="Issuer risk block: High velocity fraud score",
            attempt_number=1,
        )
        scenario_txs.append(t5)

        for tx in scenario_txs:
            db.add(tx.customer)
            db.add(tx)
        await db.commit()

    # 3. Dynamic Synthetic Batch Ingestion
    else:
        stmt_failed = select(Transaction).where(Transaction.status == "FAILED", Transaction.is_simulation == False).limit(request.batch_size)
        res_failed = await db.execute(stmt_failed)
        scenario_txs = list(res_failed.scalars().all())

    # Execute simulation loop through RecoverAI pipeline
    evaluated_count = len(scenario_txs)
    revenue_at_risk = 0.0
    revenue_recovered = 0.0
    recovered_count = 0
    escalated_count = 0
    stopped_count = 0
    cases_summary = []

    for tx in scenario_txs:
        revenue_at_risk += float(tx.amount)
        corr_id = f"{batch_id}_{tx.id[:8]}"

        # Analyze transaction (ML -> AI -> Policy Engine)
        case = await RecoveryService.analyze_transaction(
            db=db,
            transaction_id=tx.id,
            correlation_id=corr_id,
            force_simulation=True,
        )

        # Check policy enforcement outcome
        if case.status == "WAITING_APPROVAL":
            escalated_count += 1
            action_status = "ESCALATED_TO_HUMAN"
        elif case.status == "STOPPED":
            stopped_count += 1
            action_status = "STOPPED_BY_POLICY"
        else:
            action_record = await RecoveryService.execute_action(
                db=db,
                case_id=case.id,
                correlation_id=corr_id,
                force_simulation=True,
            )
            action_status = action_record.status
            if action_status == "SUCCESS":
                revenue_recovered += float(tx.amount)
                recovered_count += 1

        tx_date_str = tx.created_at.isoformat() if tx.created_at else None

        cases_summary.append({
            "case_id": case.id,
            "transaction_id": orig_tx_ids.get(tx.id, tx.external_transaction_id or tx.id),
            "internal_transaction_id": tx.id,
            "transaction_date": tx_date_str,
            "created_at": tx_date_str,
            "amount": float(tx.amount),
            "currency": tx.currency,
            "payment_method": tx.payment_method,
            "failure_code": tx.failure_code,
            "retry_attempt": tx.attempt_number,
            "customer_opt_out": tx.customer.communication_opt_out if tx.customer else False,
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


@router.post("/custom")
async def run_custom_simulation(
    request: SimulationRunRequest,
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_role(["MERCHANT_ADMIN", "ADMIN", "MERCHANT_OPERATOR"])),
):
    """
    Alias endpoint for running custom transaction data simulation.
    """
    request.source = "custom"
    return await run_recovery_simulation(request=request, db=db, _role=_role)


@router.post("/reset")
async def reset_simulation_data(
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_role(["MERCHANT_ADMIN", "ADMIN", "MERCHANT_OPERATOR"])),
):
    """
    Safely purges simulation records (is_simulation=True) from database.
    Strictly isolated: Live production transactions and metrics are never touched.
    """
    stmt_txs = select(Transaction.id).where(Transaction.is_simulation == True)
    res_txs = await db.execute(stmt_txs)
    sim_tx_ids = list(res_txs.scalars().all())

    deleted_cases_count = 0
    deleted_txs_count = 0

    if sim_tx_ids:
        await db.execute(delete(RecoveryAction).where(RecoveryAction.transaction_id.in_(sim_tx_ids)))
        await db.execute(delete(RevenueRiskAssessment).where(RevenueRiskAssessment.transaction_id.in_(sim_tx_ids)))

        stmt_del_cases = delete(RecoveryCase).where(RecoveryCase.transaction_id.in_(sim_tx_ids))
        res_cases = await db.execute(stmt_del_cases)
        deleted_cases_count = res_cases.rowcount or 0

        stmt_del_txs = delete(Transaction).where(Transaction.id.in_(sim_tx_ids))
        res_del_txs = await db.execute(stmt_del_txs)
        deleted_txs_count = res_del_txs.rowcount or 0

        await db.commit()

    return {
        "status": "SUCCESS",
        "message": "Simulation data safely reset.",
        "purged_simulation_transactions": deleted_txs_count,
        "purged_simulation_cases": deleted_cases_count,
        "live_data_protected": True,
    }
