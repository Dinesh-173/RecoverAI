# RecoverAI

> **"Detect. Decide. Recover."**
> *An AI-powered revenue recovery agent for modern merchants.*

Built for the **Razorpay AI Buildathon** — *AI Revenue Recovery Track*.

---

## 1. Executive Summary & Key Results

RecoverAI is an autonomous, policy-bounded revenue recovery platform engineered for merchants on Razorpay. It closes the critical revenue leakage loop by combining machine learning recoverability scoring, structured AI diagnostic reasoning, deterministic fintech policy guardrails, and bounded Razorpay Test Mode execution.

### Empirical Benchmark Results (Held-out 3,000 Transaction Test Set)
> [!IMPORTANT]
> All metrics below are empirically computed from our held-out test dataset (chronological split, zero data leakage). No fabricated or hardcoded results.

| Metric | Baseline Strategy ('Always Retry Once') | RecoverAI Autonomous System | Impact Delta / ROI |
|:---|:---|:---|:---|
| **Strategy** | Naive blind retry on attempt 1 | ML Recoverability + AI Diagnosis + Policy Guardrails | Context-Aware Routing |
| **Recovered Revenue** | ₹10,428,561.11 | **₹16,366,824.55** | **+₹5,938,263.44 (+56.94% Uplift)** |
| **Recovery Rate** | 32.78% | **51.44%** | **+18.66% percentage points** |
| **Wasted Retries Avoided** | 0 | **803 transactions** | Reduced Gateway Fees & Spam |
| **Human Escalation Rate** | 0.0% | **18.07%** | High-Value Safety Protection |
| **ML Model ROC-AUC** | N/A | **0.8332** | Precision: 78.75%, Recall: 87.76% |

---

## 2. System Architecture

```mermaid
flowchart TD
    subgraph Signal["1. Revenue Signal Ingestion"]
        RP_WH["Razorpay Webhook (payment.failed)"] --> WH_Endpoint["POST /webhooks/razorpay"]
        WH_Endpoint --> WH_Verify{"HMAC-SHA256 & Idempotency Check"}
        WH_Verify -- Valid & New --> EVT_Queue["Async Background Worker"]
        WH_Verify -- Duplicate --> IGNORE["HTTP 200 (DUPLICATE_IGNORED)"]
        WH_Verify -- Invalid --> REJECT["HTTP 400 (Bad Signature)"]
        EVT_Queue --> TX_Service["Transaction Service"]
    end

    subgraph Intelligence["2. ML & AI Diagnostic Pipeline"]
        ML_Model["ML Recoverability Model (Gradient Boosting)"]
        AI_Agent["AI Diagnostic Agent (LLMProvider Abstraction)"]
        Fallback["Deterministic Rule Fallback Engine"]
        
        TX_Service --> ML_Model
        ML_Model -->|Probability & Recovery Score| AI_Agent
        AI_Agent -->|Timeout / Malformed JSON| Fallback
    end

    subgraph Governance["3. Deterministic Policy Guardrails"]
        Policy["Deterministic Policy Engine"]
        AI_Agent -->|Structured Proposal (JSON)| Policy
        Fallback -->|Deterministic Proposal| Policy
        
        Policy --> RuleCheck{"Policy Rules & Limits Check"}
        RuleCheck -- Exceeds High Value / Low Confidence --> WAITING["WAITING_APPROVAL (Human Review)"]
        RuleCheck -- Opt-out / Max Retries / Low Score --> STOP["STOP_RECOVERY (Halt Action)"]
        RuleCheck -- Permitted --> APPROVED["APPROVED (Execute Action)"]
    end

    subgraph HumanOps["4. Merchant Operations"]
        Dashboard["Next.js Operations Dashboard"]
        WAITING --> Dashboard
        Dashboard -->|Merchant Authorize / Reject| HumanAction["POST /api/v1/recovery-cases/:id/approve"]
        HumanAction --> APPROVED
    end

    subgraph Execution["5. Bounded Action Execution"]
        Exec["Action Executor"]
        APPROVED --> Exec
        
        AdapterChoice{"Mode"}
        Exec --> AdapterChoice
        AdapterChoice -- Test Mode Active --> RP_Test["Razorpay Test Adapter (rzp_test_*)"]
        AdapterChoice -- Offline Demo Mode --> SIM_Adapter["Simulation Payment Adapter"]
    end

    subgraph Audit["6. Observability & Audit"]
        AuditTrail["Immutable Audit Ledger (Correlation IDs)"]
        Exec --> AuditTrail
        Exec --> DB[(PostgreSQL / SQLite)]
        DB --> Dashboard
    end
```

---

## 3. Technology Stack

- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, Lucide Icons, Recharts
- **Backend API**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0 (Async)
- **Database**: PostgreSQL (with aiosqlite zero-dependency local development support)
- **Machine Learning**: Scikit-Learn (Gradient Boosting), Pandas, NumPy, Joblib
- **AI Diagnostics**: LLMProvider abstraction (Google Gemini 2.0 Flash, OpenAI, Deterministic Mock)
- **Payments Integration**: Razorpay Test Mode APIs (`/v1/payment_links`, `/v1/orders`, `/v1/payments`) + Offline Simulation Adapter

---

## 4. Non-Negotiable Safety & Fintech Guardrails

1. **Test Mode Only**: Uses only `rzp_test_*` credentials. Never touches or stores live credentials.
2. **AI Never Directly Executes**: LLM generates structured Pydantic proposals; the Deterministic Policy Engine decides whether actions are authorized.
3. **Customer Opt-Out Enforcement**: Unsolicited SMS/WhatsApp notifications to opted-out customers are unconditionally blocked.
4. **Retry Bounds**: Halts recovery after reaching merchant retry limits to avoid customer fatigue.
5. **High-Value Protection**: Payments exceeding ₹10,000 are automatically escalated to human merchant operations.
6. **Webhook Idempotency**: Unique `razorpay_event_id` database index guarantees zero duplicate transactions.
7. **Prompt Injection Hardening**: All customer metadata is isolated in XML tags and treated as untrusted text.

---

## 5. Local Setup & Quickstart Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Clone & Configure Environment
```bash
git clone https://github.com/Dinesh-173/RecoverAI.git
cd RecoverAI

# Copy safe default environment configuration
cp .env.example .env
```

### 2. Backend Setup & Seed Data
```bash
# Install Python backend dependencies
pip install -r backend/requirements.txt

# Run ML training pipeline
python -m ml.models.train

# Run empirical evaluation benchmarks
python -m evaluation.generate_report

# Seed deterministic database (SEED=42)
python -m scripts.seed_data

# Start FastAPI backend server (Port 8000)
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open **`http://localhost:3000`** in your browser.

---

## 6. Running Tests & Quality Gate

```bash
# Run complete test suite (Unit, Policy, Fallback, Security, Integration)
python -m pytest backend/tests -v
```

---

## 7. Predefined Simulation Scenarios (1-Click Demo)

The dashboard includes a dedicated **Recovery Simulation Runner** (`/simulation`) featuring 5 canonical scenarios:
1. **Scenario 1 (High-Value VIP)**: A ₹45,000 transaction with temporary failure $\rightarrow$ Escalated to Human Approval Queue.
2. **Scenario 2 (Transient Timeout)**: A ₹1,499 UPI failure with bank downtime $\rightarrow$ Scheduled for 45-minute delayed retry.
3. **Scenario 3 (Repeated Failure)**: Attempt 3 failure $\rightarrow$ Stopped by policy engine to prevent fatigue.
4. **Scenario 4 (Privacy Opt-Out)**: Customer opted out of communication $\rightarrow$ Notification blocked by policy.
5. **Scenario 5 (Security / Fraud Block)**: Issuer fraud block $\rightarrow$ Halted immediately with zero retry.

---

## 8. Project Limitations

1. **Synthetic Data**: Trained on 20,000 synthetically generated correlated transaction records; real-world merchant deployment will benefit from continuous online learning.
2. **Test Mode Sandbox**: Razorpay Test Mode simulates authorization responses; physical bank settlement is simulated in test environments.
3. **Simplified Policy Schema**: Enterprise deployments may require custom policy rules per merchant subsidiary.

---

## 9. Documentation Index

- [Architecture & Sequence Diagrams](docs/architecture.md)
- [Security & Fintech Compliance](docs/security.md)
- [Empirical Evaluation & Methodology](docs/evaluation.md)
- [Product Strategy & ROI Model](docs/product.md)
- [Architecture Decision Records (ADRs)](docs/decisions.md)
- [5-Minute Pitch Script](docs/pitch.md)
- [Technical Interview Preparation](docs/interview.md)