from typing import Any, Dict

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from backend.app.core.database import Base


class MerchantPolicy(Base):
    """Deterministic policy knobs. The LLM cannot override these values."""

    __tablename__ = "merchant_policies"

    id = Column(String(64), primary_key=True, default=lambda: f"pol_{uuid.uuid4().hex[:12]}")
    merchant_id = Column(
        String(64),
        ForeignKey("merchants.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    max_retry_attempts = Column(Integer, nullable=False, default=2)
    high_value_threshold = Column(Numeric(14, 2), nullable=False, default=10000.00)
    min_recovery_score = Column(Numeric(14, 2), nullable=False, default=15.00)
    min_ai_confidence = Column(Numeric(5, 4), nullable=False, default=0.70)
    contact_cooldown_minutes = Column(Integer, nullable=False, default=60)
    max_contact_attempts = Column(Integer, nullable=False, default=2)
    policy_version = Column(String(50), nullable=False, default="v1.0.0")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    merchant = relationship("Merchant", back_populates="policy")

    @staticmethod
    def engine_defaults() -> Dict[str, Any]:
        return {
            "high_value_threshold": 10000.0,
            "max_retries": 2,
            "min_ai_confidence": 0.70,
            "min_recovery_score": 15.0,
            "cooldown_minutes": 60,
            "max_contact_attempts": 2,
            "policy_version": "v1.0.0",
        }

    def to_engine_dict(self) -> Dict[str, Any]:
        return {
            "high_value_threshold": float(self.high_value_threshold),
            "max_retries": int(self.max_retry_attempts),
            "min_ai_confidence": float(self.min_ai_confidence),
            "min_recovery_score": float(self.min_recovery_score),
            "cooldown_minutes": int(self.contact_cooldown_minutes),
            "max_contact_attempts": int(self.max_contact_attempts),
            "policy_version": self.policy_version,
        }
