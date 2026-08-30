import os
import json
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.main import app
from backend.app.models.merchant import Merchant
from backend.app.models.customer import Customer
from backend.app.models.transaction import Transaction
from backend.app.models.recovery_case import RecoveryCase
from backend.app.models.audit_log import AuditLog

from evaluation.evaluate_model import evaluate_model
from evaluation.evaluate_recovery import evaluate_recovery_performance
from evaluation.generate_report import generate_full_evaluation_report
from scripts.seed_data import seed_database


@pytest.mark.asyncio
async def test_evaluation_report_generation_pipeline(tmp_path):
    """Verify end-to-end evaluation pipeline runs without errors and produces valid report artifacts."""
    json_output = str(tmp_path / "results.json")
    md_output = str(tmp_path / "report.md")

    generate_full_evaluation_report(
        report_output_path=md_output,
        json_output_path=json_output
    )

    assert os.path.exists(json_output)
    assert os.path.exists(md_output)

    with open(json_output, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "model_evaluation" in data
    assert "recovery_evaluation" in data
    assert data["model_evaluation"]["roc_auc"] >= 0.80
    assert data["recovery_evaluation"]["impact_delta"]["relative_improvement_percentage"] > 0


@pytest.mark.asyncio
async def test_ml_model_test_split_evaluation_metrics():
    """Verify ML model metrics against test set acceptance criteria (ROC-AUC >= 0.80, F1 >= 0.80)."""
    metrics = evaluate_model()
    
    assert metrics["model_version"] == "v1.0.0-gbm"
    assert metrics["dataset_size_test"] == 3000
    assert metrics["roc_auc"] >= 0.80
    assert metrics["precision"] >= 0.75
    assert metrics["recall"] >= 0.80
    assert metrics["f1_score"] >= 0.80
    
    cm = metrics["confusion_matrix"]
    assert (cm["true_negatives"] + cm["false_positives"] + cm["false_negatives"] + cm["true_positives"]) == 3000


@pytest.mark.asyncio
async def test_financial_recovery_roi_uplift():
    """Verify financial recovery evaluation benchmarks against blind retry baseline."""
    res = evaluate_recovery_performance()
    
    assert res["total_evaluated_transactions"] == 3000
    assert res["revenue_at_risk"] > 0
    assert res["recoverai_performance"]["recovered_revenue"] > res["baseline_performance"]["recovered_revenue"]
    assert res["impact_delta"]["additional_revenue_recovered"] > 0
    assert res["impact_delta"]["relative_improvement_percentage"] > 40.0
    assert res["recoverai_performance"]["avoided_wasteful_retries"] > 0


@pytest.mark.asyncio
async def test_evaluation_results_api_endpoint(client):
    """Verify GET /api/v1/evaluation/results returns structured held-out evaluation metrics."""
    resp = await client.get(
        "/api/v1/evaluation/results",
        headers={"X-User-Role": "MERCHANT_ADMIN"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "model_evaluation" in data or "status" in data


@pytest.mark.asyncio
async def test_database_seeding_script(db_session: AsyncSession):
    """Verify seed_database script populates realistic merchants, customers, and transactions."""
    # Seed 15 test transactions
    await seed_database(num_transactions=15, seed=123, db=db_session)

    # Verify merchant created
    res_m = await db_session.execute(select(Merchant).where(Merchant.id == "mer_apex_digital_01"))
    merchant = res_m.scalar_one_or_none()
    assert merchant is not None
    assert merchant.name == "Apex Digital Retail"

    # Verify customers created
    res_c = await db_session.execute(select(Customer).where(Customer.merchant_id == merchant.id))
    customers = res_c.scalars().all()
    assert len(customers) >= 10

    # Verify transactions created
    res_tx = await db_session.execute(select(Transaction).where(Transaction.merchant_id == merchant.id))
    txs = res_tx.scalars().all()
    assert len(txs) >= 15


@pytest.mark.asyncio
async def test_phase8_security_and_rbac_integrity(client):
    """Verify RBAC access controls on evaluation endpoints."""
    # MERCHANT_ADMIN permitted
    resp_admin = await client.get(
        "/api/v1/evaluation/results",
        headers={"X-User-Role": "MERCHANT_ADMIN"},
    )
    assert resp_admin.status_code == 200

    # VIEWER permitted for read-only evaluation results
    resp_viewer = await client.get(
        "/api/v1/evaluation/results",
        headers={"X-User-Role": "VIEWER"},
    )
    assert resp_viewer.status_code == 200
