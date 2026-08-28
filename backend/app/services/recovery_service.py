from typing import Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.app.models.transaction import Transaction
from backend.app.models.customer import Customer
from backend.app.models.merchant import Merchant
from backend.app.models.recovery_case import RecoveryCase
from backend.app.models.recovery_action import RecoveryAction
from backend.app.models.risk_assessment import RevenueRiskAssessment
from backend.app.services.risk_service import RiskAssessmentService
from backend.app.services.audit_service import AuditService
from backend.app.agents.recovery_agent import RecoveryDiagnosticAgent
from backend.app.agents.tools import AgentToolLayer
from backend.app.policies.engine import DeterministicPolicyEngine
from backend.app.policies.rules import PolicyDecision
from backend.app.providers.payments import get_payment_provider
from backend.app.core.exceptions import (
    ResourceNotFoundException,
    PolicyViolationException,
    IdempotencyViolationException,
    UnauthorizedApprovalException,
)
from backend.app.core.logging import logger


class RecoveryService:
    @staticmethod
    async def analyze_transaction(
        db: AsyncSession,
        transaction_id: str,
        correlation_id: str = "",
        force_simulation: bool = False,
    ) -> RecoveryCase:
        """
        Full autonomous recovery loop:
        1. Context retrieval
        2. ML Risk assessment
        3. AI Diagnostic agent (with deterministic fallback)
        4. Deterministic policy guardrail validation
        5. Case lifecycle updates & Audit logging
        """
        stmt = (
            select(Transaction)
            .options(selectinload(Transaction.customer), selectinload(Transaction.merchant))
            .where(Transaction.id == transaction_id)
        )
        result = await db.execute(stmt)
        tx = result.scalar_one_or_none()
        if not tx:
            raise ResourceNotFoundException("Transaction", transaction_id)

        customer = tx.customer
        merchant = tx.merchant

        # 1. Fetch or execute ML Risk Assessment
        tx_data = {
            "id": tx.id,
            "amount": tx.amount,
            "currency": tx.currency,
            "payment_method": tx.payment_method,
            "status": tx.status,
            "failure_code": tx.failure_code,
            "failure_reason": tx.failure_reason,
            "attempt_number": tx.attempt_number,
            "merchant_category": merchant.business_category if merchant else "ECOMMERCE",
            "subscription_id": tx.subscription_id,
            "metadata_json": tx.metadata_json or {},
        }
        cust_data = {
            "id": customer.id,
            "name": customer.name,
            "customer_segment": customer.customer_segment,
            "successful_payment_count": customer.successful_payment_count,
            "failed_payment_count": customer.failed_payment_count,
            "total_lifetime_value": customer.total_lifetime_value,
            "communication_opt_out": customer.communication_opt_out,
            "email": "customer@example.com", # Masked representation
        }
        merchant_policy = {
            "high_value_threshold": merchant.high_value_threshold if merchant else 10000.0,
            "max_retries": merchant.max_retries if merchant else 2,
            "min_ai_confidence": merchant.min_ai_confidence if merchant else 0.70,
            "min_recovery_score": merchant.min_recovery_score if merchant else 15.0,
            "cooldown_minutes": merchant.cooldown_minutes if merchant else 60,
        }

        assessment = await RiskAssessmentService.assess_transaction(db, tx.id, tx_data, cust_data)

        # 2. Run AI Diagnostic Agent
        agent = RecoveryDiagnosticAgent()
        proposal = await agent.diagnose_and_propose(
            db=db,
            transaction_data=tx_data,
            customer_data=cust_data,
            ml_risk_assessment={
                "risk_score": assessment.risk_score,
                "expected_recoverable_amount": assessment.expected_recoverable_amount,
                "confidence": assessment.confidence,
            },
            merchant_policy=merchant_policy,
        )

        # 3. Calculate Deterministic Recovery Score
        recovery_score = AgentToolLayer.calculate_recovery_score(
            probability_of_recovery=assessment.confidence,
            expected_recoverable_amount=assessment.expected_recoverable_amount,
            action_success_probability=proposal.confidence,
        )

        # 4. Deterministic Policy Guardrail Check
        policy_result = DeterministicPolicyEngine.evaluate(
            agent_proposal=proposal,
            transaction_data=tx_data,
            customer_data=cust_data,
            merchant_policy=merchant_policy,
            recovery_score=recovery_score,
        )

        # 5. Create / Update Recovery Case
        stmt_case = select(RecoveryCase).where(RecoveryCase.transaction_id == tx.id)
        res_case = await db.execute(stmt_case)
        rec_case = res_case.scalar_one_or_none()

        if not rec_case:
            rec_case = RecoveryCase(
                transaction_id=tx.id,
                status="OPEN",
                risk_level="HIGH" if assessment.risk_score > 60 else ("MEDIUM" if assessment.risk_score > 30 else "LOW"),
            )
            db.add(rec_case)

        rec_case.diagnosis = proposal.diagnosis
        rec_case.recommended_action = proposal.proposed_action.type
        rec_case.recommended_delay_minutes = proposal.proposed_action.delay_minutes
        rec_case.confidence = proposal.confidence
        rec_case.recovery_score = recovery_score
        rec_case.requires_human_approval = policy_result.requires_human_approval
        rec_case.approval_reason = policy_result.reason if policy_result.requires_human_approval else None

        if policy_result.decision == PolicyDecision.ESCALATED_HUMAN_APPROVAL:
            rec_case.status = "WAITING_APPROVAL"
        elif policy_result.decision == PolicyDecision.STOPPED:
            rec_case.status = "STOPPED"
        elif policy_result.decision == PolicyDecision.APPROVED:
            rec_case.status = "SCHEDULED" if proposal.proposed_action.delay_minutes > 0 else "EXECUTING"
        else:
            rec_case.status = "STOPPED"

        await db.commit()
        await db.refresh(rec_case)

        # 6. Audit Trail Logging
        await AuditService.log_event(
            db=db,
            entity_type="RECOVERY_CASE",
            entity_id=rec_case.id,
            actor_type="AI_AGENT" if not proposal.is_fallback else "SYSTEM",
            actor_id="RecoverAI_Agent_v1",
            action="ANALYZE_TRANSACTION",
            reason=proposal.diagnosis,
            input_summary={"transaction_id": tx.id, "amount": tx.amount, "failure_code": tx.failure_code},
            output_summary={
                "strategy": proposal.recovery_strategy,
                "confidence": proposal.confidence,
                "recovery_score": recovery_score,
                "is_fallback": proposal.is_fallback,
            },
            policy_result=policy_result.decision.value,
            correlation_id=correlation_id,
        )

        return rec_case

    @staticmethod
    async def execute_action(
        db: AsyncSession,
        case_id: str,
        correlation_id: str = "",
        force_simulation: bool = False,
    ) -> RecoveryAction:
        """
        Executes a bounded financial recovery action for an approved recovery case.
        Enforces business idempotency and records immutable audit records.
        """
        stmt = (
            select(RecoveryCase)
            .options(
                selectinload(RecoveryCase.transaction).selectinload(Transaction.customer),
                selectinload(RecoveryCase.actions),
            )
            .where(RecoveryCase.id == case_id)
        )
        res = await db.execute(stmt)
        rec_case = res.scalar_one_or_none()
        if not rec_case:
            raise ResourceNotFoundException("RecoveryCase", case_id)

        tx = rec_case.transaction
        customer = tx.customer

        # Check if already successfully recovered or stopped
        if rec_case.status in ["RECOVERED", "STOPPED"]:
            raise PolicyViolationException(f"Case is already in terminal status '{rec_case.status}'.")

        action_type = rec_case.recommended_action or "RETRY_PAYMENT"

        # Business Idempotency Guard: prevent executing the exact same action twice for this attempt
        for act in rec_case.actions:
            if act.action_type == action_type and act.status in ["SUCCESS", "EXECUTING"]:
                raise IdempotencyViolationException(
                    f"Action '{action_type}' was already executed for recovery case {case_id}."
                )

        provider = get_payment_provider(force_simulation=force_simulation)
        customer_info = {
            "name": customer.name,
            "email": "customer@example.com",
        }

        # Create action record
        action_record = RecoveryAction(
            recovery_case_id=rec_case.id,
            action_type=action_type,
            status="EXECUTING",
            amount=tx.amount,
            reason=rec_case.diagnosis,
            policy_decision="APPROVED",
            policy_version="v1.2.0",
        )
        db.add(action_record)
        await db.commit()
        await db.refresh(action_record)

        try:
            result_payload = await provider.execute_bounded_recovery(
                transaction_id=tx.id,
                action_type=action_type,
                amount=tx.amount,
                currency=tx.currency,
                customer_info=customer_info,
            )

            action_record.status = "SUCCESS"
            action_record.result_json = result_payload
            action_record.executed_at = datetime.now(timezone.utc)

            # Update case status based on outcome
            if action_type == "STOP_RECOVERY":
                rec_case.status = "STOPPED"
            else:
                rec_case.status = "RECOVERED"
                # Update customer stats
                customer.successful_payment_count += 1
                customer.total_lifetime_value += tx.amount
                customer.last_payment_at = datetime.now(timezone.utc)
                tx.status = "CAPTURED"

            await db.commit()
            await db.refresh(action_record)
            await db.refresh(rec_case)

            # Audit log
            await AuditService.log_event(
                db=db,
                entity_type="RECOVERY_ACTION",
                entity_id=action_record.id,
                actor_type="SYSTEM",
                actor_id="ActionExecutor",
                action=f"EXECUTE_{action_type}",
                reason="Policy approved recovery execution",
                input_summary={"case_id": rec_case.id, "amount": tx.amount},
                output_summary=result_payload,
                policy_result="APPROVED",
                correlation_id=correlation_id,
            )
            return action_record

        except Exception as e:
            action_record.status = "FAILED"
            action_record.error_code = "EXECUTION_ERROR"
            action_record.result_json = {"error": str(e)}
            rec_case.status = "FAILED"
            await db.commit()
            raise

    @staticmethod
    async def approve_case(
        db: AsyncSession,
        case_id: str,
        user_role: str = "MERCHANT_ADMIN",
        user_id: str = "operator_1",
        correlation_id: str = "",
        force_simulation: bool = False,
    ) -> RecoveryAction:
        """Human approval for high-risk or high-value cases."""
        if user_role not in ["MERCHANT_ADMIN", "ADMIN"]:
            raise UnauthorizedApprovalException("Only users with role MERCHANT_ADMIN or ADMIN can approve cases.")

        stmt = select(RecoveryCase).where(RecoveryCase.id == case_id)
        res = await db.execute(stmt)
        rec_case = res.scalar_one_or_none()
        if not rec_case:
            raise ResourceNotFoundException("RecoveryCase", case_id)

        rec_case.requires_human_approval = False
        rec_case.status = "EXECUTING"
        rec_case.assigned_to = user_id
        await db.commit()

        await AuditService.log_event(
            db=db,
            entity_type="RECOVERY_CASE",
            entity_id=rec_case.id,
            actor_type="MERCHANT",
            actor_id=user_id,
            action="HUMAN_APPROVAL_GRANTED",
            reason="Merchant operator approved high-value recovery action",
            policy_result="APPROVED",
            correlation_id=correlation_id,
        )

        return await RecoveryService.execute_action(
            db=db,
            case_id=rec_case.id,
            correlation_id=correlation_id,
            force_simulation=force_simulation,
        )

    @staticmethod
    async def reject_case(
        db: AsyncSession,
        case_id: str,
        reason: str = "Rejected by merchant operator",
        user_role: str = "MERCHANT_ADMIN",
        user_id: str = "operator_1",
        correlation_id: str = "",
    ) -> RecoveryCase:
        """Merchant rejection of a pending recovery action."""
        if user_role not in ["MERCHANT_ADMIN", "ADMIN"]:
            raise UnauthorizedApprovalException("Only users with role MERCHANT_ADMIN or ADMIN can reject cases.")

        stmt = select(RecoveryCase).where(RecoveryCase.id == case_id)
        res = await db.execute(stmt)
        rec_case = res.scalar_one_or_none()
        if not rec_case:
            raise ResourceNotFoundException("RecoveryCase", case_id)

        rec_case.status = "STOPPED"
        rec_case.requires_human_approval = False
        rec_case.assigned_to = user_id
        await db.commit()

        await AuditService.log_event(
            db=db,
            entity_type="RECOVERY_CASE",
            entity_id=rec_case.id,
            actor_type="MERCHANT",
            actor_id=user_id,
            action="HUMAN_REJECTION",
            reason=reason,
            policy_result="STOPPED",
            correlation_id=correlation_id,
        )
        return rec_case
