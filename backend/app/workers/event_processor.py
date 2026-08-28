import json
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.models.webhook_event import WebhookEvent
from backend.app.models.transaction import Transaction
from backend.app.services.recovery_service import RecoveryService
from backend.app.core.logging import logger


class WebhookEventProcessor:
    """
    Asynchronous Webhook Event Processor.
    Handles decoupled, non-blocking execution of payment events and triggers recovery workflows.
    """
    @staticmethod
    async def process_event(db: AsyncSession, webhook_event_id: str):
        stmt = select(WebhookEvent).where(WebhookEvent.id == webhook_event_id)
        res = await db.execute(stmt)
        evt = res.scalar_one_or_none()
        if not evt:
            logger.error(f"Webhook event {webhook_event_id} not found for background processing.")
            return

        evt.status = "PROCESSING"
        await db.commit()

        try:
            payload = evt.payload_json or {}
            event_type = evt.event_type

            # Check supported Razorpay events: payment.failed, payment.captured, etc.
            if event_type == "payment.failed":
                payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
                pay_id = payment_entity.get("id")
                error_code = payment_entity.get("error_code")
                error_description = payment_entity.get("error_description")

                # Find transaction in DB
                stmt_tx = select(Transaction).where(Transaction.external_transaction_id == pay_id)
                res_tx = await db.execute(stmt_tx)
                tx = res_tx.scalar_one_or_none()

                if tx:
                    tx.status = "FAILED"
                    tx.failure_code = error_code or "GATEWAY_ERROR"
                    tx.failure_reason = error_description or "Payment failed"
                    await db.commit()

                    # Trigger autonomous recovery analysis
                    await RecoveryService.analyze_transaction(
                        db=db,
                        transaction_id=tx.id,
                        correlation_id=f"evt_{evt.razorpay_event_id}",
                    )

            elif event_type in ["payment.captured", "payment.authorized", "order.paid"]:
                payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
                pay_id = payment_entity.get("id")
                stmt_tx = select(Transaction).where(Transaction.external_transaction_id == pay_id)
                res_tx = await db.execute(stmt_tx)
                tx = res_tx.scalar_one_or_none()
                if tx:
                    tx.status = "CAPTURED"
                    await db.commit()

            evt.status = "PROCESSED"
            evt.processed_at = datetime.now(timezone.utc)
            await db.commit()
            logger.info(f"Successfully processed webhook event {evt.razorpay_event_id} ({event_type})")

        except Exception as e:
            logger.error(f"Failed to process webhook event {webhook_event_id}: {e}")
            evt.status = "FAILED"
            evt.error_message = str(e)
            await db.commit()
