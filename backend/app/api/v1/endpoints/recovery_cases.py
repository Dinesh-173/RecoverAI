from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from backend.app.core.database import get_db
from backend.app.models.recovery_case import RecoveryCase
from backend.app.models.transaction import Transaction
from backend.app.services.recovery_service import RecoveryService
from backend.app.core.security import generate_correlation_id, require_role
from backend.app.core.exceptions import ResourceNotFoundException

router = APIRouter(prefix="/recovery-cases", tags=["Recovery Cases"])


@router.get("")
async def list_recovery_cases(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = None,
    risk_level: Optional[str] = None,
    requires_approval: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_role(["MERCHANT_ADMIN", "ADMIN", "MERCHANT_OPERATOR", "VIEWER"])),
):
    """List recovery cases with filtering by status and risk level."""
    stmt = (
        select(RecoveryCase)
        .options(
            selectinload(RecoveryCase.transaction).selectinload(Transaction.customer),
            selectinload(RecoveryCase.actions),
        )
        .order_by(desc(RecoveryCase.created_at))
    )

    if status:
        stmt = stmt.where(RecoveryCase.status == status)
    if risk_level:
        stmt = stmt.where(RecoveryCase.risk_level == risk_level)
    if requires_approval is not None:
        stmt = stmt.where(RecoveryCase.requires_human_approval == requires_approval)

    stmt = stmt.offset(skip).limit(limit)
    res = await db.execute(stmt)
    cases = res.scalars().all()

    items = []
    for c in cases:
        items.append({
            "id": c.id,
            "transaction_id": c.transaction_id,
            "transaction_amount": c.transaction.amount if c.transaction else 0.0,
            "payment_method": c.transaction.payment_method if c.transaction else "UPI",
            "customer_name": c.transaction.customer.name if (c.transaction and c.transaction.customer) else "Unknown",
            "status": c.status,
            "risk_level": c.risk_level,
            "diagnosis": c.diagnosis,
            "recommended_action": c.recommended_action,
            "recommended_delay_minutes": c.recommended_delay_minutes,
            "confidence": c.confidence,
            "recovery_score": c.recovery_score,
            "requires_human_approval": c.requires_human_approval,
            "approval_reason": c.approval_reason,
            "actions_count": len(c.actions or []),
            "created_at": c.created_at,
            "updated_at": c.updated_at,
        })
    return {"items": items, "count": len(items)}


@router.get("/{case_id}")
async def get_recovery_case(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_role(["MERCHANT_ADMIN", "ADMIN", "MERCHANT_OPERATOR", "VIEWER"])),
):
    """Fetch complete recovery case diagnostics, timeline, and execution history."""
    stmt = (
        select(RecoveryCase)
        .options(
            selectinload(RecoveryCase.transaction).selectinload(Transaction.customer),
            selectinload(RecoveryCase.transaction).selectinload(Transaction.merchant),
            selectinload(RecoveryCase.transaction).selectinload(Transaction.risk_assessment),
            selectinload(RecoveryCase.actions),
        )
        .where(RecoveryCase.id == case_id)
    )
    res = await db.execute(stmt)
    c = res.scalar_one_or_none()
    if not c:
        raise ResourceNotFoundException("RecoveryCase", case_id)

    tx = c.transaction
    return {
        "id": c.id,
        "status": c.status,
        "risk_level": c.risk_level,
        "diagnosis": c.diagnosis,
        "recommended_action": c.recommended_action,
        "recommended_delay_minutes": c.recommended_delay_minutes,
        "confidence": c.confidence,
        "recovery_score": c.recovery_score,
        "requires_human_approval": c.requires_human_approval,
        "approval_reason": c.approval_reason,
        "assigned_to": c.assigned_to,
        "created_at": c.created_at,
        "updated_at": c.updated_at,
        "transaction": {
            "id": tx.id,
            "external_transaction_id": tx.external_transaction_id,
            "amount": tx.amount,
            "currency": tx.currency,
            "payment_method": tx.payment_method,
            "status": tx.status,
            "failure_code": tx.failure_code,
            "failure_reason": tx.failure_reason,
            "attempt_number": tx.attempt_number,
            "customer": {
                "id": tx.customer.id,
                "name": tx.customer.name,
                "customer_segment": tx.customer.customer_segment,
                "total_lifetime_value": tx.customer.total_lifetime_value,
                "successful_payment_count": tx.customer.successful_payment_count,
                "failed_payment_count": tx.customer.failed_payment_count,
                "communication_opt_out": tx.customer.communication_opt_out,
            } if tx.customer else None,
        } if tx else None,
        "actions": [
            {
                "id": act.id,
                "action_type": act.action_type,
                "status": act.status,
                "amount": act.amount,
                "reason": act.reason,
                "policy_decision": act.policy_decision,
                "executed_at": act.executed_at,
                "result": act.result_json,
                "error_code": act.error_code,
            }
            for act in (c.actions or [])
        ],
    }


@router.post("/{case_id}/analyze")
async def analyze_case(
    case_id: str,
    x_correlation_id: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_role(["MERCHANT_ADMIN", "ADMIN", "MERCHANT_OPERATOR"])),
):
    """Trigger ML scoring & AI diagnostic analysis for a case."""
    stmt = select(RecoveryCase).where(RecoveryCase.id == case_id)
    res = await db.execute(stmt)
    c = res.scalar_one_or_none()
    if not c:
        raise ResourceNotFoundException("RecoveryCase", case_id)

    corr_id = x_correlation_id or generate_correlation_id()
    updated_case = await RecoveryService.analyze_transaction(
        db=db,
        transaction_id=c.transaction_id,
        correlation_id=corr_id,
    )
    return {
        "status": "SUCCESS",
        "case_id": updated_case.id,
        "case_status": updated_case.status,
        "recommended_action": updated_case.recommended_action,
        "confidence": updated_case.confidence,
        "recovery_score": updated_case.recovery_score,
        "requires_human_approval": updated_case.requires_human_approval,
    }


@router.post("/{case_id}/execute")
async def execute_case_action(
    case_id: str,
    x_correlation_id: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_role(["MERCHANT_ADMIN", "ADMIN", "MERCHANT_OPERATOR"])),
):
    """Execute the policy-approved recovery action for this case."""
    corr_id = x_correlation_id or generate_correlation_id()
    action_record = await RecoveryService.execute_action(
        db=db,
        case_id=case_id,
        correlation_id=corr_id,
    )
    return {
        "status": "SUCCESS",
        "action_id": action_record.id,
        "action_type": action_record.action_type,
        "execution_status": action_record.status,
        "result": action_record.result_json,
    }
