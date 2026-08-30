from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from backend.app.core.database import Base


class User(Base):
    """Merchant-side operator. Roles: MERCHANT_ADMIN, MERCHANT_OPERATOR, VIEWER."""

    __tablename__ = "users"

    id = Column(String(64), primary_key=True, default=lambda: f"usr_{uuid.uuid4().hex[:12]}")
    merchant_id = Column(String(64), ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True)
    email_hash = Column(String(64), nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    merchant = relationship("Merchant", back_populates="users")
