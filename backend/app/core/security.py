import hmac
import hashlib
import uuid
from typing import Optional
from backend.app.core.config import settings
from backend.app.core.exceptions import WebhookSignatureException


def verify_razorpay_webhook_signature(
    raw_body: bytes,
    signature: str,
    secret: Optional[str] = None,
) -> bool:
    """
    Verifies the HMAC SHA256 signature of a Razorpay webhook payload against the secret.
    Conforms to official Razorpay Webhook Signature Verification specifications.
    """
    if not signature:
        raise WebhookSignatureException("Missing X-Razorpay-Signature header.")

    webhook_secret = secret or settings.RAZORPAY_WEBHOOK_SECRET
    if not webhook_secret:
        raise WebhookSignatureException("Webhook secret is not configured.")

    expected_signature = hmac.new(
        key=webhook_secret.encode("utf-8"),
        msg=raw_body,
        digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, signature):
        raise WebhookSignatureException("Razorpay webhook signature verification failed.")

    return True


def generate_correlation_id() -> str:
    """Generate a unique correlation ID for tracking requests across the system."""
    return f"corr_{uuid.uuid4().hex[:16]}"


def mask_email(email: str) -> str:
    """Safely mask customer email for privacy preservation (e.g. j***e@example.com)."""
    if not email or "@" not in email:
        return "masked@customer.internal"
    user, domain = email.split("@", 1)
    if len(user) <= 2:
        masked_user = user[0] + "*"
    else:
        masked_user = user[0] + "*" * (len(user) - 2) + user[-1]
    return f"{masked_user}@{domain}"


def hash_identifier(value: str) -> str:
    """Generate a deterministic SHA-256 hash for privacy-safe customer deduplication."""
    return hashlib.sha256(value.strip().lower().encode("utf-8")).hexdigest()
