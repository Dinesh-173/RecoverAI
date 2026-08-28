from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload

from backend.app.models.transaction import Transaction
from backend.app.models.customer import Customer
from backend.app.models.risk_assessment import RevenueRiskAssessment
from backend.app.models.recovery_case import RecoveryCase
from backend.app.schemas.schemas import TransactionCreate, TransactionResponse
from backend.app.core.exceptions import ResourceNotFoundException


class TransactionService:
    @staticmethod
    async def create_transaction(db: AsyncSession, data: TransactionCreate) -> Transaction:
        tx = Transaction(
            id=data.id,
            external_transaction_id=data.external_transaction_id,
            merchant_id=data.merchant_id,
            customer_id=data.customer_id,
            amount=data.amount,
            currency=data.currency,
            payment_method=data.payment_method,
            status=data.status,
            failure_reason=data.failure_reason,
            failure_code=data.failure_code,
            attempt_number=data.attempt_number,
            order_id=data.order_id,
            subscription_id=data.subscription_id,
            metadata_json=data.metadata_json,
        )
        db.add(tx)
        await db.commit()
        await db.refresh(tx)
        return tx

    @staticmethod
    async def get_transactions(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        payment_method: Optional[str] = None,
        failure_code: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        stmt = (
            select(Transaction)
            .options(
                selectinload(Transaction.customer),
                selectinload(Transaction.risk_assessment),
                selectinload(Transaction.recovery_case),
            )
            .order_by(desc(Transaction.created_at))
        )

        if status:
            stmt = stmt.where(Transaction.status == status)
        if payment_method:
            stmt = stmt.where(Transaction.payment_method == payment_method)
        if failure_code:
            stmt = stmt.where(Transaction.failure_code == failure_code)
        if min_amount is not None:
            stmt = stmt.where(Transaction.amount >= min_amount)
        if max_amount is not None:
            stmt = stmt.where(Transaction.amount <= max_amount)

        # Count total
        count_stmt = select(func.count(Transaction.id))
        count_res = await db.execute(count_stmt)
        total = count_res.scalar() or 0

        # Execute paginated
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        transactions = result.scalars().all()

        results = []
        for tx in transactions:
            results.append({
                "id": tx.id,
                "external_transaction_id": tx.external_transaction_id,
                "merchant_id": tx.merchant_id,
                "customer_id": tx.customer_id,
                "customer_name": tx.customer.name if tx.customer else "Unknown",
                "customer_segment": tx.customer.customer_segment if tx.customer else "STANDARD",
                "amount": tx.amount,
                "currency": tx.currency,
                "payment_method": tx.payment_method,
                "status": tx.status,
                "failure_reason": tx.failure_reason,
                "failure_code": tx.failure_code,
                "attempt_number": tx.attempt_number,
                "order_id": tx.order_id,
                "subscription_id": tx.subscription_id,
                "risk_score": tx.risk_assessment.risk_score if tx.risk_assessment else None,
                "recovery_probability": tx.risk_assessment.confidence if tx.risk_assessment else None,
                "case_status": tx.recovery_case.status if tx.recovery_case else "UNPROCESSED",
                "recommended_action": tx.recovery_case.recommended_action if tx.recovery_case else None,
                "created_at": tx.created_at,
                "updated_at": tx.updated_at,
            })
        return results, total

    @staticmethod
    async def get_transaction_by_id(db: AsyncSession, transaction_id: str) -> Dict[str, Any]:
        stmt = (
            select(Transaction)
            .options(
                selectinload(Transaction.customer),
                selectinload(Transaction.merchant),
                selectinload(Transaction.risk_assessment),
                selectinload(Transaction.recovery_case).selectinload(RecoveryCase.actions),
            )
            .where(Transaction.id == transaction_id)
        )
        result = await db.execute(stmt)
        tx = result.scalar_one_or_none()
        if not tx:
            raise ResourceNotFoundException("Transaction", transaction_id)

        return {
            "id": tx.id,
            "external_transaction_id": tx.external_transaction_id,
            "merchant_id": tx.merchant_id,
            "merchant_name": tx.merchant.name if tx.merchant else "Merchant",
            "customer_id": tx.customer_id,
            "customer": {
                "id": tx.customer.id,
                "name": tx.customer.name,
                "customer_segment": tx.customer.customer_segment,
                "successful_payment_count": tx.customer.successful_payment_count,
                "failed_payment_count": tx.customer.failed_payment_count,
                "total_lifetime_value": tx.customer.total_lifetime_value,
                "communication_opt_out": tx.customer.communication_opt_out,
            } if tx.customer else None,
            "amount": tx.amount,
            "currency": tx.currency,
            "payment_method": tx.payment_method,
            "status": tx.status,
            "failure_reason": tx.failure_reason,
            "failure_code": tx.failure_code,
            "attempt_number": tx.attempt_number,
            "order_id": tx.order_id,
            "subscription_id": tx.subscription_id,
            "metadata_json": tx.metadata_json or {},
            "risk_assessment": {
                "risk_score": tx.risk_assessment.risk_score,
                "expected_recoverable_amount": tx.risk_assessment.expected_recoverable_amount,
                "confidence": tx.risk_assessment.confidence,
                "model_version": tx.risk_assessment.model_version,
            } if tx.risk_assessment else None,
            "recovery_case": {
                "id": tx.recovery_case.id,
                "status": tx.recovery_case.status,
                "risk_level": tx.recovery_case.risk_level,
                "diagnosis": tx.recovery_case.diagnosis,
                "recommended_action": tx.recovery_case.recommended_action,
                "recommended_delay_minutes": tx.recovery_case.recommended_delay_minutes,
                "confidence": tx.recovery_case.confidence,
                "recovery_score": tx.recovery_case.recovery_score,
                "requires_human_approval": tx.recovery_case.requires_human_approval,
                "approval_reason": tx.recovery_case.approval_reason,
                "actions": [
                    {
                        "id": act.id,
                        "action_type": act.action_type,
                        "status": act.status,
                        "amount": act.amount,
                        "policy_decision": act.policy_decision,
                        "executed_at": act.executed_at,
                        "result_json": act.result_json,
                    }
                    for act in (tx.recovery_case.actions or [])
                ],
            } if tx.recovery_case else None,
            "created_at": tx.created_at,
            "updated_at": tx.updated_at,
        }
