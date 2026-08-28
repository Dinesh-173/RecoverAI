# RecoverAI Technical Interview Preparation & Panel Q&A

### Q1: Why did you choose this problem?
**A**: Payment failure is the single largest point of revenue leakage for digital merchants. While checkout optimization is mature, post-failure revenue recovery is fragmented, either relying on dumb static retry scripts that waste gateway fees and annoy customers, or manual spreadsheets. RecoverAI solves this by automating intelligent, context-aware recovery workflows.

---

### Q2: Why an AI agent instead of a pure rule-based system?
**A**: Real-world payment failures are multi-dimensional: customer LTV, previous payment reliability, error codes, gateway health, and communication channels all interact dynamically. Pure rule engines become unmaintainable spaghetti matrices. The AI agent acts as a flexible diagnostic reasoner that synthesizes unstructured failure context into optimal strategies, while the deterministic policy engine enforces hard safety limits.

---

### Q3: What is the exact role of the ML model vs the LLM?
**A**:
- **ML Model (Gradient Boosting Classifier)**: Fast, quantitative probability prediction ($P(\text{recovery})$) and expected recoverable amount calculation on tabular payment features.
- **LLM Diagnostic Agent**: Contextual reasoning, root-cause diagnosis, reason code generation, customer profile interpretation, and human-readable justification for merchant operators.
- **Deterministic Policy Engine**: Enforces hard constraints (opt-outs, retry bounds, high-value thresholds).

---

### Q4: How do you prevent LLM hallucinations or dangerous financial actions?
**A**:
1. The LLM has **NO direct database write access** and **NO direct payment execution API keys**.
2. The LLM returns strictly validated **Pydantic JSON** schemas.
3. Every proposal is evaluated by the **Deterministic Policy Engine** before execution. If a proposal attempts to retry an opted-out customer or exceed retry limits, the policy engine unconditionally blocks it.

---

### Q5: How do you guarantee webhook idempotency and replay protection?
**A**:
1. All webhooks require valid **HMAC-SHA256 signatures** matching the secret key.
2. The `webhook_events` database table enforces a **UNIQUE constraint on `razorpay_event_id`**.
3. If Razorpay delivers the same webhook twice, the duplicate is caught at the DB constraint level and immediately returns `200 OK (DUPLICATE_IGNORED)` without triggering duplicate actions or charges.

---

### Q6: What happens if the LLM provider experiences an outage?
**A**: RecoverAI includes an autonomous **Deterministic Fallback Engine**. If an LLM request times out, throws a rate limit, or returns malformed JSON, the fallback engine automatically routes the payment using proven rule heuristics (e.g., transient gateway errors with positive history trigger a 45-min delayed retry, while high-value payments escalate for human review). It logs `is_fallback = True` for transparency.

---

### Q7: How did you evaluate the system and prove it adds value?
**A**: We trained on 14,000 synthetic records and evaluated strictly on **3,000 held-out test records** using chronological time splits. Compared to the industry baseline ("Always retry once on attempt 1"), RecoverAI increased recovered revenue from ₹1.04 Cr to ₹1.63 Cr (+56.94% uplift) while saving 803 wasteful retries on unrecoverable payments.
