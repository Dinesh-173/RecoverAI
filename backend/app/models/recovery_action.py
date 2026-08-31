from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from backend.app.core.database import Base


class RecoveryAction(Base):
    __tablename__ = "recovery_actions"

    id = Column(
        String(64),
        primary_key=True,
        default=lambda: f"act_{uuid.uuid4().hex[:12]}",
    )

    recovery_case_id = Column(
        String(64),
        ForeignKey("recovery_cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    transaction_id = Column(
        String(64),
        ForeignKey("transactions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    action_type = Column(
        String(100),
        nullable=False,
    )

    recovery_attempt = Column(
        Integer,
        nullable=False,
        default=1,
    )

    status = Column(
        String(50),
        nullable=False,
        default="PENDING",
        index=True,
    )

    amount = Column(Numeric(14, 2), nullable=False)

    reason = Column(Text, nullable=True)

    policy_decision = Column(
        String(50),
        nullable=False,
        default="APPROVED",
    )

    policy_version = Column(
        String(50),
        nullable=False,
        default="v1.0.0",
    )

    executed_at = Column(DateTime(timezone=True), nullable=True)

    result_json = Column(
        "result",
        JSON,
        default=dict,
    )

    error_code = Column(String(100), nullable=True)

    is_simulation = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        UniqueConstraint(
            "transaction_id",
            "action_type",
            "recovery_attempt",
            name="uq_recovery_action_idempotency",
        ),
    )

    # Relationships
    recovery_case = relationship(
        "RecoveryCase",
        back_populates="actions",
    )

    transaction = relationship(
        "Transaction",
        back_populates="recovery_actions",
    )
