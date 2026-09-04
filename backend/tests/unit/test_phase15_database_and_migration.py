import pytest
from sqlalchemy import select, inspect
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.transaction import Transaction
from backend.app.models.recovery_case import RecoveryCase
from backend.app.models.recovery_action import RecoveryAction
from backend.app.models.risk_assessment import RevenueRiskAssessment


@pytest.mark.asyncio
async def test_database_columns_and_migration_applied(db_session: AsyncSession):
    """Verify that is_simulation and initial_status exist on SQLAlchemy models and database."""
    stmt = select(Transaction).limit(1)
    res = await db_session.execute(stmt)
    tx = res.scalar_one_or_none()
    if tx:
        assert hasattr(tx, "is_simulation")
        assert hasattr(tx, "initial_status")
        assert isinstance(tx.is_simulation, bool)

    stmt_rc = select(RecoveryCase).limit(1)
    res_rc = await db_session.execute(stmt_rc)
    rc = res_rc.scalar_one_or_none()
    if rc:
        assert hasattr(rc, "is_simulation")

    stmt_rra = select(RevenueRiskAssessment).limit(1)
    res_rra = await db_session.execute(stmt_rra)
    rra = res_rra.scalar_one_or_none()
    if rra:
        assert hasattr(rra, "is_simulation")

    stmt_ra = select(RecoveryAction).limit(1)
    res_ra = await db_session.execute(stmt_ra)
    ra = res_ra.scalar_one_or_none()
    if ra:
        assert hasattr(ra, "is_simulation")


@pytest.mark.asyncio
async def test_forensic_backfill_integrity(db_session: AsyncSession):
    """Verify that legacy tx_s% transactions are marked as simulation and live records as non-simulation."""
    stmt_sim_tx = select(Transaction).where(Transaction.id.like("tx_s%"))
    res_sim_tx = await db_session.execute(stmt_sim_tx)
    sim_txs = res_sim_tx.scalars().all()
    for tx in sim_txs:
        assert tx.is_simulation is True
        assert tx.initial_status == "FAILED"

    stmt_live_tx = select(Transaction).where(~Transaction.id.like("tx_s%"))
    res_live_tx = await db_session.execute(stmt_live_tx)
    live_txs = res_live_tx.scalars().all()
    for tx in live_txs:
        assert tx.is_simulation is False


@pytest.mark.asyncio
async def test_initial_status_preservation_for_recovered_transactions(db_session: AsyncSession):
    """Verify that recovered transactions retain initial_status = 'FAILED' even when status = 'CAPTURED'."""
    stmt = select(Transaction).where(Transaction.status == "CAPTURED", ~Transaction.id.like("tx_s%"))
    res = await db_session.execute(stmt)
    recovered_txs = res.scalars().all()
    for tx in recovered_txs:
        assert tx.initial_status == "FAILED"
        assert tx.status == "CAPTURED"
