from sqlalchemy import Column, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from backend.app.core.database import Base


class RevenueRiskAssessment(Base):
    __tablename__ = "revenue_risk_assessments"

    id = Column(String(64), primary_key=True, default=lambda: f"rra_{uuid.uuid4().hex[:12]}")
    transaction_id = Column(String(64), ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    risk_score = Column(Float, nullable=False) # 0.0 to 100.0 (Higher means greater revenue loss risk)
    expected_recoverable_amount = Column(Float, nullable=False) # Amount * recovery_probability
    confidence = Column(Float, nullable=False) # Model confidence 0.0 to 1.0
    model_version = Column(String(50), nullable=False, default="v1.0.0-xgb")
    features_version = Column(String(50), nullable=False, default="v1.0.0")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    transaction = relationship("Transaction", back_populates="risk_assessment")
