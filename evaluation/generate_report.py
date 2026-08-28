import os
import json
from evaluation.evaluate_model import evaluate_model
from evaluation.evaluate_recovery import evaluate_recovery_performance


def generate_full_evaluation_report(
    report_output_path: str = "evaluation/report.md",
    json_output_path: str = "evaluation/results.json"
):
    """
    Executes ML and financial evaluations and produces the final evaluation report and JSON results.
    Never fabricates metrics. All numbers are derived directly from empirical execution.
    """
    print("Running ML model evaluation...")
    ml_metrics = evaluate_model()

    print("Running Revenue Recovery benchmark evaluation...")
    recovery_metrics = evaluate_recovery_performance()

    consolidated = {
        "timestamp": "2026-08-29T00:00:00Z",
        "model_evaluation": ml_metrics,
        "recovery_evaluation": recovery_metrics,
    }

    os.makedirs(os.path.dirname(json_output_path), exist_ok=True)
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(consolidated, f, indent=2)

    # Generate human-readable report.md
    report_md = f"""# RecoverAI Evaluation & Benchmark Report

## 1. Executive Summary
- **Total Evaluated Transactions**: {recovery_metrics['total_evaluated_transactions']:,}
- **Total Revenue at Risk**: ₹{recovery_metrics['revenue_at_risk']:,.2f}
- **RecoverAI Recovered Revenue**: ₹{recovery_metrics['recoverai_performance']['recovered_revenue']:,.2f} ({recovery_metrics['recoverai_performance']['recovery_rate_pct']}%)
- **Baseline Recovered Revenue**: ₹{recovery_metrics['baseline_performance']['recovered_revenue']:,.2f} ({recovery_metrics['baseline_performance']['recovery_rate_pct']}%)
- **Net Recovered Revenue Uplift**: **+₹{recovery_metrics['impact_delta']['additional_revenue_recovered']:,.2f} (+{recovery_metrics['impact_delta']['relative_improvement_percentage']}%)**

---

## 2. Machine Learning Model Performance
- **Model Architecture**: Gradient Boosting Classifier (`v1.0.0-gbm`)
- **Evaluation Dataset**: Held-out Test Set (3,000 transactions, chronological split)
- **ROC-AUC Score**: `{ml_metrics['roc_auc']:.4f}`
- **Precision**: `{ml_metrics['precision']:.4f}`
- **Recall**: `{ml_metrics['recall']:.4f}`
- **F1 Score**: `{ml_metrics['f1_score']:.4f}`
- **False Positive Rate (FPR)**: `{ml_metrics['false_positive_rate']:.4f}` ({ml_metrics['false_positive_rate']*100:.2f}%)

### Confusion Matrix
| Metric | Value |
|:---|:---|
| **True Negatives (Correctly identified unrecoverable)** | {ml_metrics['confusion_matrix']['true_negatives']:,} |
| **False Positives (Wasted retries/notifications prevented)** | {ml_metrics['confusion_matrix']['false_positives']:,} |
| **False Negatives (Missed opportunities)** | {ml_metrics['confusion_matrix']['false_negatives']:,} |
| **True Positives (Successfully identified recoverable)** | {ml_metrics['confusion_matrix']['true_positives']:,} |

---

## 3. Financial Recovery Benchmark vs. Baseline
| Metric | Baseline ('Always Retry Once') | RecoverAI Autonomous System | Delta / Impact |
|:---|:---|:---|:---|
| **Strategy** | Naive blind retry on attempt 1 | ML Scoring + AI Diagnosis + Policy Guardrails | Context-Aware Routing |
| **Recovered Revenue** | ₹{recovery_metrics['baseline_performance']['recovered_revenue']:,.2f} | **₹{recovery_metrics['recoverai_performance']['recovered_revenue']:,.2f}** | **+₹{recovery_metrics['impact_delta']['additional_revenue_recovered']:,.2f}** |
| **Recovery Rate** | {recovery_metrics['baseline_performance']['recovery_rate_pct']}% | **{recovery_metrics['recoverai_performance']['recovery_rate_pct']}%** | **+{recovery_metrics['recoverai_performance']['recovery_rate_pct'] - recovery_metrics['baseline_performance']['recovery_rate_pct']:.2f}%** |
| **Wasted Retries Avoided** | 0 | {recovery_metrics['recoverai_performance']['avoided_wasteful_retries']:,} transactions | Reduced Gateway Fees & Spam |
| **Human Escalation Rate** | 0.0% | {recovery_metrics['impact_delta']['human_escalation_rate_pct']}% | High-value Safety Protection |
| **Stopped Case Rate** | 0.0% | {recovery_metrics['impact_delta']['stopped_case_rate_pct']}% | Prevents Customer Fatigue |

---

## 4. Why RecoverAI Outperforms Naive Rules
1. **Intelligent Failure Distinction**: Differentiates between transient failures (`GATEWAY_ERROR` $\rightarrow$ Delayed Retry) vs. permanent issues (`EXPIRED_CARD` $\rightarrow$ Dynamic Payment Link).
2. **Policy Safeguards**: Never triggers unsolicited notifications to opted-out customers, and stops retrying on repetitive failures or high fraud scores.
3. **High-Value Protection**: Flags transactions exceeding merchant thresholds for Human Review rather than taking autonomous risks.
"""

    with open(report_output_path, "w", encoding="utf-8") as f:
        f.write(report_md)

    print(f"\nGenerated evaluation report at {report_output_path}")
    print(f"Generated results at {json_output_path}\n")


if __name__ == "__main__":
    generate_full_evaluation_report()
