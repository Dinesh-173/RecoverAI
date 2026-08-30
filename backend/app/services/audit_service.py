from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.audit_log import AuditLog
from backend.app.core.security import generate_correlation_id
from backend.app.core.logging import logger


from decimal import Decimal

def _to_json_safe(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: _to_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_json_safe(v) for v in obj]
    return obj


class AuditService:
    @staticmethod
    async def log_event(
        db: AsyncSession,
        entity_type: str,
        entity_id: str,
        actor_type: str,
        actor_id: str,
        action: str,
        reason: Optional[str] = None,
        input_summary: Optional[Dict[str, Any]] = None,
        output_summary: Optional[Dict[str, Any]] = None,
        policy_result: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> AuditLog:
        """
        Record an immutable audit log entry.
        Never stores passwords, auth tokens, or raw payment secrets.
        """
        corr_id = correlation_id or generate_correlation_id()
        
        # Sanitize summaries
        clean_input = _to_json_safe(input_summary or {})
        clean_output = _to_json_safe(output_summary or {})

        audit_entry = AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            actor_type=actor_type,
            actor_id=actor_id,
            action=action,
            reason=reason,
            input_summary=clean_input,
            output_summary=clean_output,
            policy_result=policy_result,
            correlation_id=corr_id,
        )
        db.add(audit_entry)
        await db.commit()
        await db.refresh(audit_entry)

        logger.info(
            f"AUDIT [{entity_type}:{entity_id}] action={action} actor={actor_type}:{actor_id} policy={policy_result}",
            extra={"correlation_id": corr_id, "service": "AuditService"}
        )
        return audit_entry
