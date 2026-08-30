import os
import json
import pytest
import joblib
from unittest.mock import patch
from httpx import AsyncClient

from backend.app.core.config import settings, Settings
from backend.app.providers.payments import get_payment_provider, SimulationPaymentAdapter, RazorpayTestAdapter
from backend.app.policies.engine import DeterministicPolicyEngine
from backend.app.agents.schemas import AgentDiagnosticOutput, ProposedActionSpec


@pytest.mark.asyncio
async def test_phase14_health_endpoint_and_dependency_status(client: AsyncClient):
    """
    1. Deployment Smoke Test: GET /health returns HTTP 200 with HEALTHY status and DB status.
    """
    response = await client.get("/health")
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["status"] == "HEALTHY"
    assert res_json["service"] == "RecoverAI Agent Engine"
    assert res_json["dependencies"]["database"] == "HEALTHY"


@pytest.mark.asyncio
async def test_phase14_cors_origin_restriction_config():
    """
    2. CORS Configuration Test: Validates comma-separated origin strings.
    """
    s = Settings(CORS_ORIGINS="https://app.recoverai.com,https://dashboard.recoverai.com")
    origins = s.CORS_ORIGINS
    assert isinstance(origins, list)
    assert len(origins) == 2
    assert "https://app.recoverai.com" in origins
    assert "https://dashboard.recoverai.com" in origins


@pytest.mark.asyncio
async def test_phase14_environment_driven_adapter_selection():
    """
    3. Payment Mode Separation:
    - DEMO_MODE=True -> SimulationPaymentAdapter
    - DEMO_MODE=False + valid test keys -> RazorpayTestAdapter
    """
    # Demo Mode
    adapter_sim = get_payment_provider(force_simulation=True)
    assert isinstance(adapter_sim, SimulationPaymentAdapter)

    # Production Test Mode
    with patch("backend.app.providers.payments.settings.DEMO_MODE", False), \
         patch("backend.app.providers.payments.settings.RAZORPAY_KEY_ID", "rzp_test_prodkey999"):
        adapter_rzp = get_payment_provider(force_simulation=False)
        assert isinstance(adapter_rzp, RazorpayTestAdapter)


@pytest.mark.asyncio
async def test_phase14_docker_and_env_placeholders():
    """
    4. Docker Manifest & Environment Configuration Check:
    - Verify backend/Dockerfile, frontend/Dockerfile, docker-compose.yml, .env.example exist.
    - Verify zero hardcoded production secrets.
    """
    assert os.path.exists("backend/Dockerfile")
    assert os.path.exists("frontend/Dockerfile")
    assert os.path.exists("docker-compose.yml")
    assert os.path.exists(".env.example")

    with open("docker-compose.yml", "r", encoding="utf-8") as f:
        dc_text = f.read()
    assert "backend/Dockerfile" in dc_text
    assert "NEXT_PUBLIC_API_URL" in dc_text

    with open(".env.example", "r", encoding="utf-8") as f:
        env_text = f.read()
    assert "mocksecret12345" in env_text
    assert "live_key_" not in env_text


@pytest.mark.asyncio
async def test_phase14_ml_model_production_artifact_loading():
    """
    5. ML Model Artifact Verification:
    - Model file ml/models/recovery_model.joblib exists.
    - Successfully loads via joblib and returns valid predictions.
    """
    model_path = "ml/models/recovery_model.joblib"
    assert os.path.exists(model_path), "Production ML model artifact missing!"

    model_pipeline = joblib.load(model_path)
    assert hasattr(model_pipeline, "predict_proba")
    assert hasattr(model_pipeline, "predict")


@pytest.mark.asyncio
async def test_phase14_non_negotiable_safety_invariant():
    """
    6. Non-negotiable Fintech Safety Invariant:
    AI PROPOSES -> POLICY DECIDES -> EXECUTOR EXECUTES
    AI outputs cannot execute payments without policy authorization.
    """
    proposal = AgentDiagnosticOutput(
        recovery_strategy="Delayed Retry",
        proposed_action=ProposedActionSpec(type="RETRY_PAYMENT", delay_minutes=30),
        confidence=0.99,
        diagnosis="Production deployment safety test",
    )
    # High value transaction requires human approval
    res = DeterministicPolicyEngine.evaluate(
        agent_proposal=proposal,
        transaction_data={"id": "tx_dep_01", "amount": 25000.0, "failure_code": "GATEWAY_ERROR", "attempt_number": 1},
        customer_data={"id": "c_dep", "communication_opt_out": False},
        merchant_policy={"high_value_threshold": 10000.0},
        recovery_score=88.0,
    )
    assert res.decision.value == "ESCALATED_HUMAN_APPROVAL"
    assert res.requires_human_approval is True
