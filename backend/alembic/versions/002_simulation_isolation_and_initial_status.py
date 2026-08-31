"""Add simulation isolation and initial status columns.

Revision ID: 002_simulation_isolation
Revises: 001_initial
Create Date: 2026-08-31
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "002_simulation_isolation"
down_revision: Union[str, Sequence[str], None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add columns to transactions
    op.add_column(
        "transactions",
        sa.Column("is_simulation", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "transactions",
        sa.Column("initial_status", sa.String(length=50), nullable=True),
    )
    op.create_index("ix_transactions_is_simulation", "transactions", ["is_simulation"])
    op.create_index("ix_transactions_initial_status", "transactions", ["initial_status"])

    # 2. Add column to revenue_risk_assessments
    op.add_column(
        "revenue_risk_assessments",
        sa.Column("is_simulation", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_revenue_risk_assessments_is_simulation", "revenue_risk_assessments", ["is_simulation"])

    # 3. Add column to recovery_cases
    op.add_column(
        "recovery_cases",
        sa.Column("is_simulation", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_recovery_cases_is_simulation", "recovery_cases", ["is_simulation"])

    # 4. Add column to recovery_actions
    op.add_column(
        "recovery_actions",
        sa.Column("is_simulation", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_recovery_actions_is_simulation", "recovery_actions", ["is_simulation"])

    # 5. Backfill simulation flags for existing tx_s% legacy records
    op.execute("UPDATE transactions SET is_simulation = 1 WHERE id LIKE 'tx_s%'")
    op.execute("UPDATE revenue_risk_assessments SET is_simulation = 1 WHERE transaction_id LIKE 'tx_s%'")
    op.execute("UPDATE recovery_cases SET is_simulation = 1 WHERE transaction_id LIKE 'tx_s%'")
    op.execute("UPDATE recovery_actions SET is_simulation = 1 WHERE transaction_id LIKE 'tx_s%'")

    # 6. Backfill initial_status for transactions
    # Set default initial_status to current status
    op.execute("UPDATE transactions SET initial_status = status WHERE initial_status IS NULL")
    # For transactions that are FAILED or belong to a recovery_case / risk_assessment, initial_status was FAILED
    op.execute("""
        UPDATE transactions
        SET initial_status = 'FAILED'
        WHERE id IN (
            SELECT DISTINCT transaction_id FROM recovery_cases
        )
        OR id IN (
            SELECT DISTINCT transaction_id FROM revenue_risk_assessments
        )
        OR id LIKE 'tx_s%'
    """)


def downgrade() -> None:
    op.drop_index("ix_recovery_actions_is_simulation", table_name="recovery_actions")
    op.drop_column("recovery_actions", "is_simulation")

    op.drop_index("ix_recovery_cases_is_simulation", table_name="recovery_cases")
    op.drop_column("recovery_cases", "is_simulation")

    op.drop_index("ix_revenue_risk_assessments_is_simulation", table_name="revenue_risk_assessments")
    op.drop_column("revenue_risk_assessments", "is_simulation")

    op.drop_index("ix_transactions_initial_status", table_name="transactions")
    op.drop_index("ix_transactions_is_simulation", table_name="transactions")
    op.drop_column("transactions", "initial_status")
    op.drop_column("transactions", "is_simulation")
