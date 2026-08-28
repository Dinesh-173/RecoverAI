from sqlalchemy import Column, String, DateTime, Numeric, Integer, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from backend.app.core.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String(64), primary_key=True, default=lambda: f"cust_{uuid.uuid4().hex[:12]}")
    merchant_id = Column(String(64), ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    email_hash = Column(String(64), nullable=False, index=True)
    customer_segment = Column(String(50), nullable=False, default="STANDARD")  # VIP, HIGH_VALUE, STANDARD, AT_RISK
    successful_payment_count = Column(Integer, nullable=False, default=0)
    failed_payment_count = Column(Integer, nullable=False, default=0)
    total_lifetime_value = Column(Float, nullable=False, default=0.0)
    last_payment_at = Column(DateTime(timezone=True), nullable=True)
    communication_opt_out = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    merchant = relationship("Merchant", back_populates="customers")
    transactions = relationship("Transaction", back_populates="customer")
