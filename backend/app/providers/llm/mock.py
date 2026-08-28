from typing import Dict, Any
from backend.app.providers.llm.base import LLMProvider


class MockLLMProvider(LLMProvider):
    """
    Deterministic Mock LLM Provider for offline demonstration, test suites,
    and high-throughput simulated benchmarking.
    """
    async def generate_structured_response(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: Dict[str, Any],
        temperature: float = 0.1,
    ) -> Dict[str, Any]:
        # Parse basic context clues from user_prompt
        prompt_lower = user_prompt.lower()

        if "gateway_error" in prompt_lower or "network_timeout" in prompt_lower or "bank downtime" in prompt_lower:
            return {
                "diagnosis": "Customer encountered a transient bank gateway timeout. Historical payment success indicates high customer intent.",
                "recovery_strategy": "DELAYED_RETRY",
                "confidence": 0.92,
                "reason_codes": [
                    "TRANSIENT_GATEWAY_FAILURE",
                    "HIGH_HISTORICAL_INTENT",
                    "LOW_RETRY_COUNT"
                ],
                "requires_human_approval": False,
                "proposed_action": {
                    "type": "RETRY_PAYMENT",
                    "delay_minutes": 45,
                    "channel": "DIRECT_RETRY"
                }
            }
        elif "insufficient_funds" in prompt_lower:
            return {
                "diagnosis": "Transaction declined due to insufficient account balance. Immediate retries will fail; asynchronous customer payment reminder is optimal.",
                "recovery_strategy": "CUSTOMER_NOTIFICATION",
                "confidence": 0.84,
                "reason_codes": [
                    "INSUFFICIENT_FUNDS_DETECTED",
                    "REQUIRES_CUSTOMER_TOPUP",
                    "SMART_TIMED_NOTIFICATION"
                ],
                "requires_human_approval": False,
                "proposed_action": {
                    "type": "CUSTOMER_NOTIFICATION",
                    "delay_minutes": 180,
                    "channel": "WHATSAPP_SMS_PAYMENT_LINK"
                }
            }
        elif "expired_card" in prompt_lower or "card expired" in prompt_lower:
            return {
                "diagnosis": "Card on file has expired. Autonomous card retry will continue to fail; prompt customer to update payment instrument via secure Razorpay link.",
                "recovery_strategy": "CUSTOMER_NOTIFICATION",
                "confidence": 0.89,
                "reason_codes": [
                    "EXPIRED_PAYMENT_INSTRUMENT",
                    "NEW_CARD_LINK_REQUIRED"
                ],
                "requires_human_approval": False,
                "proposed_action": {
                    "type": "CUSTOMER_NOTIFICATION",
                    "delay_minutes": 30,
                    "channel": "EMAIL_PAYMENT_LINK"
                }
            }
        elif "fraud" in prompt_lower or "security_block" in prompt_lower:
            return {
                "diagnosis": "Transaction flagged for potential security or risk anomaly by issuer risk engine. Autonomous retry is forbidden.",
                "recovery_strategy": "STOP_RECOVERY",
                "confidence": 0.98,
                "reason_codes": [
                    "FRAUD_RISK_SHIELD",
                    "PREVENT_CHARGEBACK_RISK"
                ],
                "requires_human_approval": False,
                "proposed_action": {
                    "type": "STOP_RECOVERY",
                    "delay_minutes": 0,
                    "channel": "NONE"
                }
            }
        elif "high_value" in prompt_lower or "vip" in prompt_lower:
            return {
                "diagnosis": "High-value enterprise customer transaction failed. Requires human operational verification before re-attempting financial charge.",
                "recovery_strategy": "HUMAN_REVIEW",
                "confidence": 0.95,
                "reason_codes": [
                    "HIGH_VALUE_THRESHOLD_EXCEEDED",
                    "VIP_ACCOUNT_WHITEGLOVE_CARE"
                ],
                "requires_human_approval": True,
                "proposed_action": {
                    "type": "HUMAN_REVIEW",
                    "delay_minutes": 0,
                    "channel": "OPS_QUEUE"
                }
            }
        else:
            return {
                "diagnosis": "Payment failed due to an unclassified or ambiguous error. Proceeding with standard delayed retry.",
                "recovery_strategy": "DELAYED_RETRY",
                "confidence": 0.75,
                "reason_codes": [
                    "STANDARD_RECOVERY_ATTEMPT",
                    "FIRST_RETRY_WINDOW"
                ],
                "requires_human_approval": False,
                "proposed_action": {
                    "type": "RETRY_PAYMENT",
                    "delay_minutes": 60,
                    "channel": "DIRECT_RETRY"
                }
            }
