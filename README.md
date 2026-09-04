# RecoverAI

> **Autonomous, policy-governed payment failure recovery engine for modern payment gateways and high-volume merchants.**

[![Build & Tests](https://img.shields.io/badge/tests-203%20passed-success?style=flat-square&logo=pytest)](tests/)
[![Assistant Tests](https://img.shields.io/badge/assistant%20tests-41%20passed-success?style=flat-square&logo=probot)](tests/test_assistant_comprehensive.py)
[![Next.js](https://img.shields.io/badge/frontend-Next.js%2014-black?style=flat-square&logo=next.js)](frontend/)
[![FastAPI](https://img.shields.io/badge/backend-FastAPI%200.110-009688?style=flat-square&logo=fastapi)](backend/)
[![Python](https://img.shields.io/badge/python-3.11+-blue?style=flat-square&logo=python)](backend/)
[![ML Model](https://img.shields.io/badge/ML-GradientBoosting%20(ROC--AUC%200.8332)-orange?style=flat-square&logo=scikit-learn)](ml/)
[![Checkpoint](https://img.shields.io/badge/checkpoint-202cf9e-blueviolet?style=flat-square&logo=git)](https://github.com/Dinesh-173/RecoverAI)

---

## What is RecoverAI?

**RecoverAI** is an autonomous revenue recovery and payment protection system designed for payment gateways (such as Razorpay) and digital merchants.

When digital transactions fail due to bank downtime, network timeouts, or customer friction, standard systems typically face a dilemma: either abandon the transaction (causing merchant churn and customer drop-off) or blindly retry it (causing duplicate debit risks, bank rate-limiting, and network penalties).

RecoverAI solves this by coupling **predictive machine learning** and **AI failure diagnosis** with a **deterministic policy engine**:

1. **Predictive Recovery Scoring:** An engineered machine learning model predicts whether a failed payment is realistically recoverable based on gateway telemetry, historical customer behaviour, and failure categorization.
2. **AI Diagnostic Agent:** An LLM-powered diagnostic agent evaluates the failure context and synthesizes an optimal recovery strategy (e.g., smart backoff retry, alternative payment link via WhatsApp/SMS, or customer engagement).
3. **Deterministic Policy Governance:** A strict, non-bypassable 8-rule deterministic policy engine checks every proposed action against hard business boundaries—such as retry bounds, customer communication opt-outs, and a ₹10,000 dual-control approval threshold—before any action can be dispatched.

> [!IMPORTANT]
> **Safety Invariant:** In RecoverAI, AI models have **zero direct execution authority**. The AI acts strictly as an advisory diagnostic agent. All execution permissions are enforced by deterministic code, backed by an immutable audit trail.

---

## 🚀 At a Glance

| Dimension | Implementation Details | Verified Status |
| :--- | :--- | :--- |
| **Frontend** | Next.js 14 (App Router), TypeScript, Tailwind CSS, Recharts, Lucide Icons | Production build clean (`11 routes`) |
| **Backend** | Python 3.11+, FastAPI 0.110, Pydantic v2, SQLAlchemy 2.0 (Async) | 203/203 unit & integration tests pass |
| **Database** | PostgreSQL 15 (Production) / SQLite via `aiosqlite` (Zero-setup Dev) | 10 relational tables, async connection pool |
| **Machine Learning** | `GradientBoostingClassifier` (`scikit-learn`), 17 engineered features | **ROC-AUC: 0.8332**, Precision: 78.75%, Recall: 87.76% |
| **AI Diagnostics** | Multi-provider abstraction (Google Gemini, OpenAI, Deterministic Fallback) | Structured Pydantic outputs, zero execution rights |
| **Intelligence Assistant** | Natural-language FinTech copilot with read-only database tools | 41/41 security & routing tests pass |
| **Policy Governance** | 8 sequential deterministic rules, dual-control human approval $\ge ₹10,000$ | 100% code-enforced, non-bypassable |
| **Simulation** | Cryptographically isolated sandbox (`is_simulation=True`), one-click reset | Metrics exclusion, live data protected |
| **Payment Integration** | Razorpay Test Sandbox (`rzp_test_*`) + Offline Simulation Adapter | Strict test-key verification |
| **Release Checkpoint** | `202cf9e` (`feat: finalize production UI and deployment readiness`) | Clean working tree on `fix/demo-bugs` |

---

## 💡 The Problem

In digital commerce and subscription businesses, **2% to 5% of gross merchandise value (GMV)** is lost to payment failures.

```text
       Payment Initiated
              │
              ▼
   ❌ PAYMENT FAILS (Timeout / Downtime / Friction)
              │
      ┌───────┴───────────────────────────────┐
      ▼                                       ▼
Traditional Trap 1:                     Traditional Trap 2:
"Abandon Payment"                       "Blind Immediate Retries"
- Lost revenue                          - Hits unresponsive bank switches
- Customer drop-off & churn             - Causes duplicate charge complaints
- Frustrated merchant operations        - Violates card network retry limits
```

1. **Uncoordinated Retries:** Blindly retrying cards or UPI handles when a core banking switch is down wastes gateway fees and risks card network blacklisting.
2. **One-Size-Fits-All Approach:** A technical timeout requires an intelligent delay; an expired card or dropped OTP page requires reaching out to the customer with an alternative payment link. Traditional systems treat all failures identically.
3. **Black-Box AI Risk:** Autonomous systems that grant unconstrained execution rights to probabilistic LLMs risk hallucinations, financial double-debits, and compliance violations.

---

## 🧠 The Solution

RecoverAI introduces an end-to-end recovery operating system that balances intelligent recovery with deterministic financial safety:

```mermaid
flowchart TD
    A[Payment Failure Event] --> B[HMAC-Verified Webhook Ingestion]
    B --> C[Feature Engineering & ML Scoring]
    C -->|Recovery Probability & Score| D[AI Diagnostic Agent]
    D -->|Structured Recovery Proposal| E{Deterministic Policy Engine}

    E -- Exceeds High Value >= ₹10k or Low Confidence --> F[Dual-Control Human Approval Queue]
    E -- Opt-Out / Max Retries / Low Score --> G[Halt Recovery / STOPPED]
    E -- Permitted --> H[Recovery Action Execution]

    F -->|Operator Sign-Off| H
    H --> I[Payment Adapter / Notification Link]
    I --> J[Outcome Capture & Status Update]
    J --> K[Tamper-Evident Audit Ledger]
    J --> L[Real-Time Analytics & Financial Metrics]
```

### Measured Recovery Benchmark (Held-out 3,000 Transaction Test Set)

Evaluated against a test population of 3,000 failed transactions representing **₹31,815,249.85 revenue at risk**:

| Strategy | Recovered Revenue | Recovery Rate | Net Revenue Uplift | Wasted Retries Avoided |
| :--- | :--- | :--- | :--- | :--- |
| **Baseline ("Blind Retry Once")** | ₹10,428,561.11 | 32.78% | Baseline Reference | 0 retries saved |
| **RecoverAI Autonomous** | **₹16,366,824.55** | **51.44%** | **+₹5,938,263.44 (+56.94%)** | **803 retries avoided** |

---

## ✨ Core Features

### 📊 Operations Dashboard
- Real-time visibility into **Revenue at Risk**, **Recovered Revenue**, **Recovery Rate**, and **Active Cases**.
- 7-day recovery trend curves and failure breakdowns by payment method and gateway.
- System operational health indicator and demo sandbox banner.

### 💳 Transaction Explorer
- Searchable transaction ledger with filters for payment method, gateway, error codes, and live vs. simulated records.
- Inspects granular error reasons (e.g., `GATEWAY_TIMEOUT`, `INSUFFICIENT_FUNDS`, `BANK_DOWNTIME`).

### 🔄 Recovery Cases Hub & Detail View
- Multi-state workflow tracking (`ACTIVE`, `WAITING_APPROVAL`, `RECOVERED`, `FAILED`, `STOPPED`).
- Chronological timeline tracking every retry, customer notification, and state transition.
- Interactive **AI Diagnostic Modal** detailing the ML score, model confidence, and strategy rationale.

### 👤 Dual-Control Human Approvals
- Built-in two-man rule for high-value recoveries ($\ge ₹10,000$) or low-confidence AI proposals ($< 0.70$).
- Operators inspect failure context, customer LTV, and risk scores before clicking **Approve** or **Reject**.

### 📈 Recovery Analytics Studio
- Financial performance comparison between autonomous recovery and baseline blind retries.
- Method-wise recovery breakdown (UPI vs. Credit Card vs. Netbanking vs. Debit Card).
- Hourly recovery success heatmaps and error distribution analytics.

### 📝 Tamper-Evident Audit Logs
- Immutable append-only audit trail logging every system transition, ML inference, AI proposal, policy check, and operator decision.
- Formatted JSON payload diffs displaying exact state changes with user/actor attribution.

### 💬 Intelligence Assistant (FinTech Copilot)
- Context-aware natural-language assistant accessible across all dashboard pages.
- Executes read-only database tools to inspect transactions, explain case status, and analyze metrics.
- Hardened against prompt injection, system prompt extraction, and unauthorized mutation requests.

### 🧪 Scenario Simulation Engine
- Sandbox for injecting realistic failure scenarios (Bank Outage, Card Expiry Spike, UPI Timeout).
- Custom transaction builder to test arbitrary amounts, payment methods, and error conditions.
- Safe reset endpoint (`POST /api/v1/simulation/reset`) that purges test records without touching live data.

### 🔗 Webhook Ingestion Engine
- Ingests real-time payment gateway failure events (`payment.failed`).
- Cryptographic HMAC-SHA256 signature verification and database idempotency keys.

---

## 🤖 AI & Machine Learning

### 1. Machine Learning Model Pipeline

```text
Raw Transaction Data
  ├── Amount, Payment Method, Gateway, Error Category
  ├── Customer LTV, Historical Success/Failure Counts
  └── Rolling 1h Gateway Success Rate, Hour of Day, Day of Week
              │
              ▼
   ml/features/engineer.py (17 Features)
   StandardScaler (13 numeric) + OneHotEncoder (4 categorical)
              │
              ▼
   ml/models/train.py (GradientBoostingClassifier)
   n_estimators=150, learning_rate=0.08, max_depth=4, subsample=0.85
              │
              ▼
   Model Artifact: ml/models/gradient_boosting.pkl
   Outputs: Recovery Probability (0.0 - 1.0) & Recovery Score (0 - 100)
```

- **Verified Evaluation Metrics:**
  - **ROC-AUC:** `0.8332`
  - **Precision:** `78.75%` (minimizes wasted gateway fees on unrecoverable failures)
  - **Recall:** `87.76%` (captures the vast majority of recoverable transactions)
  - **F1 Score:** `0.8301`
- **Fallback Resilience:** If the model artifact cannot be read, `RiskAssessmentService` automatically falls back to an algorithmic heuristic (`fallback_heuristic_v1`), ensuring zero downtime.

### 2. AI Diagnostic Agent

The AI Diagnostic Agent (`backend/app/services/diagnostic_agent.py`) consumes transaction context, customer metadata, and ML recovery scores to formulate a structured strategy:

```python
class AgentDiagnosticOutput(BaseModel):
    recommended_action: Literal[
        "RETRY_PAYMENT",
        "CUSTOMER_NOTIFICATION",
        "HUMAN_REVIEW",
        "STOP_RECOVERY"
    ]
    recommended_delay_minutes: int = Field(ge=0, le=1440)
    recommended_channel: Optional[Literal["WHATSAPP", "SMS", "EMAIL", "IN_APP"]]
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str = Field(min_length=10, max_length=1000)
    requires_human_approval: bool
```

- **LLM Abstraction:** Supports Google Gemini (`gemini-2.0-flash` / `gemini-1.5-pro`), OpenAI (`gpt-4o`), or an offline deterministic fallback engine.
- **Strict Boundary:** The LLM's proposal is strictly an input to the Policy Engine. It has **no database mutation privileges and no direct gateway access**.

---

## 🛡️ Policy & Safety (Deterministic Governance)

The Policy Engine (`backend/app/policies/engine.py`) enforces **8 sequential, deterministic rules**. It evaluates top-to-bottom and halts on the first violation or escalation:

```text
[Rule 1: ACTION_WHITELIST_CHECK]
  └─ Action must be in {RETRY_PAYMENT, CUSTOMER_NOTIFICATION, HUMAN_REVIEW, STOP_RECOVERY}
     ↳ Fail: BLOCKED (INVALID_ACTION_TYPE)

[Rule 2: STATUS_ELIGIBILITY_RULE]
  └─ Transaction current status must be "FAILED"
     ↳ Fail: BLOCKED (TRANSACTION_NOT_ELIGIBLE)

[Rule 3: CUSTOMER_OPT_OUT_RULE]
  └─ If customer has communication_opt_out == True and action is CUSTOMER_NOTIFICATION
     ↳ Triggered: BLOCKED (CUSTOMER_COMMUNICATION_OPT_OUT)

[Rule 4: MAX_RETRY_LIMIT_RULE]
  └─ If retry attempt_number >= merchant_policy.max_retries (default 2)
     ↳ Triggered: STOPPED (MAX_RETRIES_EXCEEDED) -> Target: STOP_RECOVERY

[Rule 5: RECOVERY_STOP_CONFIRMED]
  └─ If proposed action is STOP_RECOVERY
     ↳ Triggered: STOPPED (RECOVERY_TERMINATED_BY_POLICY)

[Rule 6: HIGH_VALUE_THRESHOLD_RULE]
  └─ If transaction amount >= merchant_policy.high_value_threshold (default ₹10,000.00)
     ↳ Triggered: ESCALATED_HUMAN_APPROVAL -> Target: WAITING_APPROVAL

[Rule 7: MIN_CONFIDENCE_RULE]
  └─ If AI confidence < min_confidence (default 0.70) or requires_human_approval == True
     ↳ Triggered: ESCALATED_HUMAN_APPROVAL -> Target: WAITING_APPROVAL

[Rule 8: MIN_RECOVERY_SCORE_RULE]
  └─ If ML recovery_score < min_recovery_score (default 15.0)
     ↳ Triggered: STOPPED (RECOVERY_SCORE_BELOW_THRESHOLD)

[FALLBACK: APPROVED]
  └─ All safety checks passed -> APPROVED for execution
```

---

## 💬 Intelligence Assistant

The Intelligence Assistant (`backend/app/services/assistant_service.py`) is an operations copilot for merchant risk and finance teams:

```text
User Query: "Why was case RC-1049 escalated to human review?"
                     │
                     ▼
+─────────────────────────────────────────────────────────────+
|               LAYER 1: SECURITY SHIELDS                     |
| - Prompt Injection Detection: Rejects override patterns    |
| - System Prompt Shield: Blocks internal prompt leaks        |
| - Mutation Blocker: Refuses write/approval requests         |
+─────────────────────────────────────────────────────────────+
                     │
                     ▼
+─────────────────────────────────────────────────────────────+
|               LAYER 2: INTENT CLASSIFICATION                |
| Routes to: TRANSACTION | RECOVERY_CASE | POLICY | ANALYTICS |
+─────────────────────────────────────────────────────────────+
                     │
                     ▼
+─────────────────────────────────────────────────────────────+
|               LAYER 3: READ-ONLY TOOL CALLS                 |
| - get_transaction_details(id)                               |
| - get_recovery_case_summary(id)                             |
| - get_recent_audit_trail(id)                                |
| - get_dashboard_summary()                                   |
+─────────────────────────────────────────────────────────────+
                     │
                     ▼
+─────────────────────────────────────────────────────────────+
|               LAYER 4: FACT-GROUNDED RESPONSE               |
| Answers strictly from retrieved DB context with citations.   |
+─────────────────────────────────────────────────────────────+
```

- **What it CAN do:** Explain failure reasons, detail policy rule triggers, summarize audit histories, and calculate operational KPIs.
- **What it CANNOT do:** Execute payments, modify policies, approve escalated cases, or bypass security rules. When asked to approve a case, it safely redirects the user to `/approvals`.

---

## 🏗️ Architecture

```mermaid
flowchart TD
    subgraph Client["Frontend Client (Next.js 14)"]
        UI_Dash["Dashboard & Explorer"]
        UI_Appr["Approvals Queue"]
        UI_Sim["Scenario Simulator"]
        UI_Asst["Intelligence Assistant"]
    end

    subgraph API["Backend API (FastAPI)"]
        Router["API Router (v1)"]
        Auth_CORS["CORS & HMAC Signature Verification"]
    end

    subgraph Services["Core Application Services"]
        TxService["Transaction Service"]
        RiskService["Risk Assessment Service"]
        DiagAgent["Diagnostic Agent"]
        PolicyEng["Deterministic Policy Engine"]
        RecEngine["Recovery Engine"]
        AsstService["Assistant Service"]
        AuditService["Audit Service"]
        SimService["Simulation Service"]
    end

    subgraph Persistence["Database & Storage"]
        DB[(PostgreSQL / SQLite)]
        ModelStore["ML Model Store (joblib)"]
    end

    subgraph External["External Adapters"]
        RZP_Test["Razorpay Test Adapter (rzp_test_*)"]
        SimAdapter["Simulation Payment Adapter"]
    end

    Client -->|HTTP / JSON| Router
    Router --> Auth_CORS
    Auth_CORS --> Services

    RiskService --> ModelStore
    DiagAgent --> Services
    PolicyEng --> Services
    RecEngine --> External
    Services --> DB
```

---

## 🧰 Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | Next.js 14.2.24 (App Router), React 18, TypeScript, Tailwind CSS 3.4, Recharts, Lucide React |
| **Backend API** | Python 3.11+, FastAPI 0.110.0, Uvicorn, Pydantic v2 |
| **ORM & Migrations** | SQLAlchemy 2.0 (Async), Alembic migrations |
| **Database** | PostgreSQL 15 (`asyncpg`) for production; SQLite (`aiosqlite`) for zero-setup local dev |
| **Machine Learning** | `scikit-learn` (`GradientBoostingClassifier`), Pandas, NumPy, Joblib |
| **AI / LLM Providers** | Google Gemini (`google-generativeai`), OpenAI API, Deterministic Offline Mock |
| **Payment Gateway** | Razorpay Test Mode API (`/v1/orders`, `/v1/payments`, `/v1/payment_links`), HMAC SHA-256 |
| **Containerization** | Multi-stage Dockerfiles, Docker Compose |
| **Testing** | `pytest`, `pytest-asyncio`, `httpx` (203 backend tests, 41 assistant tests) |

---

## 🗄️ Data Model

The schema consists of **10 relational tables** designed for complete financial auditability:

```text
merchants ──────────────< merchant_policies
    │
    ▼
customers
    │
    ▼
transactions ───────────< revenue_risk_assessments (ML scores)
    │
    ├───────────────────< recovery_cases
    │                         │
    │                         └───< recovery_actions (Execution attempts)
    │
    ├───────────────────< audit_logs (Append-only state diffs)
    │
    └───────────────────< webhook_events (Idempotency & payload log)
```

- **`transactions`:** The central financial ledger with immutable `initial_status` to prevent metric drift.
- **`revenue_risk_assessments`:** Persists model version, recovery probability, and risk tiers.
- **`recovery_cases`:** State machine managing recovery progression, current stage, and resolution.
- **`recovery_actions`:** Append-only log of every retry, WhatsApp payment link, or SMS message dispatched.
- **`audit_logs`:** Tamper-evident ledger recording all state transitions across every entity.

---

## 🔐 Security

### Implemented Security Mechanisms
- **HMAC-SHA256 Webhook Verification:** Incoming webhooks from payment gateways are cryptographically verified using the merchant's secret key.
- **Dual-Control Human Oversight:** Financial recoveries $\ge ₹10,000$ or low-confidence recommendations ($< 0.70$) cannot execute autonomously; they mandate operator approval.
- **SQL Injection Defense:** All database interactions are parameterized through SQLAlchemy 2.0 ORM queries.
- **Strict Input Validation:** All API request payloads and query parameters are strictly validated via Pydantic v2 models.
- **Prompt Injection Defense:** Assistant input is sanitized against override patterns, and customer metadata is isolated in XML blocks.
- **Test-Key Enforcement:** In active mode, the Razorpay adapter verifies that credentials begin with `rzp_test_`, refusing live production keys.
- **Simulation Data Isolation:** Simulated transactions are strictly tagged (`is_simulation=True`) and excluded from production metrics.

### Recommended Future Production Enhancements
- Multi-tenant Row-Level Security (RLS) policies at the PostgreSQL database layer.
- Enterprise SSO integration via OAuth2 / OIDC.
- Dedicated hardware security module (HSM) or AWS KMS for webhook secret encryption.

---

## 🧪 Simulation Mode

RecoverAI includes a dedicated simulation environment allowing merchants to stress-test their recovery strategies:

- **Strict Data Isolation:** Every simulated transaction, case, action, and risk assessment has `is_simulation = True`.
- **Protected Financial Metrics:** All dashboard and analytics queries enforce `WHERE is_simulation = FALSE`. Live metrics are never polluted.
- **Gateway Decoupling:** In simulation mode, payment retries are routed to the in-memory `SimulationPaymentAdapter`. No external API calls are made.
- **One-Click Sandbox Reset:** `POST /api/v1/simulation/reset` purges all simulated rows while keeping live transaction records intact.

---

## 📈 Recovery Analytics

RecoverAI calculates financial impact using verified formulas that eliminate mathematical distortion:

$$\text{Revenue at Risk} = \sum_{\substack{\text{initial\_status} = \text{"FAILED"} \\ \text{is\_simulation} = \text{False}}} \text{amount}$$

$$\text{Recovered Revenue} = \sum_{\substack{\text{initial\_status} = \text{"FAILED"} \\ \text{status} = \text{"SUCCESS"} \\ \text{is\_simulation} = \text{False}}} \text{amount}$$

$$\text{Recovery Rate} = \begin{cases}
0.00\% & \text{if } \text{Revenue at Risk} = 0 \\
\left( \frac{\text{Recovered Revenue}}{\text{Revenue at Risk}} \right) \times 100 & \text{otherwise}
\end{cases}$$

> [!TIP]
> **Resolution of Denominator Drift:** When a failed payment recovers, naive systems change its status to `SUCCESS`, shrinking the at-risk denominator and distorting the recovery percentage. RecoverAI records immutable `initial_status = "FAILED"` at creation, ensuring the mathematical denominator remains stable.

---

## 🔌 API Overview

FastAPI provides an interactive OpenAPI / Swagger specification at **`http://localhost:8000/docs`**.

| Route Prefix | Purpose | Key Endpoints |
| :--- | :--- | :--- |
| `/health` | Health Check | `GET /health` |
| `/api/v1/dashboard` | Executive KPIs | `GET /api/v1/dashboard/metrics` |
| `/api/v1/transactions` | Transaction Ledger | `GET /api/v1/transactions`, `POST /api/v1/transactions`, `GET /api/v1/transactions/{id}` |
| `/api/v1/recovery-cases` | Case Management | `GET /api/v1/recovery-cases`, `GET /api/v1/recovery-cases/{id}`, `POST .../analyze`, `POST .../execute` |
| `/api/v1/approvals` | Human Governance | `GET /api/v1/approvals/pending`, `POST .../approve`, `POST .../reject` |
| `/api/v1/analytics` | Strategic BI | `GET /api/v1/analytics/overview` |
| `/api/v1/evaluation` | Model Benchmarks | `GET /api/v1/evaluation/results` |
| `/api/v1/audit-logs` | Compliance Trail | `GET /api/v1/audit-logs` |
| `/api/v1/simulation` | Sandbox Runner | `POST /api/v1/simulation/run`, `POST /api/v1/simulation/custom`, `POST /api/v1/simulation/reset` |
| `/api/v1/assistant` | FinTech Copilot | `POST /api/v1/assistant/chat` |
| `/webhooks` | Gateway Receiver | `POST /webhooks/razorpay` (HMAC SHA-256 verified) |

---

## 📁 Project Structure

```text
RecoverAI/
├── backend/
│   ├── app/
│   │   ├── api/v1/                 # 8 API routers (transactions, recovery, analytics, etc.)
│   │   ├── db/                     # Async SQLAlchemy session and declarative base
│   │   ├── models/                 # 10 SQLAlchemy ORM models
│   │   ├── schemas/                # Pydantic v2 request/response contracts
│   │   ├── services/               # Core business logic (ML, Agent, Policy, Recovery)
│   │   ├── policies/               # Deterministic Policy Engine (8 rules)
│   │   ├── main.py                 # FastAPI application & CORS configuration
│   │   └── config.py               # Pydantic BaseSettings environment manager
│   ├── alembic/                    # Database migrations
│   ├── Dockerfile                  # Backend production Dockerfile
│   └── requirements.txt            # Python dependencies
├── frontend/
│   ├── app/                        # Next.js 14 App Router (11 verified routes)
│   │   ├── dashboard/              # Executive KPI dashboard
│   │   ├── transactions/           # Transaction explorer
│   │   ├── recovery-cases/         # Case workflow list & [id] detail views
│   │   ├── approvals/              # Dual-control human approval queue
│   │   ├── analytics/              # Recovery BI charts
│   │   ├── audit-logs/             # Compliance audit ledger
│   │   ├── simulator/              # Failure simulation runner
│   │   └── evaluation/             # Model benchmark charts
│   ├── components/
│   │   ├── assistant/              # Intelligence Assistant drawer component
│   │   ├── layout/                 # Sidebar, Header, Navigation
│   │   └── ui/                     # Cards, Badges, Modals, Buttons
│   ├── lib/                        # API client (lib/api.ts) & utility helpers
│   ├── Dockerfile                  # Next.js standalone Dockerfile
│   └── package.json                # Frontend dependencies
├── ml/
│   ├── features/                   # Feature extraction & engineering pipeline
│   ├── models/                     # Training script (train.py) & serialized model (.pkl)
│   └── data/                       # Dataset generation scripts
├── evaluation/                     # Verified benchmark evaluation artifacts (.json)
├── tests/                          # 203 backend tests + 41 assistant tests
├── docs/                           # Architecture, security, and interview documentation
├── docker-compose.yml              # Multi-tier containerized production setup
└── README.md                       # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.10+** (Python 3.11 recommended)
- **Node.js 18+** and **npm**
- *(Optional)* **Docker & Docker Compose**

### 1. Clone the Repository
```bash
git clone https://github.com/Dinesh-173/RecoverAI.git
cd RecoverAI
```

### 2. Backend Setup
```bash
# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
# source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Seed initial demonstration data (42 seed)
python -m scripts.seed_data

# Start backend server (Port 8000)
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Frontend Setup
```bash
# In a new terminal:
cd frontend

# Install dependencies
npm install

# Start Next.js development server (Port 3000)
npm run dev
```

Open **`http://localhost:3000`** in your browser.

---

## ⚙️ Environment Variables

Create a `.env` file in the project root:

```ini
# Environment
ENVIRONMENT=development
PORT=8000
HOST=127.0.0.1

# Database (defaults to zero-setup SQLite; use postgresql+asyncpg:// in production)
DATABASE_URL=sqlite+aiosqlite:///./recoverai.db
SYNC_DATABASE_URL=sqlite:///./recoverai.db

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Operational Mode (true = offline demo mode; false = active test-mode recovery)
DEMO_MODE=true

# Razorpay Test Credentials (only required if DEMO_MODE=false)
RAZORPAY_KEY_ID=rzp_test_yourkey
RAZORPAY_KEY_SECRET=your_secret
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret

# AI Diagnostic Provider (mock, gemini, openai)
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
LLM_MODEL=gemini-2.0-flash
```

---

## 🐳 Docker Deployment

RecoverAI includes a fully configured `docker-compose.yml` supporting PostgreSQL 15, FastAPI, and Next.js:

```bash
# 1. Build container images
docker compose build

# 2. Launch services in detached mode
docker compose up -d

# 3. Verify service health
docker compose ps
curl -f http://localhost:8000/health
```

Access the frontend at **`http://localhost:3000`** and backend docs at **`http://localhost:8000/docs`**.

---

## 🧪 Testing

The repository maintains an automated, non-destructive test suite:

```bash
# Run all backend unit & integration tests (203 tests)
python -m pytest -v

# Run the comprehensive Intelligence Assistant test suite (41 tests)
python -m pytest tests/test_assistant_comprehensive.py -v

# Verify frontend production build
cd frontend && npm run build
```

**Last Verified Status:**
- **Backend Tests:** `203 passed` (100% pass rate)
- **Assistant Tests:** `41 passed` (Prompt injection, routing, tool boundary verification)
- **Frontend Build:** `Passed` (11 static/server routes compiled with zero errors)
- **Browser Automation:** Verified across 4 viewports (Desktop, Laptop, Tablet, Mobile) with zero console errors.

---

## 🎬 Demo Flow (60-Second Walkthrough)

1. **Dashboard (`/dashboard`):** Review real-time KPIs showing ₹45.2M revenue at risk and a 51.4% recovery rate.
2. **Transaction Explorer (`/transactions`):** Identify a high-value failed payment (e.g., ₹12,500 due to a UPI timeout).
3. **Recovery Case (`/recovery-cases/[id]`):** Open the case detail view. Click the **AI Diagnostic Explanation** modal to see the 88% recovery probability and recommended retry backoff.
4. **Human Governance (`/approvals`):** Observe that the case is paused in `WAITING_APPROVAL`. The Policy Engine intercepted autonomous execution because Rule 6 mandates dual-control approval for transactions $\ge ₹10,000$.
5. **Operator Sign-Off:** Click **Approve** in the Approvals queue. The action executes, the payment status transitions to `SUCCESS`, and the recovered revenue increments.
6. **Audit Ledger (`/audit-logs`):** Inspect the newly generated immutable audit entry confirming operator approval and state change.
7. **Intelligence Assistant:** Open the floating copilot drawer and ask: *"Why was this case escalated?"* The assistant cites Rule 6 and explains the financial threshold.

---

## 🎯 Why RecoverAI Matters for Payment Gateways

For companies like **Razorpay**, failed payments are not just technical errors; they represent direct business loss:

1. **Top-Line Merchant Retention:** Merchants churn when conversion drops. Automating recovery of over 50% of failed revenue creates immediate stickiness.
2. **Maximized Gateway MDR:** Gateways earn transaction fees on captured volume. Recovering ₹16.3M across 3,000 transactions directly recaptures lost processing revenue.
3. **Smart Traffic Steering:** Rather than blindly pounding an impaired banking switch, RecoverAI reroutes recovery through healthy alternative rails (e.g., WhatsApp PayLinks).
4. **Network Compliance Protection:** Governed retries ensure merchants never exceed card network retry limits, preventing fines and acquiring-bank sanctions.

---

## ⭐ What Makes RecoverAI Different?

- **Dual-Architecture (Probabilistic + Deterministic):** Machine learning provides predictive scoring; deterministic code enforces non-negotiable safety rules.
- **Zero Hallucination Risk in Financial Execution:** The AI model is strictly an advisor. It cannot execute transactions or modify balances.
- **Mathematical Metric Integrity:** Preserves immutable initial failure status to prevent denominator drift.
- **Isolated Simulation:** Risk-free sandbox that mirrors production logic without touching live customer data or payment gateways.
- **Auditable & Explainable:** Every decision, retry, score, and operator approval is stamped into an append-only ledger.

---

## ⚠️ Current Limitations

- **Synthetic Training Data:** The model was trained on 20,000 synthetically generated records modeling real Razorpay failure patterns. Production rollout requires training on live gateway logs.
- **Test Mode Sandbox:** Payment execution interacts with Razorpay's Test Sandbox (`rzp_test_*`) or in-memory simulation adapters. Live bank transfers are blocked by design.
- **Single-Subsidiary Policy Model:** Current merchant policies are defined at the merchant root level. Multi-subsidiary policy inheritance is planned for future releases.
- **In-Memory Assistant Context:** The Intelligence Assistant currently maintains conversation state using an in-memory LRU cache. A horizontally scaled deployment would back this with Redis.

---

## 🗺️ Future Roadmap

- [ ] **Contextual Multi-Armed Bandits:** Dynamic backoff learning using reinforcement learning to adapt to real-time bank switch latency.
- [ ] **Distributed Task Queuing:** Celery / Redis Streams pipeline for processing 10,000+ webhook events per second.
- [ ] **TokenHQ Mandate Recovery:** Automated subscription retry optimization against recurring tokenized cards.
- [ ] **Merchant Slack/Teams Notifications:** Interactive approval requests dispatched directly to merchant risk channels.

---

## 📌 Project Status

```text
🟢 Git Checkpoint: 202cf9e (feat: finalize production UI and deployment readiness)
🟢 Working Tree: Clean (Branch: fix/demo-bugs)
🟢 Backend Test Suite: 203 / 203 Passed
🟢 Assistant Test Suite: 41 / 41 Passed
🟢 Frontend Production Build: Clean (11 routes compiled)
🟢 Database Support: PostgreSQL 15 & SQLite verified
🟢 Docker Configuration: Verified multi-tier build
```

---

## License

License: Not currently specified.

---

## Contributing

Contributions are welcome. Please open an issue to discuss proposed architectural changes before submitting a pull request. All submissions must pass the existing test suite:

```bash
python -m pytest
cd frontend && npm run build
```
