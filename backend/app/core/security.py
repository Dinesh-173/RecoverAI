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


from typing import List
from fastapi import Header, Depends
from backend.app.core.exceptions import ForbiddenException, UnauthorizedApprovalException

def require_role(allowed_roles: List[str]):
    """
    FastAPI dependency factory enforcing Role-Based Access Control (RBAC).
    Extracts role from X-User-Role header (defaults to MERCHANT_ADMIN if omitted).
    """
    async def role_checker(
        x_user_role: Optional[str] = Header(None),
    ) -> str:
        role = (x_user_role or "MERCHANT_ADMIN").upper()
        normalized_allowed = [r.upper() for r in allowed_roles]
        if role not in normalized_allowed:
            if set(normalized_allowed) == {"MERCHANT_ADMIN", "ADMIN"}:
                raise UnauthorizedApprovalException(
                    f"User role '{role}' is not authorized. Allowed roles: {allowed_roles}"
                )
            raise ForbiddenException(
                f"User role '{role}' is not authorized for this endpoint. Allowed roles: {allowed_roles}"
            )
        return role
    return role_checker
