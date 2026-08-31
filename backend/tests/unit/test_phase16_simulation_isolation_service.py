import pytest
from httpx import AsyncClient
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.transaction import Transaction
from backend.app.models.recovery_case import RecoveryCase
from backend.app.models.recovery_action import RecoveryAction
from backend.app.models.risk_assessment import RevenueRiskAssessment

ADMIN_HEADERS = {"X-User-Role": "MERCHANT_ADMIN", "X-User-ID": "admin_1"}


@pytest.mark.asyncio
async def test_simulation_does_not_pollute_live_transactions(
    client: AsyncClient, db_session: AsyncSession
):
    """Verify that running a simulation tags new transactions with is_simulation=True."""
    live_count_before = (
        await db_session.execute(select(func.count(Transaction.id)).where(Transaction.is_simulation == False))
    ).scalar()

    response = await client.post(
        "/api/v1/simulation/run", json={"scenario_name": "predefined_5_scenarios"}, headers=ADMIN_HEADERS
    )
    assert response.status_code == 200
    data = response.json()
    assert data["evaluated_count"] == 5

    live_count_after = (
        await db_session.execute(select(func.count(Transaction.id)).where(Transaction.is_simulation == False))
    ).scalar()
    assert live_count_after == live_count_before

    sim_count = (
        await db_session.execute(select(func.count(Transaction.id)).where(Transaction.is_simulation == True))
    ).scalar()
    assert sim_count >= 5


@pytest.mark.asyncio
async def test_simulation_does_not_pollute_live_recovery_cases(
    client: AsyncClient, db_session: AsyncSession
):
    """Verify that running a simulation tags new recovery cases with is_simulation=True."""
    live_cases_before = (
        await db_session.execute(select(func.count(RecoveryCase.id)).where(RecoveryCase.is_simulation == False))
    ).scalar()

    response = await client.post(
        "/api/v1/simulation/run", json={"scenario_name": "predefined_5_scenarios"}, headers=ADMIN_HEADERS
    )
    assert response.status_code == 200

    live_cases_after = (
        await db_session.execute(select(func.count(RecoveryCase.id)).where(RecoveryCase.is_simulation == False))
    ).scalar()
    assert live_cases_after == live_cases_before


@pytest.mark.asyncio
async def test_simulation_does_not_pollute_live_actions(
    client: AsyncClient, db_session: AsyncSession
):
    """Verify that running a simulation tags new recovery actions with is_simulation=True."""
    live_actions_before = (
        await db_session.execute(select(func.count(RecoveryAction.id)).where(RecoveryAction.is_simulation == False))
    ).scalar()

    response = await client.post(
        "/api/v1/simulation/run", json={"scenario_name": "predefined_5_scenarios"}, headers=ADMIN_HEADERS
    )
    assert response.status_code == 200

    live_actions_after = (
        await db_session.execute(select(func.count(RecoveryAction.id)).where(RecoveryAction.is_simulation == False))
    ).scalar()
    assert live_actions_after == live_actions_before


@pytest.mark.asyncio
async def test_repeated_simulation_runs_are_isolated(
    client: AsyncClient, db_session: AsyncSession
):
    """Verify that running 3 consecutive simulations keeps live transaction count unchanged."""
    live_before = (
        await db_session.execute(select(func.count(Transaction.id)).where(Transaction.is_simulation == False))
    ).scalar()

    for _ in range(3):
        res = await client.post(
            "/api/v1/simulation/run", json={"scenario_name": "predefined_5_scenarios"}, headers=ADMIN_HEADERS
        )
        assert res.status_code == 200

    live_after = (
        await db_session.execute(select(func.count(Transaction.id)).where(Transaction.is_simulation == False))
    ).scalar()
    assert live_after == live_before


@pytest.mark.asyncio
async def test_simulation_result_is_still_correct(
    client: AsyncClient
):
    """Verify that simulation run response structure and numbers remain accurate."""
    response = await client.post(
        "/api/v1/simulation/run", json={"scenario_name": "predefined_5_scenarios"}, headers=ADMIN_HEADERS
    )
    assert response.status_code == 200
    data = response.json()

    assert data["evaluated_count"] == 5
    assert "batch_id" in data
    assert "revenue_at_risk" in data
    assert "revenue_recovered" in data
    assert "cases" in data
    assert len(data["cases"]) == 5
