import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.models.risk_assessment import RevenueRiskAssessment
from backend.app.ml_utils import get_trained_model
from backend.app.features_utils import compute_realtime_features
from backend.app.core.logging import logger


class RiskAssessmentService:
    @staticmethod
    async def assess_transaction(
        db: AsyncSession,
        transaction_id: str,
        transaction_data: Dict[str, Any],
        customer_data: Dict[str, Any],
    ) -> RevenueRiskAssessment:
        """
        Calculates ML recoverability probability and expected recoverable amount.
        Persists RevenueRiskAssessment record.
        """
        # Check if already assessed
        stmt = select(RevenueRiskAssessment).where(RevenueRiskAssessment.transaction_id == transaction_id)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            return existing

        amount = float(transaction_data.get("amount", 0.0))
        model = get_trained_model()

        if model is not None:
            features_df = compute_realtime_features(transaction_data, customer_data)
            try:
                prob = float(model.predict_proba(features_df)[0, 1])
            except Exception as e:
                logger.warning(f"Model prediction failed ({e}). Using statistical default.")
                prob = 0.65
        else:
            # Fallback heuristic if model not loaded
            f_code = transaction_data.get("failure_code", "")
            if f_code in ["GATEWAY_ERROR", "NETWORK_TIMEOUT"]:
                prob = 0.85
            elif f_code == "INSUFFICIENT_FUNDS":
                prob = 0.60
            elif f_code == "FRAUD_SECURITY_BLOCK":
                prob = 0.05
            else:
                prob = 0.50

        # Risk score: 0 (low risk / easily recovered) to 100 (high risk of permanent loss)
        risk_score = round((1.0 - prob) * 100.0, 2)
        expected_amount = round(amount * prob, 2)

        assessment = RevenueRiskAssessment(
            transaction_id=transaction_id,
            risk_score=risk_score,
            expected_recoverable_amount=expected_amount,
            confidence=round(prob, 4),
            model_version="v1.0.0-gbm",
            features_version="v1.0.0",
        )
        db.add(assessment)
        await db.commit()
        await db.refresh(assessment)
        return assessment
