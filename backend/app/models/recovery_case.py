from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Integer, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from backend.app.core.database import Base


class RecoveryCase(Base):
    __tablename__ = "recovery_cases"

    id = Column(String(64), primary_key=True, default=lambda: f"case_{uuid.uuid4().hex[:12]}")
    transaction_id = Column(String(64), ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    status = Column(String(50), nullable=False, default="OPEN", index=True)
    # Statuses: OPEN, ANALYZING, WAITING_APPROVAL, SCHEDULED, EXECUTING, RECOVERED, FAILED, STOPPED, ESCALATED
    risk_level = Column(String(20), nullable=False, default="MEDIUM") # LOW, MEDIUM, HIGH, CRITICAL
    diagnosis = Column(Text, nullable=True)
    recommended_action = Column(String(100), nullable=True) # RETRY_PAYMENT, DELAYED_RETRY, CUSTOMER_NOTIFICATION, HUMAN_REVIEW, STOP_RECOVERY
    recommended_delay_minutes = Column(Integer, nullable=False, default=0)
    confidence = Column(Float, nullable=False, default=0.0)
    recovery_score = Column(Float, nullable=False, default=0.0)
    requires_human_approval = Column(Boolean, nullable=False, default=False, index=True)
    approval_reason = Column(String(255), nullable=True)
    assigned_to = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    transaction = relationship("Transaction", back_populates="recovery_case")
    actions = relationship("RecoveryAction", back_populates="recovery_case", cascade="all, delete-orphan")
