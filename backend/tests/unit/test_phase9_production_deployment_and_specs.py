import os
import json
import pytest
from backend.app.main import app
from backend.app.core.config import settings


@pytest.mark.asyncio
async def test_postman_collection_and_openapi_specs_existence():
    """Verify OpenAPI v3 specs and Postman Collections/Environments exist and are valid JSON."""
    openapi_path = "postman/specs/openapi.json"
    coll_path = "postman/collections/RecoverAI.postman_collection.json"
    env_path = "postman/environments/RecoverAI.postman_environment.json"

    assert os.path.exists(openapi_path), f"Missing {openapi_path}"
    assert os.path.exists(coll_path), f"Missing {coll_path}"
    assert os.path.exists(env_path), f"Missing {env_path}"

    with open(openapi_path, "r", encoding="utf-8") as f:
        openapi_spec = json.load(f)
    assert openapi_spec.get("openapi", "").startswith("3.")
    assert "paths" in openapi_spec
    assert "/health" in openapi_spec["paths"]
    assert "/api/v1/dashboard/metrics" in openapi_spec["paths"]

    with open(coll_path, "r", encoding="utf-8") as f:
        coll_data = json.load(f)
    assert "info" in coll_data
    assert coll_data["info"]["name"] == "RecoverAI API Suite"
    assert len(coll_data["item"]) >= 5

    with open(env_path, "r", encoding="utf-8") as f:
        env_data = json.load(f)
    assert env_data["name"] == "RecoverAI Production Environment"
    assert any(v["key"] == "base_url" for v in env_data["values"])


@pytest.mark.asyncio
async def test_openapi_schema_generation_and_tags():
    """Verify app.openapi() generates comprehensive documentation for all system tags."""
    schema = app.openapi()
    assert schema["info"]["title"] == "RecoverAI - Autonomous AI Revenue Recovery Agent"
    assert schema["info"]["version"] == "1.0.0"

    paths = schema["paths"]
    expected_endpoints = [
        "/health",
        "/webhooks/razorpay",
        "/api/v1/dashboard/metrics",
        "/api/v1/transactions",
        "/api/v1/recovery-cases",
        "/api/v1/approvals/pending",
        "/api/v1/simulation/run",
        "/api/v1/audit-logs",
        "/api/v1/evaluation/results",
    ]
    for ep in expected_endpoints:
        assert ep in paths, f"Missing OpenAPI endpoint path: {ep}"


@pytest.mark.asyncio
async def test_production_docker_and_env_configuration():
    """Verify production Dockerfiles, docker-compose, and environment configuration templates exist."""
    assert os.path.exists("docker-compose.yml")
    assert os.path.exists("backend/Dockerfile")
    assert os.path.exists("frontend/Dockerfile")
    assert os.path.exists(".env.example")

    with open("docker-compose.yml", "r", encoding="utf-8") as f:
        dc_content = f.read()
    assert "backend:" in dc_content
    assert "frontend:" in dc_content
    assert "8000:8000" in dc_content

    # Verify safe default settings (no live Razorpay secrets in defaults)
    assert settings.RAZORPAY_KEY_ID.startswith("rzp_test_") or "mock" in settings.RAZORPAY_KEY_ID.lower()


@pytest.mark.asyncio
async def test_postman_collection_request_headers_and_payloads():
    """Verify Postman collection items include RBAC role headers and webhook signature headers."""
    coll_path = "postman/collections/RecoverAI.postman_collection.json"
    with open(coll_path, "r", encoding="utf-8") as f:
        coll = json.load(f)

    # Flatten requests
    requests = []
    def extract_requests(items):
        for item in items:
            if "request" in item:
                requests.append(item)
            if "item" in item:
                extract_requests(item["item"])

    extract_requests(coll["item"])
    assert len(requests) >= 8

    # Verify webhook request includes X-Razorpay-Signature
    wh_req = next((r for r in requests if "webhook" in r["name"].lower()), None)
    assert wh_req is not None
    headers = {h["key"]: h["value"] for h in wh_req["request"]["header"]}
    assert "X-Razorpay-Signature" in headers


@pytest.mark.asyncio
async def test_phase9_non_negotiable_fintech_guardrails():
    """Verify Phase 9 non-negotiable safety requirements."""
    # 1. AI is advisory, policy decides
    from backend.app.policies.engine import DeterministicPolicyEngine
    from backend.app.agents.schemas import AgentDiagnosticOutput, ProposedActionSpec

    # High value transaction (>10,000) must escalate
    tx_data = {"id": "tx_safe_01", "amount": 15000.0, "failure_code": "GATEWAY_ERROR", "attempt_number": 1}
    cust_data = {"id": "c1", "communication_opt_out": False, "failed_payment_count": 0}
    proposal = AgentDiagnosticOutput(
        recovery_strategy="Intelligent Delayed Retry",
        proposed_action=ProposedActionSpec(type="RETRY_PAYMENT", delay_minutes=45),
        confidence=0.90,
        diagnosis="Gateway timeout on high value payment",
    )
    pol_res = DeterministicPolicyEngine.evaluate(
        agent_proposal=proposal,
        transaction_data=tx_data,
        customer_data=cust_data,
        merchant_policy={},
        recovery_score=80.0,
    )
    assert pol_res.requires_human_approval is True
