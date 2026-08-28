from sqlalchemy import Column, String, DateTime, Text, JSON
from datetime import datetime, timezone
import uuid

from backend.app.core.database import Base


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(String(64), primary_key=True, default=lambda: f"wh_{uuid.uuid4().hex[:12]}")
    razorpay_event_id = Column(String(100), unique=True, nullable=False, index=True) # MANDATORY UNIQUE CONSTRAINT FOR IDEMPOTENCY
    event_type = Column(String(100), nullable=False, index=True) # payment.failed, payment.captured, order.paid, etc.
    payload_hash = Column(String(64), nullable=False)
    received_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), nullable=False, default="RECEIVED", index=True) # RECEIVED, PROCESSING, PROCESSED, FAILED, DUPLICATE
    payload_json = Column("payload", JSON, default=dict)
    error_message = Column(Text, nullable=True)
