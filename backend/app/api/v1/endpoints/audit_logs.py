from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.app.core.database import get_db
from backend.app.models.audit_log import AuditLog
from backend.app.core.security import require_role

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("")
async def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    entity_type: Optional[str] = None,
    actor_type: Optional[str] = None,
    action: Optional[str] = None,
    correlation_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_role(["MERCHANT_ADMIN", "ADMIN", "MERCHANT_OPERATOR", "VIEWER"])),
):
    """Retrieve immutable audit logs with correlation IDs and policy results."""
    stmt = select(AuditLog).order_by(desc(AuditLog.timestamp))

    if entity_type:
        stmt = stmt.where(AuditLog.entity_type == entity_type)
    if actor_type:
        stmt = stmt.where(AuditLog.actor_type == actor_type)
    if action:
        stmt = stmt.where(AuditLog.action == action)
    if correlation_id:
        stmt = stmt.where(AuditLog.correlation_id == correlation_id)

    stmt = stmt.offset(skip).limit(limit)
    res = await db.execute(stmt)
    logs = res.scalars().all()

    items = []
    for l in logs:
        items.append({
            "id": l.id,
            "entity_type": l.entity_type,
            "entity_id": l.entity_id,
            "actor_type": l.actor_type,
            "actor_id": l.actor_id,
            "action": l.action,
            "reason": l.reason,
            "input_summary": l.input_summary,
            "output_summary": l.output_summary,
            "policy_result": l.policy_result,
            "timestamp": l.timestamp,
            "correlation_id": l.correlation_id,
        })
    return {"items": items, "count": len(items)}
