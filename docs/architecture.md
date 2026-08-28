# RecoverAI System Architecture

## 1. Architectural Philosophy
RecoverAI adheres strictly to the separation of **Statistical Prediction (ML)**, **Contextual Diagnostic Reasoning (AI)**, **Deterministic Guardrail Enforcement (Policy Engine)**, and **Financial Action Execution (Adapters)**.

```
Payment Event / Webhook
  │
  ▼
1. ML Risk Model (XGBoost/GBM) ──► Fast statistical recoverability score & revenue estimation
  │
  ▼
2. AI Diagnostic Agent (LLM) ──► Failure root-cause synthesis & intervention strategy formulation
  │
  ▼
3. Deterministic Policy Engine ──► Immutable guardrail validation (Opt-out, limits, cooldowns, approvals)
  │
  ├── IF Escalated ──► Merchant Ops Queue (Waiting Approval)
  ├── IF Blocked ──► Terminal Stop & Audit Record
  └── IF Approved ──► Bounded Action Executor
                          │
                          ▼
4. Payment Adapters (Razorpay Test Mode / Simulation)
  │
  ▼
5. Immutable Audit Trail & Financial ROI Metrics
```

---

## 2. Component Taxonomy

### 2.1 Ingestion & Webhooks Layer
- **Endpoint**: `POST /webhooks/razorpay`
- **Security**: HMAC SHA-256 signature verification over raw request body.
- **Idempotency**: Strict unique constraint on `razorpay_event_id` in PostgreSQL/SQLite. Duplicate events return `200 OK (DUPLICATE_IGNORED)` without re-processing.
- **Async Dispatch**: Quick acceptance with asynchronous worker handoff.

### 2.2 Machine Learning Recoverability Service
- **Model**: Gradient Boosting Classifier trained on 20,000 correlated transaction records.
- **ROC-AUC**: `0.8332`, **Precision**: `78.75%`, **Recall**: `87.76%`.
- **Target**: Bounded probability of successful recovery upon intervention.
- **Score Formula**:
  $$\text{Recovery Score} = P(\text{Recovery}) \times \text{Expected Recoverable Amount} \times P(\text{Action Success})$$

### 2.3 AI Diagnostic Agent
- **Interface**: `LLMProvider` abstraction supporting Google Gemini, OpenAI, and high-throughput deterministic Mock providers.
- **Safety**: Treats all customer metadata as untrusted text.
- **Output Contract**: Strict Pydantic JSON schema validation.
- **Fallback Guarantee**: If the LLM is unavailable or malformed, the system falls back to deterministic decision rules (`is_fallback = True`).

### 2.4 Deterministic Policy Engine
The policy engine acts as an immutable firewall. No LLM recommendation can bypass these rules:
1. **Customer Opt-Out**: Immediate block of communication channels.
2. **Max Retries**: Halts execution if retry attempts $\ge \text{max\_retries}$.
3. **High-Value Threshold**: Escalates amounts $\ge \text{threshold}$ to Human Ops queue.
4. **Low Confidence**: Escalates AI confidence $< 0.70$ to Human Ops queue.
5. **Economic Feasibility**: Stops recovery if recovery score $< 15.0$.

### 2.5 Action Execution Adapters
- **Razorpay Test Adapter**: Interacts with official Razorpay Test Mode endpoints (`/v1/payment_links`, `/v1/orders`, `/v1/payments/{id}`) using `rzp_test_*` credentials.
- **Simulation Payment Adapter**: Self-contained offline simulator for reproducible zero-credential local evaluation and reviewer demonstrations.
