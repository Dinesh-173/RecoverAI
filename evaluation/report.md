# RecoverAI Evaluation & Benchmark Report

## 1. Executive Summary
- **Total Evaluated Transactions**: 3,000
- **Total Revenue at Risk**: ₹31,815,249.85
- **RecoverAI Recovered Revenue**: ₹16,366,824.55 (51.44%)
- **Baseline Recovered Revenue**: ₹10,428,561.11 (32.78%)
- **Net Recovered Revenue Uplift**: **+₹5,938,263.44 (+56.94%)**

---

## 2. Machine Learning Model Performance
- **Model Architecture**: Gradient Boosting Classifier (`v1.0.0-gbm`)
- **Evaluation Dataset**: Held-out Test Set (3,000 transactions, chronological split)
- **ROC-AUC Score**: `0.8332`
- **Precision**: `0.7875`
- **Recall**: `0.8776`
- **F1 Score**: `0.8301`
- **False Positive Rate (FPR)**: `0.4462` (44.62%)

### Confusion Matrix
| Metric | Value |
|:---|:---|
| **True Negatives (Correctly identified unrecoverable)** | 576 |
| **False Positives (Wasted retries/notifications prevented)** | 464 |
| **False Negatives (Missed opportunities)** | 240 |
| **True Positives (Successfully identified recoverable)** | 1,720 |

---

## 3. Financial Recovery Benchmark vs. Baseline
| Metric | Baseline ('Always Retry Once') | RecoverAI Autonomous System | Delta / Impact |
|:---|:---|:---|:---|
| **Strategy** | Naive blind retry on attempt 1 | ML Scoring + AI Diagnosis + Policy Guardrails | Context-Aware Routing |
| **Recovered Revenue** | ₹10,428,561.11 | **₹16,366,824.55** | **+₹5,938,263.44** |
| **Recovery Rate** | 32.78% | **51.44%** | **+18.66%** |
| **Wasted Retries Avoided** | 0 | 803 transactions | Reduced Gateway Fees & Spam |
| **Human Escalation Rate** | 0.0% | 18.07% | High-value Safety Protection |
| **Stopped Case Rate** | 0.0% | 29.07% | Prevents Customer Fatigue |

---

## 4. Why RecoverAI Outperforms Naive Rules
1. **Intelligent Failure Distinction**: Differentiates between transient failures (`GATEWAY_ERROR` $ightarrow$ Delayed Retry) vs. permanent issues (`EXPIRED_CARD` $ightarrow$ Dynamic Payment Link).
2. **Policy Safeguards**: Never triggers unsolicited notifications to opted-out customers, and stops retrying on repetitive failures or high fraud scores.
3. **High-Value Protection**: Flags transactions exceeding merchant thresholds for Human Review rather than taking autonomous risks.
