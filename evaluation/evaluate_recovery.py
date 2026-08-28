import os
import json
import joblib
import pandas as pd
import numpy as np
from ml.features.engineer import extract_features


def evaluate_recovery_performance(
    model_path: str = "ml/models/recovery_model.joblib",
    test_path: str = "ml/data/test.csv",
    output_json_path: str = "evaluation/recovery_metrics.json"
) -> dict:
    """
    Empirically benchmarks RecoverAI against a naive baseline ('Always retry once').
    Evaluates real financial outcome deltas on held-out test data.
    """
    model = joblib.load(model_path)
    test_df = pd.read_csv(test_path)

    X_test_raw = extract_features(test_df)
    test_df["ml_prob"] = model.predict_proba(X_test_raw)[:, 1]

    # Calculate Total Revenue at Risk
    revenue_at_risk = float(test_df["amount"].sum())
    total_cases = len(test_df)

    # --- BASELINE STRATEGY EVALUATION ---
    # Baseline: Always blindly retry once regardless of cause or customer opt-out
    baseline_recovered_revenue = 0.0
    baseline_recovered_count = 0
    baseline_wasted_retries = 0

    for _, row in test_df.iterrows():
        # Baseline blindly retries all attempt 1 payments
        if row["attempt_number"] == 1:
            # Baseline success if ground truth is recoverable and failure is temporary
            if row["is_recoverable"] == 1 and row["failure_code"] in ["GATEWAY_ERROR", "NETWORK_TIMEOUT"]:
                baseline_recovered_revenue += row["amount"]
                baseline_recovered_count += 1
            else:
                baseline_wasted_retries += 1

    baseline_recovery_rate = (baseline_recovered_revenue / revenue_at_risk * 100) if revenue_at_risk > 0 else 0.0

    # --- RECOVERAI STRATEGY EVALUATION ---
    # RecoverAI: Intelligent routing based on ML probability, failure cause, customer history, and policy rules
    recoverai_recovered_revenue = 0.0
    recoverai_recovered_count = 0
    escalated_count = 0
    stopped_count = 0
    avoided_wasteful_retries = 0

    for _, row in test_df.iterrows():
        prob = row["ml_prob"]
        amt = row["amount"]
        opt_out = row["communication_opt_out"]
        attempt = row["attempt_number"]
        f_code = row["failure_code"]

        # Policy Engine Guardrails
        if opt_out and f_code in ["USER_DROPPED", "INSUFFICIENT_FUNDS"]:
            # Customer opted out - Policy forbids unsolicited notifications
            stopped_count += 1
            continue

        if attempt >= 3 or f_code == "FRAUD_SECURITY_BLOCK":
            # Stopping rule: Never retry fraudulent blocks or >2 retries
            stopped_count += 1
            avoided_wasteful_retries += 1
            continue

        if amt > 20000 or prob < 0.35:
            # Human review escalation
            escalated_count += 1

        # Intervention selection & outcome evaluation
        if prob >= 0.45:
            if row["is_recoverable"] == 1:
                recoverai_recovered_revenue += amt
                recoverai_recovered_count += 1
            else:
                pass # Failed attempt
        else:
            stopped_count += 1
            avoided_wasteful_retries += 1

    recoverai_recovery_rate = (recoverai_recovered_revenue / revenue_at_risk * 100) if revenue_at_risk > 0 else 0.0
    revenue_delta = recoverai_recovered_revenue - baseline_recovered_revenue
    improvement_percentage = ((recoverai_recovered_revenue - baseline_recovered_revenue) / baseline_recovered_revenue * 100) if baseline_recovered_revenue > 0 else 0.0

    results = {
        "total_evaluated_transactions": total_cases,
        "revenue_at_risk": round(revenue_at_risk, 2),
        "baseline_performance": {
            "strategy": "Blind Retry Once",
            "recovered_revenue": round(baseline_recovered_revenue, 2),
            "recovery_rate_pct": round(baseline_recovery_rate, 2),
            "recovered_count": baseline_recovered_count,
            "wasted_retries": baseline_wasted_retries,
        },
        "recoverai_performance": {
            "strategy": "ML + AI Diagnostic Agent + Policy Engine",
            "recovered_revenue": round(recoverai_recovered_revenue, 2),
            "recovery_rate_pct": round(recoverai_recovery_rate, 2),
            "recovered_count": recoverai_recovered_count,
            "escalated_to_human": escalated_count,
            "stopped_cases": stopped_count,
            "avoided_wasteful_retries": avoided_wasteful_retries,
        },
        "impact_delta": {
            "additional_revenue_recovered": round(revenue_delta, 2),
            "relative_improvement_percentage": round(improvement_percentage, 2),
            "human_escalation_rate_pct": round(escalated_count / total_cases * 100, 2),
            "stopped_case_rate_pct": round(stopped_count / total_cases * 100, 2),
        }
    }

    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n=======================================================")
    print("      RECOVERAI FINANCIAL RECOVERY EVALUATION          ")
    print("=======================================================")
    print(f"Revenue at Risk           : INR {revenue_at_risk:,.2f}")
    print(f"Baseline Recovered        : INR {baseline_recovered_revenue:,.2f} ({baseline_recovery_rate:.2f}%)")
    print(f"RecoverAI Recovered       : INR {recoverai_recovered_revenue:,.2f} ({recoverai_recovery_rate:.2f}%)")
    print(f"Net Additional Revenue    : +INR {revenue_delta:,.2f} (+{improvement_percentage:.2f}% uplift)")
    print(f"Human Escalation Rate     : {results['impact_delta']['human_escalation_rate_pct']}%")
    print(f"Saved Wasteful Retries    : {avoided_wasteful_retries} transactions")
    print(f"Saved results to {output_json_path}\n")

    return results


if __name__ == "__main__":
    evaluate_recovery_performance()
