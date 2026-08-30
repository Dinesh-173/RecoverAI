from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.models.transaction import Transaction
from backend.app.models.customer import Customer
from backend.app.models.merchant import Merchant
from backend.app.models.merchant_policy import MerchantPolicy
from backend.app.models.risk_assessment import RevenueRiskAssessment


class AgentToolLayer:
    """
    Controlled read-only tool layer providing clean abstractions for the AI agent.
    Prevents direct arbitrary DB execution.
    """
    @staticmethod
    async def get_transaction(db: AsyncSession, transaction_id: str) -> Optional[Dict[str, Any]]:
        stmt = select(Transaction).where(Transaction.id == transaction_id)
        result = await db.execute(stmt)
        tx = result.scalar_one_or_none()
        if not tx:
            return None
        return {
            "id": tx.id,
            "external_transaction_id": tx.external_transaction_id,
            "merchant_id": tx.merchant_id,
            "customer_id": tx.customer_id,
            "amount": tx.amount,
            "currency": tx.currency,
            "payment_method": tx.payment_method,
            "status": tx.status,
            "failure_reason": tx.failure_reason,
            "failure_code": tx.failure_code,
            "attempt_number": tx.attempt_number,
            "metadata_json": tx.metadata_json or {},
        }

    @staticmethod
    async def get_customer_history(db: AsyncSession, customer_id: str) -> Optional[Dict[str, Any]]:
        stmt = select(Customer).where(Customer.id == customer_id)
        result = await db.execute(stmt)
        cust = result.scalar_one_or_none()
        if not cust:
            return None
        return {
            "id": cust.id,
            "name": cust.name,
            "customer_segment": cust.customer_segment,
            "successful_payment_count": cust.successful_payment_count,
            "failed_payment_count": cust.failed_payment_count,
            "total_lifetime_value": cust.total_lifetime_value,
            "communication_opt_out": cust.communication_opt_out,
        }

    @staticmethod
    async def get_merchant_policy(db: AsyncSession, merchant_id: str) -> Dict[str, Any]:
        stmt = select(MerchantPolicy).where(MerchantPolicy.merchant_id == merchant_id)
        result = await db.execute(stmt)
        policy = result.scalar_one_or_none()
        if not policy:
            return MerchantPolicy.engine_defaults()
        return policy.to_engine_dict()

    @staticmethod
    def calculate_recovery_score(
        probability_of_recovery: float,
        expected_recoverable_amount: float,
        action_success_probability: float = 0.90
    ) -> float:
        """
        Deterministic calculation:
        recovery_score = probability_of_recovery * expected_recoverable_amount * action_success_probability / 100
        Normalized to a clean scalar score.
        """
        raw = probability_of_recovery * (expected_recoverable_amount / 100.0) * action_success_probability
        return round(float(raw), 2)
