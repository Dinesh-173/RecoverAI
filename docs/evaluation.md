# RecoverAI Empirical Evaluation & Methodology

## 1. Methodology & Data Splitting
- **Dataset Size**: 20,000 synthetic transaction records with realistic correlations across payment rails (UPI, CARD, NETBANKING, WALLET) and failure types.
- **Split Strategy**: Chronological time-based split (70% Train = 14,000 records, 15% Validation = 3,000 records, 15% Held-out Test = 3,000 records).
- **Zero Leakage**: All performance benchmarks and metrics reported in RecoverAI are evaluated strictly on the 3,000 held-out test records.

---

## 2. Empirical ML Classifier Metrics
- **Model**: Gradient Boosting Classifier (`v1.0.0-gbm`)
- **ROC-AUC**: `0.8332`
- **Precision**: `78.75%`
- **Recall**: `87.76%`
- **F1 Score**: `83.01%`
- **False Positive Rate (FPR)**: `44.62%`

### Confusion Matrix (Test Split)
| Metric | Value | Meaning in Fintech Context |
|:---|:---|:---|
| **True Negatives (TN)** | `576` | Correctly identified unrecoverable payments; avoided spamming customer or incurring wasted gateway fees |
| **False Positives (FP)** | `464` | Attempted recovery on unrecoverable transaction |
| **False Negatives (FN)** | `240` | Missed recovery opportunity |
| **True Positives (TP)** | `1,720` | Correctly identified and recovered lost revenue |

---

## 3. Financial Benchmark vs. Baseline
| Metric | Baseline Strategy ('Always Retry Once') | RecoverAI Autonomous System | Delta / Financial Impact |
|:---|:---|:---|:---|
| **Strategy Formulation** | Blind retry of all first-attempt failures | ML Recoverability Scoring + AI Diagnostic Routing + Policy Guardrails | Context-Aware |
| **Recovered Revenue** | ₹10,428,561.11 | **₹16,366,824.55** | **+₹5,938,263.44 (+56.94% uplift)** |
| **Recovery Rate** | 32.78% | **51.44%** | **+18.66% percentage points** |
| **Wasted Retries Avoided** | 0 | **803 transactions** | Reduced Gateway Fees & Spam |
| **Human Escalation Rate** | 0.0% | **18.07%** | High-value Safety Protection |
| **Stopped Case Rate** | 0.0% | **26.77%** | Prevents Customer Fatigue |

---

## 4. Ablation & System Value Contribution
1. **Rule-Only System**: Simple static thresholds fail to capture customer historical reliability and transient vs permanent error nuances.
2. **ML-Only System**: Scores probability accurately but cannot generate human-readable diagnostic explanations or formulate dynamic delay schedules.
3. **AI-Agent Only**: Strong qualitative diagnosis, but prone to hallucinations or unsafe financial actions without guardrails.
4. **RecoverAI (ML + AI Agent + Policy Engine)**: Combines statistical scoring, contextual reasoning, and strict deterministic fintech guardrails.
