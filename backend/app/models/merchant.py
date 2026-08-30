from sqlalchemy import Column, DateTime, String
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
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    customers = relationship(
        "Customer",
        back_populates="merchant",
        cascade="all, delete-orphan",
    )
    transactions = relationship(
        "Transaction",
        back_populates="merchant",
        cascade="all, delete-orphan",
    )
    policy = relationship(
        "MerchantPolicy",
        back_populates="merchant",
        uselist=False,
        cascade="all, delete-orphan",
    )
    users = relationship(
        "User",
        back_populates="merchant",
        cascade="all, delete-orphan",
    )
