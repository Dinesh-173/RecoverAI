from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from backend.app.core.database import Base


class RecoveryAction(Base):
    __tablename__ = "recovery_actions"

    id = Column(String(64), primary_key=True, default=lambda: f"act_{uuid.uuid4().hex[:12]}")
    recovery_case_id = Column(String(64), ForeignKey("recovery_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    action_type = Column(String(100), nullable=False) # RETRY_PAYMENT, CUSTOMER_NOTIFICATION, PAYMENT_LINK, HUMAN_REVIEW
    status = Column(String(50), nullable=False, default="PENDING", index=True) # PENDING, EXECUTING, SUCCESS, FAILED, BLOCKED
    amount = Column(Float, nullable=False)
    reason = Column(Text, nullable=True)
    policy_decision = Column(String(50), nullable=False, default="APPROVED") # APPROVED, BLOCKED, ESCALATED
    policy_version = Column(String(50), nullable=False, default="v1.0.0")
    executed_at = Column(DateTime(timezone=True), nullable=True)
    result_json = Column("result", JSON, default=dict)
    error_code = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    recovery_case = relationship("RecoveryCase", back_populates="actions")
