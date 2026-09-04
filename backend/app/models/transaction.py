from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Numeric, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from backend.app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(
        String(64),
        primary_key=True,
        default=lambda: f"tx_{uuid.uuid4().hex[:12]}",
    )

    external_transaction_id = Column(
        String(100),
        unique=True,
        nullable=True,
        index=True,
    )  # e.g. pay_xxxxx

    merchant_id = Column(
        String(64),
        ForeignKey("merchants.id"),
        nullable=False,
        index=True,
    )

    customer_id = Column(
        String(64),
        ForeignKey("customers.id"),
        nullable=False,
        index=True,
    )

    amount = Column(Numeric(14, 2), nullable=False)

    currency = Column(
        String(3),
        nullable=False,
        default="INR",
    )

    payment_method = Column(
        String(50),
        nullable=False,
        default="UPI",
    )  # UPI, CARD, NETBANKING, WALLET

    status = Column(
        String(50),
        nullable=False,
        index=True,
    )  # AUTHORIZED, CAPTURED, FAILED, REFUNDED

    initial_status = Column(
        String(50),
        nullable=True,
        index=True,
    )  # Historical status at creation (e.g., FAILED before recovery to CAPTURED)

    is_simulation = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )

    def __init__(self, **kwargs):
        if "initial_status" not in kwargs and "status" in kwargs:
            kwargs["initial_status"] = kwargs["status"]
        super().__init__(**kwargs)

    failure_reason = Column(
        String(255),
        nullable=True,
    )

    failure_code = Column(
        String(100),
        nullable=True,
    )  # BAD_REQUEST_ERROR, GATEWAY_ERROR, INSUFFICIENT_FUNDS, etc.

    attempt_number = Column(
        Integer,
        nullable=False,
        default=1,
    )

    order_id = Column(
        String(100),
        nullable=True,
        index=True,
    )  # order_xxxxx

    subscription_id = Column(
        String(100),
        nullable=True,
        index=True,
    )  # sub_xxxxx

    metadata_json = Column(
        "metadata",
        JSON,
        default=dict,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    merchant = relationship(
        "Merchant",
        back_populates="transactions",
    )

    customer = relationship(
        "Customer",
        back_populates="transactions",
    )

    risk_assessment = relationship(
        "RevenueRiskAssessment",
        back_populates="transaction",
        uselist=False,
        cascade="all, delete-orphan",
    )

    recovery_case = relationship(
        "RecoveryCase",
        back_populates="transaction",
        uselist=False,
        cascade="all, delete-orphan",
    )

    recovery_actions = relationship(
        "RecoveryAction",
        back_populates="transaction",
        cascade="all, delete-orphan",
    )