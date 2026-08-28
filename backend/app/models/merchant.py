from sqlalchemy import Column, String, DateTime, Numeric, Integer, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from backend.app.core.database import Base


class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(String(64), primary_key=True, default=lambda: f"mer_{uuid.uuid4().hex[:12]}")
    name = Column(String(255), nullable=False)
    business_category = Column(String(100), nullable=False, default="ECOMMERCE")
    currency = Column(String(3), nullable=False, default="INR")
    
    # Configurable merchant policy settings
    high_value_threshold = Column(Float, nullable=False, default=10000.0)
    max_retries = Column(Integer, nullable=False, default=2)
    min_ai_confidence = Column(Float, nullable=False, default=0.70)
    min_recovery_score = Column(Float, nullable=False, default=15.0)
    cooldown_minutes = Column(Integer, nullable=False, default=60)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    customers = relationship("Customer", back_populates="merchant", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="merchant")
