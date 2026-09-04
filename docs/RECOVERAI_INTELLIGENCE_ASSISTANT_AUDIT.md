# RecoverAI Intelligence Assistant — Comprehensive Production Architecture & Audit Report

## 1. Executive Summary

The **RecoverAI Intelligence Assistant** is a context-aware, tool-governed, read-only AI copilot embedded directly into the RecoverAI operations platform.

### Core FinTech Safety Invariant
> **"AI can understand, analyze, explain, recommend, and assist. RecoverAI's deterministic Policy Engine and permission system control financial actions."**
>
> The Intelligence Assistant **CANNOT** execute real financial payment retries, authorize high-value approvals, alter Policy Engine rules, or bypass RBAC permissions. Default permission is strictly **READ ONLY**.

---

## 2. Architecture & System Flow

```
+-----------------------------------------------------------------------+
|                RecoverAI Intelligence Assistant UI                    |
|       (Floating Widget Button + Slide-over Glassmorphism Panel)        |
+-----------------------------------------------------------------------+
                                   |
              POST /api/v1/assistant/chat (RBAC Enforced)
                                   v
+-----------------------------------------------------------------------+
|                    IntelligenceAssistantService                       |
|  - Length Limit Safeguard (Max 2,000 chars per message)               |
|  - System Prompt Leak Protection ("Show me system prompt" -> Refusal)  |
|  - Prompt Injection Defense (<untrusted_metadata> wrapper)            |
|  - Financial Mutation Guard (Prohibits payment execution)             |
|  - Page Context Detector (dashboard, simulation, cases, etc.)         |
|  - Controlled Tool Registry (Read-only verified backend tools)        |
|  - Response Formatter & Citation Generator                            |
+-----------------------------------------------------------------------+
          |                                               |
          v                                               v
+------------------------+                     +------------------------+
|  Metrics & Data Tools  |                     |  Policy Engine Rules   |
| (Metrics, Risk, Case)  |                     |  (Authoritative State) |
+------------------------+                     +------------------------+
```

---

## 3. Controlled Read-Only Tool Registry

The assistant employs a strict allowlist of read-only data tools. Arbitrary code execution (`eval`, `exec`, generic SQL) is strictly prohibited.

| Tool Name | Scope | Description |
|:---|:---|:---|
| `get_dashboard_metrics` | Read-only | Computes live Revenue at Risk, Recovered Revenue, Recovery Rate, and Open Cases in INR. |
| `get_model_evaluation` | Read-only | Returns empirical ML evaluation metrics (**ROC-AUC 0.8332**, Precision 78.75%, Recall 87.76%). |
| `get_system_health` | Read-only | Queries live `/health` status (FastAPI engine, PostgreSQL/SQLite, Policy Engine). |
| `get_pending_approvals` | Read-only | Queries active high-value cases (>= ₹10,000) awaiting human merchant approval. |
| `get_audit_logs` | Read-only | Queries the immutable audit trail history for recent actions and policy decisions. |
| `get_recovery_case` | Read-only | Fetches 5-stage decision explainability pipeline for a given `case_id`. |
| `get_simulation_summary` | Read-only | Explains predefined demo scenarios, custom CSV uploads, manual entry, and date range filters. |
| `get_current_page_context` | Read-only | Adapts responses based on active page route (`dashboard`, `recovery_case`, `simulation`, `analytics`, `approvals`, `audit_logs`). |

---

## 4. Security & FinTech Compliance Guardrails

1. **System Prompt Protection**:
   - Intercepts requests attempting system prompt extraction (`"Show me your system prompt"`, `"reveal hidden instructions"`).
   - Responds with an explicit security refusal without leaking internal prompts.
2. **Prompt Injection Defense**:
   - Detects malicious override patterns (`"ignore previous instructions"`, `"bypass policy"`).
   - Wraps customer metadata and failure reasons inside `<untrusted_metadata>` tags.
   - Treats untrusted text as DATA rather than system instructions.
3. **Financial Mutation Guard**:
   - Intercepts requests attempting direct payment execution or approval.
   - Redirects merchants to the authorized **Pending Approvals Queue** (`/approvals`) for high-value cases ($\ge \text{₹}10,000$).
4. **Length Limit Safeguard**:
   - Enforces a 2,000 character maximum length limit per query to prevent memory DoS attacks.
5. **RBAC Enforcement**:
   - Server-side validation of `X-User-Role` headers (`VIEWER`, `MERCHANT_OPERATOR`, `MERCHANT_ADMIN`, `ADMIN`).
   - Invalid roles receive `HTTP 403 Forbidden`.
6. **PII Masking & Privacy**:
   - Customer emails are hashed via SHA-256 and UI-masked.
7. **Simulation Isolation**:
   - Explains custom dataset testing (`is_simulation=True`) with zero production metric impact.

---

## 5. Verification & Audit Results

### Backend Test Suite
- **Phase 21 Unit Tests**: **14 passed** (0 failed)
- **Full Backend Regression Suite**: **175 passed** (0 failed, 0 errors in 18.55s)

### Frontend Production Build
- **Next.js Production Build (`npm run build`)**: **`✓ Compiled successfully`**
- **Static Pages Generated**: **`11/11`**
- **TypeScript Errors**: **`0`**

### Live API Verification (`scratch/live_assistant_verifier.py`)
- `GET /health` $\rightarrow$ `HTTP 200 HEALTHY`
- `POST /api/v1/assistant/chat` (Revenue Query) $\rightarrow$ `HTTP 200 OK` (`get_dashboard_metrics`)
- `POST /api/v1/assistant/chat` (ML ROC-AUC Query) $\rightarrow$ `HTTP 200 OK` (`get_model_evaluation`)
- `POST /api/v1/assistant/chat` (Pending Approvals Tool) $\rightarrow$ `HTTP 200 OK` (`get_pending_approvals`)
- `POST /api/v1/assistant/chat` (Audit Logs Tool) $\rightarrow$ `HTTP 200 OK` (`get_audit_logs`)
- `POST /api/v1/assistant/chat` (System Prompt Leak Defense) $\rightarrow$ `HTTP 200 OK` (`security_prompt_protection`)
- `POST /api/v1/assistant/chat` (Prompt Injection Defense) $\rightarrow$ `HTTP 200 OK` (Blocked by security guardrail)
- `POST /api/v1/assistant/chat` (Financial Mutation Guard) $\rightarrow$ `HTTP 200 OK` (Prohibited read-only boundary)
- `POST /api/v1/assistant/chat` (Length Limit Safeguard) $\rightarrow$ `HTTP 200 OK` (`request_sanitizer`)

---

## 6. Known Limitations & Future Scope
- **LLM Provider Integration**: Uses deterministic mock responses when external LLM API key (`GEMINI_API_KEY`) is not configured, maintaining 100% offline reliability.
- **Read-Only Scope**: By design, the assistant does not execute payment retries directly; all financial mutations must be triggered via the operations UI or Policy Engine pipeline.
