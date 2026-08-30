import json
import hashlib

from fastapi import APIRouter, Request, Header, BackgroundTasks, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.core.database import get_db, AsyncSessionLocal
from backend.app.models.webhook_event import WebhookEvent
from backend.app.core.security import verify_razorpay_webhook_signature
from backend.app.workers.event_processor import WebhookEventProcessor
from backend.app.core.logging import logger


router = APIRouter(prefix="", tags=["Webhooks"])


async def process_webhook_background(webhook_event_id: str):
    """Background task worker for asynchronous event processing."""

    # During tests, use the test database session factory.
    # In normal application execution, use the production session factory.
    from backend.app.main import app

    session_factory = getattr(
        app.state,
        "test_session_factory",
        AsyncSessionLocal,
    )

    async with session_factory() as session:
        await WebhookEventProcessor.process_event(
            session,
            webhook_event_id,
        )


@router.post(
    "/webhooks/razorpay",
    status_code=status.HTTP_200_OK,
)
async def handle_razorpay_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_razorpay_signature: str = Header(None),
    x_razorpay_event_id: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Ingest Razorpay webhook notifications with HMAC-SHA256 signature verification,
    idempotent deduplication via razorpay_event_id,
    and asynchronous processing.
    """

    raw_body = await request.body()

    # ---------------------------------------------------------
    # 1. Signature Verification
    # ---------------------------------------------------------

    try:
        verify_razorpay_webhook_signature(
            raw_body=raw_body,
            signature=x_razorpay_signature,
        )

    except Exception as e:
        logger.warning(
            f"Webhook signature validation rejected: {e}"
        )

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "code": "INVALID_WEBHOOK_SIGNATURE",
                    "message": str(e),
                }
            },
        )

    # ---------------------------------------------------------
    # 2. Extract Event ID
    # ---------------------------------------------------------

    event_id = x_razorpay_event_id

    payload_hash = hashlib.sha256(raw_body).hexdigest()

    try:
        payload_data = json.loads(
            raw_body.decode("utf-8")
        )
    except Exception:
        payload_data = {}

    if not event_id:
        event_id = (
            payload_data.get("event_id")
            or f"evt_hash_{payload_hash[:16]}"
        )

    event_type = payload_data.get(
        "event",
        "unknown",
    )

    # ---------------------------------------------------------
    # 3. Idempotency Check
    # ---------------------------------------------------------

    stmt = select(WebhookEvent).where(
        WebhookEvent.razorpay_event_id == event_id
    )

    res = await db.execute(stmt)

    existing_event = res.scalar_one_or_none()

    if existing_event:
        logger.info(
            f"Duplicate webhook event ignored: {event_id}"
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "DUPLICATE_IGNORED",
                "event_id": event_id,
            },
        )

    # ---------------------------------------------------------
    # 4. Store Event Record
    # ---------------------------------------------------------

    webhook_event = WebhookEvent(
        razorpay_event_id=event_id,
        event_type=event_type,
        payload_hash=payload_hash,
        payload_json=payload_data,
        status="RECEIVED",
    )

    db.add(webhook_event)

    await db.commit()

    await db.refresh(webhook_event)

    # ---------------------------------------------------------
    # 5. Dispatch Background Processing
    # ---------------------------------------------------------

    background_tasks.add_task(
        process_webhook_background,
        webhook_event.id,
    )

    # ---------------------------------------------------------
    # 6. Return Fast 200 OK
    # ---------------------------------------------------------

    return {
        "status": "ACCEPTED",
        "event_id": event_id,
        "event_type": event_type,
    }