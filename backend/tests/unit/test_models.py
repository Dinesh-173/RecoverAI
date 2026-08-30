import pytest
from sqlalchemy import create_engine, event, inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.core.database import Base
from backend.app.models import (
    AuditLog,
    Customer,
    Merchant,
    MerchantPolicy,
    RecoveryAction,
    RecoveryCase,
    RevenueRiskAssessment,
    Transaction,
    User,
    WebhookEvent,
)


@pytest.fixture()
def session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _fk_pragma(dbapi_connection, _connection_record):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


def _seed_merchant_graph(db: Session) -> tuple[Merchant, Customer, Transaction, RecoveryCase]:
    merchant = Merchant(name="Acme Payments", business_category="SAAS", currency="INR")
    db.add(merchant)
    db.flush()

    db.add(
        MerchantPolicy(
            merchant_id=merchant.id,
            max_retry_attempts=2,
            high_value_threshold=10000.0,
            min_recovery_score=15.0,
            min_ai_confidence=0.70,
            contact_cooldown_minutes=60,
            max_contact_attempts=2,
        )
    )
    db.add(
        User(
            merchant_id=merchant.id,
            email_hash="abc123",
            display_name="Ops Admin",
            role="MERCHANT_ADMIN",
        )
    )
    customer = Customer(
        merchant_id=merchant.id,
        name="Priya",
        email_hash="custhash",
        customer_segment="HIGH_VALUE",
        successful_payment_count=8,
        failed_payment_count=1,
    )
    db.add(customer)
    db.flush()

    txn = Transaction(
        merchant_id=merchant.id,
        customer_id=customer.id,
        amount=499.0,
        status="FAILED",
        failure_reason="temporary_failure",
        failure_code="GATEWAY_ERROR",
        attempt_number=1,
    )
    db.add(txn)
    db.flush()

    case = RecoveryCase(transaction_id=txn.id, status="OPEN", risk_level="MEDIUM")
    db.add(case)
    db.commit()
    db.refresh(merchant)
    db.refresh(customer)
    db.refresh(txn)
    db.refresh(case)
    return merchant, customer, txn, case


def test_create_core_graph(session: Session):
    merchant, customer, txn, case = _seed_merchant_graph(session)
    assert merchant.id.startswith("mer_")
    assert customer.merchant_id == merchant.id
    assert txn.customer_id == customer.id
    assert case.transaction_id == txn.id
    assert session.scalar(select(MerchantPolicy).where(MerchantPolicy.merchant_id == merchant.id))
    assert session.scalar(select(User).where(User.role == "MERCHANT_ADMIN"))


def _index_columns(inspector, table: str) -> set[str]:
    names: set[str] = set()
    for idx in inspector.get_indexes(table):
        names.update(idx.get("column_names") or [])
    return names


def test_required_indexes_exist(session: Session):
    inspector = inspect(session.bind)
    assert "status" in _index_columns(inspector, "transactions")
    assert "created_at" in _index_columns(inspector, "transactions")
    assert "status" in _index_columns(inspector, "recovery_cases")
    assert "correlation_id" in _index_columns(inspector, "audit_logs")


def test_webhook_event_id_is_unique(session: Session):
    session.add(
        WebhookEvent(
            razorpay_event_id="evt_1",
            event_type="payment.failed",
            payload_hash="hash-a",
        )
    )
    session.commit()
    session.add(
        WebhookEvent(
            razorpay_event_id="evt_1",
            event_type="payment.failed",
            payload_hash="hash-b",
        )
    )
    with pytest.raises(IntegrityError):
        session.commit()


def test_recovery_action_idempotency_unique(session: Session):
    _, _, txn, case = _seed_merchant_graph(session)
    session.add(
        RecoveryAction(
            recovery_case_id=case.id,
            transaction_id=txn.id,
            action_type="DELAYED_RETRY",
            recovery_attempt=1,
            amount=txn.amount,
        )
    )
    session.commit()
    session.add(
        RecoveryAction(
            recovery_case_id=case.id,
            transaction_id=txn.id,
            action_type="DELAYED_RETRY",
            recovery_attempt=1,
            amount=txn.amount,
        )
    )
    with pytest.raises(IntegrityError):
        session.commit()


def test_one_policy_per_merchant(session: Session):
    merchant, *_ = _seed_merchant_graph(session)
    session.add(MerchantPolicy(merchant_id=merchant.id))
    with pytest.raises(IntegrityError):
        session.commit()


def test_audit_log_correlation_id_persists(session: Session):
    session.add(
        AuditLog(
            entity_type="RECOVERY_CASE",
            entity_id="case_test",
            actor_type="SYSTEM",
            actor_id="phase2",
            action="CREATE",
            correlation_id="corr_abc",
        )
    )
    session.commit()
    row = session.scalar(select(AuditLog).where(AuditLog.correlation_id == "corr_abc"))
    assert row is not None
    assert row.actor_type == "SYSTEM"


def test_risk_assessment_links_to_transaction(session: Session):
    _, _, txn, _ = _seed_merchant_graph(session)
    session.add(
        RevenueRiskAssessment(
            transaction_id=txn.id,
            risk_score=72.5,
            expected_recoverable_amount=400.0,
            confidence=0.81,
            model_version="v1.0.0",
            features_version="v1.0.0",
        )
    )
    session.commit()
    stored = session.scalar(
        select(RevenueRiskAssessment).where(RevenueRiskAssessment.transaction_id == txn.id)
    )
    assert stored.confidence == pytest.approx(0.81)
