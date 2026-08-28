# RecoverAI Security & Fintech Compliance

## 1. Webhook Signature Verification
All incoming webhooks at `POST /webhooks/razorpay` require valid HMAC SHA-256 signatures generated with the secret key (`X-Razorpay-Signature`).
- Signatures are computed directly over the raw, unparsed request bytes.
- Comparison utilizes constant-time string comparison (`hmac.compare_digest`) to prevent timing side-channel attacks.
- Invalid or missing signatures immediately return `HTTP 400 Bad Request`.

## 2. Webhook & Action Idempotency
- **Event Deduplication**: The `webhook_events` table contains a unique database index on `razorpay_event_id`. Replayed or duplicated events return `200 OK (DUPLICATE_IGNORED)` without triggering duplicate actions.
- **Action Idempotency**: Recovery actions are bounded by `(recovery_case_id, action_type, attempt_number)` preventing duplicate retry charges or multi-firing notifications.

## 3. PII Masking & Customer Data Protection
- **No Raw Credentials**: Card numbers, CVVs, and banking passwords are never requested, stored, or processed.
- **Masked Data**: Customer emails and phone numbers are hashed or masked (`j***e@example.com`) before reaching the UI or logs.
- **Audit Sanitization**: Audit logs automatically scrub sensitive keys (`secret`, `password`, `key_secret`, `token`).

## 4. Prompt Injection Defenses
- All external inputs (customer names, transaction metadata notes) are treated as **UNTRUSTED TEXT**.
- Isolated XML tags (`<untrusted_metadata>`) enforce strict boundary separation.
- The LLM only returns structured JSON conforming to a Pydantic schema. It has **ZERO direct DB access** or shell permissions.
- Hardcoded deterministic policy rules override any LLM output.

## 5. Role-Based Access Control (RBAC)
- `MERCHANT_ADMIN`: Full permission to configure policies, approve high-value transactions, and reject cases.
- `MERCHANT_OPERATOR`: Can view and analyze cases, trigger batch simulations.
- `VIEWER`: Read-only access to dashboard and analytics. Financial approval endpoints enforce role verification.
