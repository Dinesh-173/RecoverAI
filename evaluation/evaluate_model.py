import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)
from ml.features.engineer import extract_features


def evaluate_model(
    model_path: str = "ml/models/recovery_model.joblib",
    test_path: str = "ml/data/test.csv",
    output_json_path: str = "evaluation/model_metrics.json"
) -> dict:
    """
    Evaluates the trained revenue recovery model on the held-out test dataset.
    Generates machine-readable metrics and prints a comprehensive report.
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Trained model not found at {model_path}. Please train it first.")

    model = joblib.load(model_path)
    test_df = pd.read_csv(test_path)

    X_test_raw = extract_features(test_df)
    y_test = test_df["is_recoverable"]

    y_pred = model.predict(X_test_raw)
    y_prob = model.predict_proba(X_test_raw)[:, 1]

    # Metrics calculation
    precision = float(precision_score(y_test, y_pred))
    recall = float(recall_score(y_test, y_pred))
    f1 = float(f1_score(y_test, y_pred))
    roc_auc = float(roc_auc_score(y_test, y_prob))
    
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0

    metrics = {
        "model_version": "v1.0.0-gbm",
        "dataset_size_test": len(test_df),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(roc_auc, 4),
        "false_positive_rate": round(fpr, 4),
        "confusion_matrix": {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp),
        },
        "domain_analysis": {
            "why_false_positives_matter": (
                "A False Positive represents executing costly recovery attempts or customer notifications "
                "on transactions that are fundamentally unrecoverable (e.g. invalid accounts, fraud blocks). "
                "Minimizing FPR protects merchant reputation and prevents notification fatigue."
            ),
            "why_false_negatives_matter": (
                "A False Negative means abandoning a payment that could have been recovered, leading to direct lost revenue."
            )
        }
    }

    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print("\n==========================================")
    print("      RECOVERAI ML MODEL EVALUATION       ")
    print("==========================================")
    print(f"Test Dataset Size : {len(test_df)}")
    print(f"Precision         : {precision:.4f}")
    print(f"Recall            : {recall:.4f}")
    print(f"F1 Score          : {f1:.4f}")
    print(f"ROC-AUC           : {roc_auc:.4f}")
    print(f"False Positive Rate: {fpr:.4f} ({fpr*100:.2f}%)")
    print("\nConfusion Matrix:")
    print(f"  [TN={tn:4d}  FP={fp:4d}]")
    print(f"  [FN={fn:4d}  TP={tp:4d}]")
    print(f"\nSaved metrics to {output_json_path}\n")

    return metrics


if __name__ == "__main__":
    evaluate_model()
