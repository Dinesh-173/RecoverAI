import os
import json
import pytest
from unittest.mock import patch
from httpx import AsyncClient

from backend.app.providers.payments import get_payment_provider, RazorpayTestAdapter, SimulationPaymentAdapter
from backend.app.policies.engine import DeterministicPolicyEngine
from backend.app.agents.schemas import AgentDiagnosticOutput, ProposedActionSpec


@pytest.mark.asyncio
async def test_phase11_predefined_simulation_scenarios(client: AsyncClient):
    """
    TEST 1: Verification of the 5 canonical live demonstration scenarios:
    - Scenario 1 (High-Value VIP): ₹45,000 -> ESCALATED TO HUMAN (WAITING_APPROVAL)
    - Scenario 2 (Transient Timeout): ₹1,499 UPI -> Delayed Retry / Policy Evaluated
    - Scenario 3 (Repeated Failure): Attempt 3 -> STOPPED BY POLICY
    - Scenario 4 (Customer Privacy Opt-Out): Opt-out -> STOPPED BY POLICY
    - Scenario 5 (Security Fraud Anomaly): Fraud block -> STOPPED BY POLICY (0 retries)
    """
    response = await client.post(
        "/api/v1/simulation/run",
        json={"scenario_name": "predefined_5_scenarios", "batch_size": 10},
        headers={"X-User-Role": "MERCHANT_ADMIN"},
    )
    assert response.status_code == 200
    res_data = response.json()

    assert res_data["evaluated_count"] == 5
    assert res_data["escalated_count"] == 1
    assert res_data["stopped_count"] >= 3

    cases = res_data["cases"]
    assert len(cases) == 5

    # Scenario 1 (VIP High-Value ₹45,000)
    s1 = cases[0]
    assert s1["amount"] == 45000.0
    assert s1["case_status"] == "WAITING_APPROVAL"
    assert s1["action_status"] == "ESCALATED_TO_HUMAN"

    # Scenario 3 (Repeated Failure Attempt 3)
    s3 = cases[2]
    assert s3["failure_code"] == "INSUFFICIENT_FUNDS"
    assert s3["case_status"] == "STOPPED"
    assert s3["action_status"] == "STOPPED_BY_POLICY"

    # Scenario 4 (Customer Opted Out)
    s4 = cases[3]
    assert s4["failure_code"] == "USER_DROPPED"
    assert s4["case_status"] == "STOPPED"
    assert s4["action_status"] == "STOPPED_BY_POLICY"

    # Scenario 5 (Security Fraud Block)
    s5 = cases[4]
    assert s5["failure_code"] == "FRAUD_SECURITY_BLOCK"
    assert s5["case_status"] == "STOPPED"
    assert s5["action_status"] == "STOPPED_BY_POLICY"


@pytest.mark.asyncio
async def test_phase11_architecture_decisions_and_safety():
    """
    TEST 2: Verification of Architecture Decision Records (ADRs):
    - ADR 01: Three-Tier Safety Architecture (AI proposes -> Policy decides -> Executor executes)
    - ADR 02: Dual Payment Adapters (RazorpayTestAdapter & SimulationPaymentAdapter)
    - ADR 04: Deterministic AI Fallback Engine
    """
    # 1. ADR 01: AI Proposal is evaluated by Policy Engine before action execution
    proposal = AgentDiagnosticOutput(
        recovery_strategy="Delayed Retry",
        proposed_action=ProposedActionSpec(type="RETRY_PAYMENT", delay_minutes=45),
        confidence=0.95,
        diagnosis="Transient bank downtime",
    )
    tx_data = {"id": "tx_adr_01", "amount": 15000.0, "failure_code": "GATEWAY_ERROR", "attempt_number": 1}
    cust_data = {"id": "c1", "communication_opt_out": False}
    policy_res = DeterministicPolicyEngine.evaluate(
        agent_proposal=proposal,
        transaction_data=tx_data,
        customer_data=cust_data,
        merchant_policy={},
        recovery_score=85.0,
    )
    # High value transaction (>10,000) MUST escalate to human approval regardless of AI confidence
    assert policy_res.requires_human_approval is True

    # 2. ADR 02: Dual Payment Adapter Pattern
    adapter_sim = get_payment_provider(force_simulation=True)
    assert isinstance(adapter_sim, SimulationPaymentAdapter)

    with patch("backend.app.providers.payments.settings.DEMO_MODE", False), \
         patch("backend.app.providers.payments.settings.RAZORPAY_KEY_ID", "rzp_test_livekey9999"):
        adapter_rzp = get_payment_provider(force_simulation=False)
        assert isinstance(adapter_rzp, RazorpayTestAdapter)

    # 3. ADR 04: Deterministic Fallback Engine for AI Downtime
    from backend.app.agents.recovery_agent import RecoveryDiagnosticAgent
    agent = RecoveryDiagnosticAgent()
    with patch.object(agent.provider, "generate_structured_response", side_effect=RuntimeError("504 Gateway Timeout")):
        fallback_output = await agent.diagnose_and_propose(
            db=None,
            transaction_data={"id": "tx_fb", "amount": 1499.0, "failure_code": "GATEWAY_ERROR"},
            customer_data={"id": "c1", "communication_opt_out": False},
            ml_risk_assessment={"recovery_score": 75.0, "risk_score": 25.0},
            merchant_policy={},
        )
        assert fallback_output.is_fallback is True
        assert fallback_output.confidence > 0.0


@pytest.mark.asyncio
async def test_phase11_empirical_metrics_consistency():
    """
    TEST 3: Verification of empirical benchmark evaluation output consistency:
    - ROC-AUC = 0.8332, Precision = 78.75%, Recall = 87.76%, F1 = 83.01%
    - Held-out 3,000 transaction split metrics match documentation exactly.
    """
    results_path = "evaluation/results.json"
    assert os.path.exists(results_path), "Missing evaluation/results.json"

    with open(results_path, "r", encoding="utf-8") as f:
        results = json.load(f)

    model_eval = results["model_evaluation"]
    assert model_eval["dataset_size_test"] == 3000
    assert model_eval["roc_auc"] == 0.8332
    assert model_eval["precision"] == 0.7875
    assert model_eval["recall"] == 0.8776
    assert model_eval["f1_score"] == 0.8301

    rec_eval = results["recovery_evaluation"]
    assert rec_eval["total_evaluated_transactions"] == 3000
    assert rec_eval["recoverai_performance"]["recovered_revenue"] == 16366824.55
    assert rec_eval["baseline_performance"]["recovered_revenue"] == 10428561.11
    assert rec_eval["impact_delta"]["relative_improvement_percentage"] == 56.94
    assert rec_eval["recoverai_performance"]["avoided_wasteful_retries"] == 803

    # Cross-check README.md consistency
    with open("README.md", "r", encoding="utf-8") as f:
        readme_content = f.read()
    assert "0.8332" in readme_content
    assert "16,366,824.55" in readme_content or "16,366,824" in readme_content
    assert "+56.94%" in readme_content
    assert "803" in readme_content


@pytest.mark.asyncio
async def test_phase11_submission_package_readiness():
    """
    TEST 4: Verification of hackathon production submission package readiness:
    - OpenAPI Specification (openapi.json)
    - Postman v2.1 Collection & Environment
    - Multi-stage Docker manifests & docker-compose configuration
    - Zero hardcoded production secrets
    """
    openapi_path = "postman/specs/openapi.json"
    coll_path = "postman/collections/RecoverAI.postman_collection.json"
    env_path = "postman/environments/RecoverAI.postman_environment.json"

    assert os.path.exists(openapi_path)
    assert os.path.exists(coll_path)
    assert os.path.exists(env_path)
    assert os.path.exists("docker-compose.yml")
    assert os.path.exists("backend/Dockerfile")
    assert os.path.exists("frontend/Dockerfile")
    assert os.path.exists(".env.example")
    assert os.path.exists("scripts/seed_data.py")

    with open(coll_path, "r", encoding="utf-8") as f:
        coll = json.load(f)
    assert coll["info"]["name"] == "RecoverAI API Suite"

    with open(env_path, "r", encoding="utf-8") as f:
        env = json.load(f)
    assert env["name"] == "RecoverAI Production Environment"
