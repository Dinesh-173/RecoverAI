import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.pool import StaticPool

from backend.app.core.database import Base, get_db
from backend.app.main import app

# IMPORTANT: Import every model before create_all()
from backend.app.models.merchant import Merchant
from backend.app.models.customer import Customer
from backend.app.models.transaction import Transaction
from backend.app.models.recovery_case import RecoveryCase
from backend.app.models.recovery_action import RecoveryAction
from backend.app.models.risk_assessment import RevenueRiskAssessment
from backend.app.models.webhook_event import WebhookEvent
from backend.app.models.audit_log import AuditLog


# Use ONE shared SQLite connection for the entire test database.
# This is important because SQLite :memory: databases are connection-specific.
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DB_URL,
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    # Create all tables in the SAME connection pool used by the tests.
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    # Clean up tables after each test.
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # IMPORTANT:
    # Background tasks must use the same test database.
    app.state.test_session_factory = TestSessionLocal

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()

    if hasattr(app.state, "test_session_factory"):
        delattr(app.state, "test_session_factory")


@pytest.fixture
def admin_headers():
    return {"X-User-Role": "ADMIN"}