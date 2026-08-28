import os
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.agents.schemas import AgentDiagnosticOutput, ProposedActionSpec
from backend.app.agents.prompts import SYSTEM_DIAGNOSTIC_PROMPT, build_diagnostic_user_prompt
from backend.app.agents.tools import AgentToolLayer
from backend.app.providers.llm import get_llm_provider
from backend.app.core.logging import logger


class RecoveryDiagnosticAgent:
    """
    Autonomous AI Diagnostic Agent for payment failure root-cause analysis and strategy formulation.
    Enforces structured Pydantic validation and includes a deterministic fallback engine.
    """
    def __init__(self, provider_type: str = ""):
        self.provider = get_llm_provider(provider_type)

    async def diagnose_and_propose(
        self,
        db: AsyncSession,
        transaction_data: Dict[str, Any],
        customer_data: Dict[str, Any],
        ml_risk_assessment: Dict[str, Any],
        merchant_policy: Dict[str, Any],
    ) -> AgentDiagnosticOutput:
        """
        Executes AI diagnosis. If LLM fails or is unavailable, seamlessly falls back
        to deterministic rule-based diagnosis.
        """
        user_prompt = build_diagnostic_user_prompt(
            transaction_data=transaction_data,
            customer_data=customer_data,
            ml_risk_assessment=ml_risk_assessment,
            merchant_policy=merchant_policy,
        )

        response_schema = AgentDiagnosticOutput.model_json_schema()

        try:
            raw_response = await self.provider.generate_structured_response(
                system_prompt=SYSTEM_DIAGNOSTIC_PROMPT,
                user_prompt=user_prompt,
                response_schema=response_schema,
            )
            parsed_output = AgentDiagnosticOutput(**raw_response)
            parsed_output.is_fallback = False
            return parsed_output

        except Exception as e:
            logger.warning(
                f"LLM generation failed or unavailable ({str(e)}). Engaging deterministic fallback engine.",
                extra={"service": "RecoveryDiagnosticAgent"}
            )
            return self._deterministic_fallback(
                transaction_data=transaction_data,
                customer_data=customer_data,
                ml_risk_assessment=ml_risk_assessment,
                merchant_policy=merchant_policy
            )

    def _deterministic_fallback(
        self,
        transaction_data: Dict[str, Any],
        customer_data: Dict[str, Any],
        ml_risk_assessment: Dict[str, Any],
        merchant_policy: Dict[str, Any],
    ) -> AgentDiagnosticOutput:
        """
        Fintech-grade deterministic fallback decision tree when LLM is unavailable.
        """
        f_code = transaction_data.get("failure_code", "UNKNOWN")
        attempt = transaction_data.get("attempt_number", 1)
        amount = transaction_data.get("amount", 0.0)
        prev_success = customer_data.get("successful_payment_count", 0)
        opt_out = customer_data.get("communication_opt_out", False)
        high_val_thresh = merchant_policy.get("high_value_threshold", 10000.0)

        # High value override
        if amount >= high_val_thresh:
            return AgentDiagnosticOutput(
                diagnosis="AI unavailable — deterministic fallback used. High-value payment escalated for operational review.",
                recovery_strategy="HUMAN_REVIEW",
                confidence=0.90,
                reason_codes=["FALLBACK_ACTIVE", "HIGH_VALUE_THRESHOLD_EXCEEDED"],
                requires_human_approval=True,
                proposed_action=ProposedActionSpec(
                    type="HUMAN_REVIEW",
                    delay_minutes=0,
                    channel="OPS_QUEUE"
                ),
                is_fallback=True,
            )

        # Fraud / Security blocks
        if f_code in ["FRAUD_SECURITY_BLOCK", "STOLEN_CARD"]:
            return AgentDiagnosticOutput(
                diagnosis="AI unavailable — deterministic fallback used. Transaction halted due to security risk flags.",
                recovery_strategy="STOP_RECOVERY",
                confidence=0.95,
                reason_codes=["FALLBACK_ACTIVE", "FRAUD_SECURITY_BLOCK"],
                requires_human_approval=False,
                proposed_action=ProposedActionSpec(
                    type="STOP_RECOVERY",
                    delay_minutes=0,
                    channel="NONE"
                ),
                is_fallback=True,
            )

        # Transient Gateway / Network errors
        if f_code in ["GATEWAY_ERROR", "NETWORK_TIMEOUT"] and attempt < 2 and prev_success >= 1:
            return AgentDiagnosticOutput(
                diagnosis="AI unavailable — deterministic fallback used. Transient network/gateway error with positive customer history.",
                recovery_strategy="DELAYED_RETRY",
                confidence=0.85,
                reason_codes=["FALLBACK_ACTIVE", "TRANSIENT_FAILURE", "HISTORICAL_SUCCESS"],
                requires_human_approval=False,
                proposed_action=ProposedActionSpec(
                    type="RETRY_PAYMENT",
                    delay_minutes=45,
                    channel="DIRECT_RETRY"
                ),
                is_fallback=True,
            )

        # Balance / Instrument issues
        if f_code in ["INSUFFICIENT_FUNDS", "USER_DROPPED", "EXPIRED_CARD"]:
            if not opt_out:
                return AgentDiagnosticOutput(
                    diagnosis="AI unavailable — deterministic fallback used. Customer prompted via secure payment link.",
                    recovery_strategy="CUSTOMER_NOTIFICATION",
                    confidence=0.80,
                    reason_codes=["FALLBACK_ACTIVE", "CUSTOMER_NOTIFICATION_ALLOWED"],
                    requires_human_approval=False,
                    proposed_action=ProposedActionSpec(
                        type="CUSTOMER_NOTIFICATION",
                        delay_minutes=60,
                        channel="SMS_PAYMENT_LINK"
                    ),
                    is_fallback=True,
                )
            else:
                return AgentDiagnosticOutput(
                    diagnosis="AI unavailable — deterministic fallback used. Customer has opted out of communication.",
                    recovery_strategy="STOP_RECOVERY",
                    confidence=0.90,
                    reason_codes=["FALLBACK_ACTIVE", "CUSTOMER_OPT_OUT"],
                    requires_human_approval=False,
                    proposed_action=ProposedActionSpec(
                        type="STOP_RECOVERY",
                        delay_minutes=0,
                        channel="NONE"
                    ),
                    is_fallback=True,
                )

        # Default fallback
        return AgentDiagnosticOutput(
            diagnosis="AI unavailable — deterministic fallback used. Attempt limits or unrecoverable pattern reached.",
            recovery_strategy="STOP_RECOVERY",
            confidence=0.70,
            reason_codes=["FALLBACK_ACTIVE", "DEFAULT_STOP_RULE"],
            requires_human_approval=False,
            proposed_action=ProposedActionSpec(
                type="STOP_RECOVERY",
                delay_minutes=0,
                channel="NONE"
            ),
            is_fallback=True,
        )
