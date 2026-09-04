from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text


@pytest.fixture()
def sqlite_url(tmp_path: Path) -> str:
    db_path = tmp_path / "phase2.db"
    return f"sqlite:///{db_path.as_posix()}"


def test_alembic_upgrade_and_downgrade(sqlite_url: str, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SYNC_DATABASE_URL", sqlite_url)
    root = Path(__file__).resolve().parents[3]
    cfg = Config(str(root / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", sqlite_url)

    command.upgrade(cfg, "head")
    engine = create_engine(sqlite_url)
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    expected = {
        "merchants",
        "merchant_policies",
        "users",
        "customers",
        "transactions",
        "revenue_risk_assessments",
        "recovery_cases",
        "recovery_actions",
        "audit_logs",
        "webhook_events",
        "alembic_version",
    }
    assert expected.issubset(tables)

    webhook_uniques = inspector.get_unique_constraints("webhook_events")
    assert any("razorpay_event_id" in (u.get("column_names") or []) for u in webhook_uniques) or any(
        col.get("unique") for col in inspector.get_columns("webhook_events") if col["name"] == "razorpay_event_id"
    )

    action_uniques = inspector.get_unique_constraints("recovery_actions")
    assert any(u.get("name") == "uq_recovery_action_idempotency" for u in action_uniques)

    with engine.connect() as conn:
        version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        assert version == "002_simulation_isolation"

    command.downgrade(cfg, "base")
    inspector = inspect(engine)
    remaining = set(inspector.get_table_names())
    remaining.discard("alembic_version")
    assert remaining == set()
    engine.dispose()
