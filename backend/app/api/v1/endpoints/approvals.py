from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Header, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from backend.app.core.database import get_db
from backend.app.models.recovery_case import RecoveryCase
from backend.app.models.transaction import Transaction
from backend.app.services.recovery_service import RecoveryService
from backend.app.core.security import generate_correlation_id, require_role

router = APIRouter(prefix="", tags=["Human Approvals"])


@router.get("/approvals/pending")
async def get_pending_approvals(db: AsyncSession = Depends(get_db)):
    """Fetch all cases requiring manual human merchant signoff."""
    stmt = (
        select(RecoveryCase)
        .options(
            selectinload(RecoveryCase.transaction).selectinload(Transaction.customer),
            selectinload(RecoveryCase.transaction).selectinload(Transaction.risk_assessment),
        )
        .where(
            RecoveryCase.requires_human_approval == True,
            RecoveryCase.status == "WAITING_APPROVAL",
        )
        .order_by(desc(RecoveryCase.created_at))
    )
    res = await db.execute(stmt)
    cases = res.scalars().all()

    items = []
    for c in cases:
        tx = c.transaction
        cust = tx.customer if tx else None
        risk = tx.risk_assessment if tx else None
        items.append({
            "id": c.id,
            "transaction_id": c.transaction_id,
            "amount": tx.amount if tx else 0.0,
            "currency": tx.currency if tx else "INR",
            "payment_method": tx.payment_method if tx else "UPI",
            "customer_name": cust.name if cust else "Unknown",
            "customer_segment": cust.customer_segment if cust else "STANDARD",
            "failure_code": tx.failure_code if tx else "GATEWAY_ERROR",
            "failure_reason": tx.failure_reason if tx else "Payment failed",
            "diagnosis": c.diagnosis,
            "recommended_action": c.recommended_action,
            "confidence": c.confidence,
            "recovery_score": c.recovery_score,
            "approval_reason": c.approval_reason or "Amount exceeds high-value threshold or requires review",
            "created_at": c.created_at,
        })
    return {"items": items, "count": len(items)}


@router.post("/recovery-cases/{case_id}/approve")
async def approve_recovery_case(
    case_id: str,
    x_user_role: str = Header(None),
    x_user_id: str = Header("ops_lead_1"),
    x_correlation_id: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_role(["MERCHANT_ADMIN", "ADMIN"])),
):
    """Approve a pending high-value or escalated recovery action."""
    effective_role = x_user_role or _role
    corr_id = x_correlation_id or generate_correlation_id()
    action_record = await RecoveryService.approve_case(
        db=db,
        case_id=case_id,
        user_role=effective_role,
        user_id=x_user_id,
        correlation_id=corr_id,
    )
    return {
        "status": "APPROVED_AND_EXECUTED",
        "case_id": case_id,
        "action_id": action_record.id,
        "action_type": action_record.action_type,
        "execution_status": action_record.status,
    }


@router.post("/recovery-cases/{case_id}/reject")
async def reject_recovery_case(
    case_id: str,
    reason: str = Body("Rejected by merchant operator", embed=True),
    x_user_role: str = Header(None),
    x_user_id: str = Header("ops_lead_1"),
    x_correlation_id: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_role(["MERCHANT_ADMIN", "ADMIN"])),
):
    """Reject and safely terminate a pending recovery case."""
    effective_role = x_user_role or _role
    corr_id = x_correlation_id or generate_correlation_id()
    stopped_case = await RecoveryService.reject_case(
        db=db,
        case_id=case_id,
        reason=reason,
        user_role=effective_role,
        user_id=x_user_id,
        correlation_id=corr_id,
    )
    return {
        "status": "REJECTED_AND_STOPPED",
        "case_id": stopped_case.id,
        "case_status": stopped_case.status,
    }
