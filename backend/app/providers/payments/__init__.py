from backend.app.providers.payments.base import PaymentProvider
from backend.app.providers.payments.razorpay_test import RazorpayTestAdapter
from backend.app.providers.payments.simulation import SimulationPaymentAdapter
from backend.app.core.config import settings


def get_payment_provider(force_simulation: bool = False) -> PaymentProvider:
    """Retrieve payment provider. Defaults to RazorpayTestAdapter if keys are provided, else SimulationPaymentAdapter."""
    if force_simulation or settings.DEMO_MODE or not settings.RAZORPAY_KEY_ID or settings.RAZORPAY_KEY_ID.startswith("rzp_test_mock"):
        return SimulationPaymentAdapter()
    return RazorpayTestAdapter()


__all__ = ["PaymentProvider", "RazorpayTestAdapter", "SimulationPaymentAdapter", "get_payment_provider"]
