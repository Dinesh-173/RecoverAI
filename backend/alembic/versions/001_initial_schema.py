"""Initial RecoverAI schema.

Revision ID: 001_initial
Revises:
Create Date: 2026-08-29
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001_initial"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "merchants",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("business_category", sa.String(100), nullable=False, server_default="ECOMMERCE"),
        sa.Column("currency", sa.String(3), nullable=False, server_default="INR"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "merchant_policies",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("merchant_id", sa.String(64), sa.ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("max_retry_attempts", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("high_value_threshold", sa.Float(), nullable=False, server_default="10000.0"),
        sa.Column("min_recovery_score", sa.Float(), nullable=False, server_default="15.0"),
        sa.Column("min_ai_confidence", sa.Float(), nullable=False, server_default="0.70"),
        sa.Column("contact_cooldown_minutes", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("max_contact_attempts", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("policy_version", sa.String(50), nullable=False, server_default="v1.0.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("merchant_id", name="uq_merchant_policies_merchant_id"),
    )
    op.create_index("ix_merchant_policies_merchant_id", "merchant_policies", ["merchant_id"])

    op.create_table(
        "users",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("merchant_id", sa.String(64), sa.ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email_hash", sa.String(64), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_merchant_id", "users", ["merchant_id"])
    op.create_index("ix_users_email_hash", "users", ["email_hash"])
    op.create_index("ix_users_role", "users", ["role"])

    op.create_table(
        "customers",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("merchant_id", sa.String(64), sa.ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email_hash", sa.String(64), nullable=False),
        sa.Column("customer_segment", sa.String(50), nullable=False, server_default="STANDARD"),
        sa.Column("successful_payment_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed_payment_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_lifetime_value", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("last_payment_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("communication_opt_out", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_customers_merchant_id", "customers", ["merchant_id"])
    op.create_index("ix_customers_email_hash", "customers", ["email_hash"])

    op.create_table(
        "transactions",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("external_transaction_id", sa.String(100), nullable=True),
        sa.Column("merchant_id", sa.String(64), sa.ForeignKey("merchants.id"), nullable=False),
        sa.Column("customer_id", sa.String(64), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="INR"),
        sa.Column("payment_method", sa.String(50), nullable=False, server_default="UPI"),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("failure_reason", sa.String(255), nullable=True),
        sa.Column("failure_code", sa.String(100), nullable=True),
        sa.Column("attempt_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("order_id", sa.String(100), nullable=True),
        sa.Column("subscription_id", sa.String(100), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("external_transaction_id", name="uq_transactions_external_id"),
    )
    op.create_index("ix_transactions_external_transaction_id", "transactions", ["external_transaction_id"])
    op.create_index("ix_transactions_merchant_id", "transactions", ["merchant_id"])
    op.create_index("ix_transactions_customer_id", "transactions", ["customer_id"])
    op.create_index("ix_transactions_status", "transactions", ["status"])
    op.create_index("ix_transactions_created_at", "transactions", ["created_at"])
    op.create_index("ix_transactions_order_id", "transactions", ["order_id"])
    op.create_index("ix_transactions_subscription_id", "transactions", ["subscription_id"])

    op.create_table(
        "revenue_risk_assessments",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column(
            "transaction_id",
            sa.String(64),
            sa.ForeignKey("transactions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("expected_recoverable_amount", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("model_version", sa.String(50), nullable=False, server_default="v1.0.0-xgb"),
        sa.Column("features_version", sa.String(50), nullable=False, server_default="v1.0.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("transaction_id", name="uq_revenue_risk_assessments_transaction_id"),
    )
    op.create_index("ix_revenue_risk_assessments_transaction_id", "revenue_risk_assessments", ["transaction_id"])

    op.create_table(
        "recovery_cases",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column(
            "transaction_id",
            sa.String(64),
            sa.ForeignKey("transactions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(50), nullable=False, server_default="OPEN"),
        sa.Column("risk_level", sa.String(20), nullable=False, server_default="MEDIUM"),
        sa.Column("diagnosis", sa.Text(), nullable=True),
        sa.Column("recommended_action", sa.String(100), nullable=True),
        sa.Column("recommended_delay_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("recovery_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("requires_human_approval", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("approval_reason", sa.String(255), nullable=True),
        sa.Column("assigned_to", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("transaction_id", name="uq_recovery_cases_transaction_id"),
    )
    op.create_index("ix_recovery_cases_transaction_id", "recovery_cases", ["transaction_id"])
    op.create_index("ix_recovery_cases_status", "recovery_cases", ["status"])
    op.create_index("ix_recovery_cases_requires_human_approval", "recovery_cases", ["requires_human_approval"])
    op.create_index("ix_recovery_cases_created_at", "recovery_cases", ["created_at"])

    op.create_table(
        "recovery_actions",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column(
            "recovery_case_id",
            sa.String(64),
            sa.ForeignKey("recovery_cases.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "transaction_id",
            sa.String(64),
            sa.ForeignKey("transactions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("action_type", sa.String(100), nullable=False),
        sa.Column("recovery_attempt", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(50), nullable=False, server_default="PENDING"),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("policy_decision", sa.String(50), nullable=False, server_default="APPROVED"),
        sa.Column("policy_version", sa.String(50), nullable=False, server_default="v1.0.0"),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("error_code", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint(
            "transaction_id",
            "action_type",
            "recovery_attempt",
            name="uq_recovery_action_idempotency",
        ),
    )
    op.create_index("ix_recovery_actions_recovery_case_id", "recovery_actions", ["recovery_case_id"])
    op.create_index("ix_recovery_actions_transaction_id", "recovery_actions", ["transaction_id"])
    op.create_index("ix_recovery_actions_status", "recovery_actions", ["status"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", sa.String(64), nullable=False),
        sa.Column("actor_type", sa.String(50), nullable=False, server_default="SYSTEM"),
        sa.Column("actor_id", sa.String(100), nullable=False, server_default="system_worker"),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("input_summary", sa.JSON(), nullable=True),
        sa.Column("output_summary", sa.JSON(), nullable=True),
        sa.Column("policy_result", sa.String(50), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("correlation_id", sa.String(64), nullable=False),
    )
    op.create_index("ix_audit_logs_entity_type", "audit_logs", ["entity_type"])
    op.create_index("ix_audit_logs_entity_id", "audit_logs", ["entity_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_timestamp", "audit_logs", ["timestamp"])
    op.create_index("ix_audit_logs_correlation_id", "audit_logs", ["correlation_id"])

    op.create_table(
        "webhook_events",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("razorpay_event_id", sa.String(100), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("payload_hash", sa.String(64), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="RECEIVED"),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.UniqueConstraint("razorpay_event_id", name="uq_webhook_events_razorpay_event_id"),
    )
    op.create_index("ix_webhook_events_razorpay_event_id", "webhook_events", ["razorpay_event_id"])
    op.create_index("ix_webhook_events_event_type", "webhook_events", ["event_type"])
    op.create_index("ix_webhook_events_received_at", "webhook_events", ["received_at"])
    op.create_index("ix_webhook_events_status", "webhook_events", ["status"])


def downgrade() -> None:
    op.drop_table("webhook_events")
    op.drop_table("audit_logs")
    op.drop_table("recovery_actions")
    op.drop_table("recovery_cases")
    op.drop_table("revenue_risk_assessments")
    op.drop_table("transactions")
    op.drop_table("customers")
    op.drop_table("users")
    op.drop_table("merchant_policies")
    op.drop_table("merchants")
