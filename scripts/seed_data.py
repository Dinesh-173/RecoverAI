import asyncio
import os
import random
import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.models.merchant import Merchant
from backend.app.models.merchant_policy import MerchantPolicy
from backend.app.models.customer import Customer
from backend.app.models.transaction import Transaction
from backend.app.models.recovery_case import RecoveryCase
from backend.app.models.risk_assessment import RevenueRiskAssessment
from backend.app.models.recovery_action import RecoveryAction
from backend.app.models.audit_log import AuditLog
from backend.app.core.security import hash_identifier, generate_correlation_id
from backend.app.services.risk_service import RiskAssessmentService
from backend.app.services.recovery_service import RecoveryService


async def seed_database(num_transactions: int = 150, seed: int = 42):
    """
    Seeds the database with deterministic sample merchant, customers,
    and transactions for immediate local exploration and live UI demonstration.
    """
    random.seed(seed)
    print(f"Initializing database schema...")
    await init_db()

    async with AsyncSessionLocal() as db:
        print("Checking for existing merchant...")
        stmt_m = select(Merchant).where(Merchant.id == "mer_apex_digital_01")
        res_m = await db.execute(stmt_m)
        merchant = res_m.scalar_one_or_none()
        if not merchant:
            merchant = Merchant(
                id="mer_apex_digital_01",
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

        print("Generating customer pool...")
        customer_names = [
            ("Vikram Aditya", "VIP", 32, 1, 145000.0, False),
            ("Ananya Sharma", "STANDARD", 8, 1, 12400.0, False),
            ("Rohan Verma", "STANDARD", 3, 2, 4500.0, False),
            ("Pooja Mehta", "HIGH_VALUE", 14, 0, 48000.0, True), # Opted out
            ("Sameer Joshi", "STANDARD", 4, 1, 6200.0, False),
            ("Kavita Nair", "VIP", 28, 0, 180000.0, False),
            ("Aditya Roy", "AT_RISK", 1, 4, 1500.0, False),
            ("Deepa Patel", "HIGH_VALUE", 11, 1, 35000.0, False),
            ("Tarun Reddy", "STANDARD", 5, 0, 7800.0, False),
            ("Sneha Rao", "STANDARD", 2, 1, 3100.0, False),
        ]

        customers = []
        for name, seg, succ, fail, ltv, opt_out in customer_names:
            c = Customer(
                merchant_id=merchant.id,
                name=name,
                email_hash=hash_identifier(f"{name.lower().replace(' ', '')}@example.com"),
                customer_segment=seg,
                successful_payment_count=succ,
                failed_payment_count=fail,
                total_lifetime_value=ltv,
                communication_opt_out=opt_out,
            )
            db.add(c)
            customers.append(c)
        await db.commit()
        for c in customers:
            await db.refresh(c)

        print(f"Generating {num_transactions} realistic transaction records...")
        methods = ["UPI", "CARD", "NETBANKING", "WALLET"]
        failure_scenarios = [
            ("GATEWAY_ERROR", "Bank server gateway timeout / downtime", 1),
            ("NETWORK_TIMEOUT", "NPCI / PSP connection timeout", 1),
            ("INSUFFICIENT_FUNDS", "Account balance insufficient", 1),
            ("USER_DROPPED", "Customer abandoned 3DS verification window", 1),
            ("EXPIRED_CARD", "Payment instrument expired", 1),
            ("GATEWAY_ERROR", "Bank server gateway timeout / downtime", 2),
            ("INSUFFICIENT_FUNDS", "Account balance insufficient", 3), # Exceeded retries
            ("FRAUD_SECURITY_BLOCK", "Issuer risk security block", 1),
        ]

        base_time = datetime.now(timezone.utc) - timedelta(days=14)
        created_txs = []

        for i in range(num_transactions):
            tx_time = base_time + timedelta(hours=(i * 2.2), minutes=random.randint(0, 50))
            cust = random.choice(customers)
            method = random.choice(methods)
            f_code, f_reason, attempt = random.choice(failure_scenarios)
            
            if cust.customer_segment == "VIP":
                amount = random.choice([12000.0, 18500.0, 24999.0, 45000.0])
            elif cust.customer_segment == "HIGH_VALUE":
                amount = random.choice([5999.0, 8999.0, 11500.0, 14999.0])
            else:
                amount = random.choice([499.0, 999.0, 1499.0, 2499.0, 3999.0, 4999.0])

            tx = Transaction(
                external_transaction_id=f"pay_seed_{uuid.uuid4().hex[:10]}",
                merchant_id=merchant.id,
                customer_id=cust.id,
                amount=amount,
                currency="INR",
                payment_method=method,
                status="FAILED",
                failure_code=f_code,
                failure_reason=f_reason,
                attempt_number=attempt,
                order_id=f"order_{uuid.uuid4().hex[:10]}",
                created_at=tx_time,
                updated_at=tx_time,
            )
            db.add(tx)
            created_txs.append(tx)

        await db.commit()
        for tx in created_txs:
            await db.refresh(tx)

        print("Running initial RecoverAI diagnostic analysis across seed batch...")
        # Process a subset of transactions through recovery engine to populate cases & audits
        for tx in created_txs[:40]:
            try:
                await RecoveryService.analyze_transaction(
                    db=db,
                    transaction_id=tx.id,
                    correlation_id=f"seed_corr_{tx.id[:8]}",
                    force_simulation=True,
                )
            except Exception as e:
                print(f"Error processing seed tx {tx.id}: {e}")

        # Execute some approved cases to create initial recovered revenue
        stmt_cases = select(RecoveryCase).where(RecoveryCase.status == "EXECUTING").limit(15)
        res_cases = await db.execute(stmt_cases)
        for c in res_cases.scalars().all():
            try:
                await RecoveryService.execute_action(
                    db=db,
                    case_id=c.id,
                    correlation_id=f"seed_exec_{c.id[:8]}",
                    force_simulation=True,
                )
            except Exception as e:
                pass

        print("Database seeding completed successfully.")


if __name__ == "__main__":
    asyncio.run(seed_database(num_transactions=150, seed=42))
