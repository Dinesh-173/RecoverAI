from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class PaymentProvider(ABC):
    """
    Abstract Payment Provider abstraction for RecoverAI.
    Enforces standardized execution across Razorpay Test Mode and local Simulation.
    """
    @abstractmethod
    async def create_payment_link(
        self,
        amount: float,
        currency: str,
        description: str,
        customer_name: str,
        customer_email: str,
        reference_id: str,
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def fetch_payment(self, payment_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def create_order(
        self,
        amount: float,
        currency: str,
        receipt: str,
        notes: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def execute_bounded_recovery(
        self,
        transaction_id: str,
        action_type: str,
        amount: float,
        currency: str,
        customer_info: Dict[str, Any],
    ) -> Dict[str, Any]:
        pass
