import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """Derive domain-specific fintech features from raw transaction records."""
    data = df.copy()

    # Derived historical ratio
    total_hist = data["previous_success_count"] + data["previous_failure_count"]
    data["success_ratio"] = np.where(total_hist > 0, data["previous_success_count"] / total_hist, 0.5)

    # Log transformations for heavily skewed monetary metrics
    data["log_amount"] = np.log1p(np.maximum(0, data["amount"]))
    data["log_ltv"] = np.log1p(np.maximum(0, data["customer_lifetime_value"]))

    # Interaction: High value + repeated failure
    data["is_high_risk_retry"] = ((data["attempt_number"] > 1) & (data["amount"] > 10000)).astype(int)

    return data


def build_preprocessor() -> ColumnTransformer:
    """Builds a robust, production-grade scikit-learn feature preprocessor."""
    numeric_features = [
        "amount",
        "log_amount",
        "attempt_number",
        "previous_success_count",
        "previous_failure_count",
        "success_ratio",
        "customer_lifetime_value",
        "log_ltv",
        "is_subscription",
        "communication_opt_out",
        "hour_of_day",
        "day_of_week",
        "is_high_risk_retry"
    ]

    categorical_features = [
        "payment_method",
        "merchant_category",
        "failure_code",
        "customer_segment"
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features),
        ]
    )
    return preprocessor
