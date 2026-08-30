import os
import json
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, AsyncMock

from ml.data.synthetic_generator import generate_synthetic_dataset
from ml.features.engineer import extract_features, build_preprocessor
from ml.models.train import train_model
from evaluation.evaluate_model import evaluate_model
from evaluation.evaluate_recovery import evaluate_recovery_performance
from backend.app.ml_utils import get_trained_model
from backend.app.features_utils import compute_realtime_features
from backend.app.services.risk_service import RiskAssessmentService


def test_synthetic_dataset_reproducibility_and_schema(tmp_path):
    out_dir = str(tmp_path / "data")
    df1 = generate_synthetic_dataset(num_records=100, seed=42, output_dir=out_dir)
    df2 = generate_synthetic_dataset(num_records=100, seed=42, output_dir=out_dir)

    assert len(df1) == 100
    assert len(df2) == 100
    assert (df1["ground_truth_probability"] == df2["ground_truth_probability"]).all()
    assert (df1["is_recoverable"] == df2["is_recoverable"]).all()

    required_cols = [
        "transaction_id", "timestamp", "customer_id", "customer_segment",
        "merchant_category", "payment_method", "amount", "failure_code",
        "failure_reason", "attempt_number", "previous_success_count",
        "previous_failure_count", "customer_lifetime_value", "is_subscription",
        "communication_opt_out", "hour_of_day", "day_of_week",
        "ground_truth_probability", "optimal_strategy", "is_recoverable"
    ]
    for col in required_cols:
        assert col in df1.columns

    assert df1["is_recoverable"].isin([0, 1]).all()
    assert os.path.exists(os.path.join(out_dir, "train.csv"))
    assert os.path.exists(os.path.join(out_dir, "val.csv"))
    assert os.path.exists(os.path.join(out_dir, "test.csv"))


def test_feature_engineering_extraction_and_preprocessor():
    raw_df = pd.DataFrame([{
        "transaction_id": "tx_test_01",
        "amount": 12000.0,
        "payment_method": "UPI",
        "merchant_category": "ECOMMERCE",
        "failure_code": "GATEWAY_ERROR",
        "attempt_number": 2,
        "previous_success_count": 8,
        "previous_failure_count": 2,
        "customer_lifetime_value": 45000.0,
        "is_subscription": 1,
        "communication_opt_out": 0,
        "customer_segment": "HIGH_VALUE",
        "hour_of_day": 14,
        "day_of_week": 2,
    }])

    extracted = extract_features(raw_df)
    assert "success_ratio" in extracted.columns
    assert "log_amount" in extracted.columns
    assert "log_ltv" in extracted.columns
    assert "is_high_risk_retry" in extracted.columns

    assert extracted["success_ratio"].iloc[0] == 0.8  # 8 / (8+2)
    assert extracted["is_high_risk_retry"].iloc[0] == 1  # attempt > 1 and amount > 10000

    preprocessor = build_preprocessor()
    transformed = preprocessor.fit_transform(extracted)
    assert isinstance(transformed, np.ndarray)
    assert transformed.shape[0] == 1
    assert transformed.shape[1] > 10  # Encoded features


def test_model_artifact_loading_and_prediction():
    model_path = "ml/models/recovery_model.joblib"
    assert os.path.exists(model_path)

    model = get_trained_model(model_path)
    assert model is not None

    sample_tx = {
        "id": "tx_sample_01",
        "amount": 5000.0,
        "payment_method": "UPI",
        "merchant_category": "ECOMMERCE",
        "failure_code": "GATEWAY_ERROR",
        "failure_reason": "Bank timeout",
        "attempt_number": 1,
    }
    sample_cust = {
        "successful_payment_count": 10,
        "failed_payment_count": 1,
        "total_lifetime_value": 25000.0,
        "communication_opt_out": 0,
        "customer_segment": "HIGH_VALUE",
    }

    features_df = compute_realtime_features(sample_tx, sample_cust)
    probs = model.predict_proba(features_df)

    assert probs.shape == (1, 2)
    prob_recoverable = float(probs[0, 1])
    assert 0.0 <= prob_recoverable <= 1.0


@pytest.mark.asyncio
async def test_realtime_feature_computation_and_risk_assessment_service(db_session):
    tx_data = {
        "id": "tx_risk_test_999",
        "amount": 8000.0,
        "payment_method": "UPI",
        "merchant_category": "SAAS",
        "failure_code": "GATEWAY_ERROR",
        "attempt_number": 1,
    }
    cust_data = {
        "successful_payment_count": 5,
        "failed_payment_count": 0,
        "total_lifetime_value": 15000.0,
        "communication_opt_out": 0,
        "customer_segment": "STANDARD",
    }

    assessment = await RiskAssessmentService.assess_transaction(
        db=db_session,
        transaction_id="tx_risk_test_999",
        transaction_data=tx_data,
        customer_data=cust_data,
    )

    assert assessment is not None
    assert assessment.transaction_id == "tx_risk_test_999"
    assert assessment.model_version == "v1.0.0-gbm"
    assert 0.0 <= assessment.confidence <= 1.0
    assert 0.0 <= assessment.risk_score <= 100.0
    assert assessment.expected_recoverable_amount >= 0.0

    # Verify exact documented mathematical formulas:
    # risk_score = (1 - probability) * 100
    # expected_recoverable_amount = amount * probability
    expected_risk_score = round((1.0 - assessment.confidence) * 100.0, 2)
    assert abs(float(assessment.risk_score) - expected_risk_score) < 0.01
    assert float(assessment.expected_recoverable_amount) > 0.0


@pytest.mark.asyncio
async def test_risk_assessment_model_fallback_when_unloaded(db_session):
    tx_data = {
        "id": "tx_risk_fallback_01",
        "amount": 5000.0,
        "payment_method": "UPI",
        "failure_code": "GATEWAY_ERROR",
    }
    cust_data = {}

    with patch("backend.app.services.risk_service.get_trained_model", return_value=None):
        assessment = await RiskAssessmentService.assess_transaction(
            db=db_session,
            transaction_id="tx_risk_fallback_01",
            transaction_data=tx_data,
            customer_data=cust_data,
        )

        assert assessment is not None
        assert assessment.confidence == 0.85  # Fallback for GATEWAY_ERROR
        assert assessment.risk_score == 15.0  # (1 - 0.85) * 100
        assert assessment.expected_recoverable_amount == 4250.0  # 5000 * 0.85


def test_evaluation_methodology_and_acceptance_criteria():
    model_metrics = evaluate_model(
        model_path="ml/models/recovery_model.joblib",
        test_path="ml/data/test.csv",
        output_json_path="evaluation/model_metrics.json"
    )

    assert model_metrics["roc_auc"] >= 0.80
    assert model_metrics["precision"] >= 0.75
    assert model_metrics["recall"] >= 0.85
    assert model_metrics["f1_score"] >= 0.80
    assert "confusion_matrix" in model_metrics

    rec_metrics = evaluate_recovery_performance(
        model_path="ml/models/recovery_model.joblib",
        test_path="ml/data/test.csv",
        output_json_path="evaluation/recovery_metrics.json"
    )

    assert rec_metrics["impact_delta"]["relative_improvement_percentage"] > 40.0
    assert rec_metrics["recoverai_performance"]["recovery_rate_pct"] > rec_metrics["baseline_performance"]["recovery_rate_pct"]
