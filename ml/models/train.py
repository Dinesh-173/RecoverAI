import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, roc_auc_score

from ml.features.engineer import extract_features, build_preprocessor


def train_model(
    train_path: str = "ml/data/train.csv",
    val_path: str = "ml/data/val.csv",
    model_output_path: str = "ml/models/recovery_model.joblib",
) -> Pipeline:
    """
    Trains the revenue recoverability prediction model using Gradient Boosting on fintech features.
    """
    print(f"Loading training data from {train_path}...")
    train_df = pd.read_csv(train_path)
    val_df = pd.read_csv(val_path)

    X_train_raw = extract_features(train_df)
    y_train = train_df["is_recoverable"]

    X_val_raw = extract_features(val_df)
    y_val = val_df["is_recoverable"]

    preprocessor = build_preprocessor()

    # Model: Gradient Boosting Classifier with balanced hyper-parameters for fintech scoring
    classifier = GradientBoostingClassifier(
        n_estimators=150,
        learning_rate=0.08,
        max_depth=4,
        random_state=42,
        subsample=0.85
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier)
        ]
    )

    print("Fitting Recovery Prediction Model pipeline...")
    pipeline.fit(X_train_raw, y_train)

    # Validation check
    val_preds = pipeline.predict(X_val_raw)
    val_probs = pipeline.predict_proba(X_val_raw)[:, 1]

    roc_auc = roc_auc_score(y_val, val_probs)
    print("\n--- Validation Performance ---")
    print(f"Validation ROC-AUC: {roc_auc:.4f}")
    print(classification_report(y_val, val_preds))

    os.makedirs(os.path.dirname(model_output_path), exist_ok=True)
    joblib.dump(pipeline, model_output_path)
    print(f"Model saved successfully to {model_output_path}")

    return pipeline


if __name__ == "__main__":
    train_model()
