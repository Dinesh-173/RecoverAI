from sqlalchemy import Column, String, DateTime, Text, JSON
from datetime import datetime, timezone
import uuid

from backend.app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(64), primary_key=True, default=lambda: f"aud_{uuid.uuid4().hex[:12]}")
    entity_type = Column(String(50), nullable=False, index=True) # TRANSACTION, RECOVERY_CASE, RECOVERY_ACTION, WEBHOOK
    entity_id = Column(String(64), nullable=False, index=True)
    actor_type = Column(String(50), nullable=False, default="SYSTEM") # SYSTEM, AI_AGENT, MERCHANT, ADMIN
    actor_id = Column(String(100), nullable=False, default="system_worker")
    action = Column(String(100), nullable=False, index=True)
    reason = Column(Text, nullable=True)
    input_summary = Column(JSON, default=dict)
    output_summary = Column(JSON, default=dict)
    policy_result = Column(String(50), nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    correlation_id = Column(String(64), nullable=False, index=True)
