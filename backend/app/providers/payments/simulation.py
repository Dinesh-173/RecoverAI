import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from backend.app.providers.payments.base import PaymentProvider


class SimulationPaymentAdapter(PaymentProvider):
    """
    Clearly labeled Simulation Payment Adapter.
    Used for local offline development, demo mode, and repeatable test runs
    without requiring external Razorpay network connectivity.
    """
    async def create_payment_link(
        self,
        amount: float,
        currency: str,
        description: str,
        customer_name: str,
        customer_email: str,
        reference_id: str,
    ) -> Dict[str, Any]:
        sim_id = f"sim_plink_{uuid.uuid4().hex[:12]}"
        return {
            "status": "SUCCESS",
            "provider": "SIMULATION_ADAPTER",
            "is_simulation": True,
            "payment_link_id": sim_id,
            "short_url": f"https://rzp.io/sim/{sim_id}",
            "amount": amount,
            "currency": currency,
            "simulated_at": datetime.now(timezone.utc).isoformat(),
            "notice": "DEMO / SIMULATION ONLY - NO REAL MONEY MOVED"
        }

    async def fetch_payment(self, payment_id: str) -> Dict[str, Any]:
        return {
            "id": payment_id,
            "provider": "SIMULATION_ADAPTER",
            "is_simulation": True,
            "status": "captured",
            "amount": 250000,
            "currency": "INR",
            "method": "upi",
            "notice": "DEMO / SIMULATION ONLY"
        }

    async def create_order(
        self,
        amount: float,
        currency: str,
        receipt: str,
        notes: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        sim_order_id = f"sim_order_{uuid.uuid4().hex[:12]}"
        return {
            "id": sim_order_id,
            "provider": "SIMULATION_ADAPTER",
            "is_simulation": True,
            "amount": int(amount * 100),
            "currency": currency,
            "receipt": receipt,
            "status": "created",
            "notice": "DEMO / SIMULATION ONLY"
        }

    async def execute_bounded_recovery(
        self,
        transaction_id: str,
        action_type: str,
        amount: float,
        currency: str,
        customer_info: Dict[str, Any],
    ) -> Dict[str, Any]:
        sim_action_id = f"sim_act_{uuid.uuid4().hex[:12]}"
        
        if action_type in ["CUSTOMER_NOTIFICATION", "PAYMENT_LINK"]:
            return await self.create_payment_link(
                amount=amount,
                currency=currency,
                description=f"Simulated payment recovery for {transaction_id}",
                customer_name=customer_info.get("name", "Customer"),
                customer_email=customer_info.get("email", "customer@example.com"),
                reference_id=sim_action_id
            )
        elif action_type == "RETRY_PAYMENT":
            return {
                "status": "SUCCESS",
                "provider": "SIMULATION_ADAPTER",
                "is_simulation": True,
                "action": "RETRY_PAYMENT",
                "simulated_action_id": sim_action_id,
                "amount": amount,
                "currency": currency,
                "notice": "DEMO / SIMULATION ONLY - NO REAL MONEY MOVED"
            }
        elif action_type == "STOP_RECOVERY":
            return {
                "status": "SUCCESS",
                "provider": "SIMULATION_ADAPTER",
                "is_simulation": True,
                "action": "STOP_RECOVERY",
                "message": "Recovery terminated safely per policy."
            }
        else:
            return {
                "status": "SUCCESS",
                "provider": "SIMULATION_ADAPTER",
                "is_simulation": True,
                "action": action_type,
                "message": f"Simulated {action_type} executed successfully."
            }
