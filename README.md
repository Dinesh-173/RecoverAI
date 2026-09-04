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

## 5. Setup & Deployment Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- (Optional for Docker) Docker & Docker Compose

---

### A. Local Development Setup (Zero-Setup SQLite)

#### 1. Configure Environment
- **Windows (PowerShell)**:
  ```powershell
  Copy-Item .env.example .env
  ```
- **Linux / macOS (Bash)**:
  ```bash
  cp .env.example .env
  ```

#### 2. Install Dependencies & Seed Sample Data
```bash
# Install backend dependencies
pip install -r backend/requirements.txt

# Seed sample transactions and recovery cases (SEED=42)
python -m scripts.seed_data
```

#### 3. Start Development Servers
- **Option 1: Windows One-Click Quickstart**:
  ```powershell
  .\start-recoverai.ps1
  ```
- **Option 2: Manual Launch**:
  ```bash
  # Terminal 1: Backend API (Port 8000)
  python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

  # Terminal 2: Next.js Frontend (Port 3000)
  cd frontend
  npm run dev
  ```

Open **`http://localhost:3000`** in your browser.

---

### B. Production Deployment (PostgreSQL + Docker Compose)

The repository provides a fully containerized multi-tier deployment configuration.

#### 1. Production Environment Configuration
Set the following variables in `.env`:
```ini
ENVIRONMENT=production
PORT=8000
HOST=0.0.0.0

# Database: Use asyncpg for production PostgreSQL
DATABASE_URL=postgresql+asyncpg://<pg_user>:<pg_password>@<pg_host>:5432/<pg_db>
SYNC_DATABASE_URL=postgresql://<pg_user>:<pg_password>@<pg_host>:5432/<pg_db>

# CORS: Set exact merchant dashboard origin(s)
CORS_ORIGINS=https://app.yourdomain.com

# Razorpay Test Mode Credentials
RAZORPAY_KEY_ID=rzp_test_<your_key>
RAZORPAY_KEY_SECRET=<your_secret>
RAZORPAY_WEBHOOK_SECRET=<your_webhook_secret>

# AI / LLM Provider (mock, gemini, openai)
LLM_PROVIDER=gemini
GEMINI_API_KEY=<your_gemini_key>
LLM_MODEL=gemini-2.0-flash

# Operational Mode (false = active test-mode recovery, true = demo sandbox)
DEMO_MODE=false
```

> [!IMPORTANT]
> **API URL Configuration**: Next.js client bundles inline `NEXT_PUBLIC_*` variables at build time. When deploying frontend and backend on separate domains, supply `NEXT_PUBLIC_API_URL="https://api.yourdomain.com/api/v1"` during `npm run build`. For containerized deployments sharing a reverse proxy (e.g., NGINX, Cloudflare, or Traefik), route `/api/v1` to port 8000 and `/` to port 3000.

#### 2. Launch with Docker Compose
```bash
# Build production images
docker compose build

# Start services in detached mode
docker compose up -d

# Verify container health
docker compose ps
curl -f http://localhost:8000/health
```

#### 3. Standalone Production Build (Non-Docker)
```bash
# Backend (FastAPI + Uvicorn)
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Frontend (Next.js Production Bundle)
cd frontend
export NEXT_PUBLIC_API_URL="https://api.yourdomain.com/api/v1"
npm ci
npm run build
npm run start
```

---

## 6. Predefined & Custom Simulation Scenarios

The dashboard includes an **Autonomous Recovery Simulation Runner** (`/simulation`) with full support for:
1. **5 Canonical Demo Scenarios**:
   - **Scenario 1 (High-Value VIP)**: A ₹45,000 transaction with temporary failure $\rightarrow$ Escalated to Human Approval Queue (`WAITING_APPROVAL`).
   - **Scenario 2 (Transient Timeout)**: A ₹1,499 UPI failure with bank downtime $\rightarrow$ Scheduled for delayed retry (`SCHEDULED`).
   - **Scenario 3 (Repeated Failure)**: Attempt 3 failure $\rightarrow$ Stopped by Policy Engine to prevent fatigue (`STOPPED_BY_POLICY`).
   - **Scenario 4 (Privacy Opt-Out)**: Customer opted out $\rightarrow$ Notification blocked by Policy Engine (`STOPPED_BY_POLICY`).
   - **Scenario 5 (Security / Fraud Block)**: Issuer fraud block $\rightarrow$ Halted immediately with 0 retries (`STOPPED_BY_POLICY`).
2. **Custom CSV File Upload**: Upload custom datasets using the provided CSV template with full validation.
3. **Manual Form Entry**: Add, preview, and test custom failed transactions interactively.
4. **Historical Date Preservation & Range Filtering**: Historical transaction timestamps are preserved (`is_simulation=True`) with inclusive boundary filtering (`Start Date` / `End Date`).
5. **Simulation Reset Endpoint**: Execute `POST /api/v1/simulation/reset` to safely purge simulation records while preserving live production data.

---

## 7. Running Tests & Quality Gate

```bash
# Run complete test suite (Unit, Policy, Fallback, Security, Integration)
python -m pytest -v

# Run targeted Phase 16 custom data & date simulation tests
python -m pytest backend/tests/unit/test_phase16_custom_data_date_simulation.py -v
```

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
- [RecoverAI Intelligence Assistant Audit](docs/RECOVERAI_INTELLIGENCE_ASSISTANT_AUDIT.md)

---

## 10. RecoverAI Intelligence Assistant

RecoverAI includes an embedded, context-aware, tool-governed **Intelligence Assistant**:

- **Floating UI Copilot**: Accessible via the `🤖 RecoverAI AI` button on any screen.
- **Page Context Aware**: Automatically adapts explanations to the active screen (`/dashboard`, `/transactions`, `/recovery-cases/[id]`, `/simulation`, `/analytics`, `/approvals`, `/audit-logs`).
- **Controlled Tool Registry**: Reads live metrics, ML evaluation benchmarks (**ROC-AUC 0.8332**), Policy Engine rationales, and system health status.
- **FinTech Safety Invariant**: AI is strictly advisory and read-only; the Policy Engine and permission system retain sole authoritative control over financial payment actions.
- **Prompt Injection Defense**: Treats external customer metadata as untrusted data (`<untrusted_metadata>`), blocking instruction bypass attempts.
