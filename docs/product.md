# RecoverAI Product Strategy & Business Model

## 1. Problem Statement
Online merchants lose 15% to 30% of gross merchandise value (GMV) to failed payments, checkout drop-offs, and subscription mandate declines. 
Merchants currently rely on:
1. **Blind static retries**: Retrying every failed transaction immediately, causing high gateway charges, customer annoyance, and worsening bank rate limits.
2. **Generic spam notifications**: Bombarding customers who already paid or opted out.
3. **Manual spreadsheet operations**: Missing high-value enterprise transactions while wasting hours on low-value unrecoverable dropouts.

---

## 2. The Solution: RecoverAI
RecoverAI provides an autonomous, policy-bounded revenue recovery engine designed natively for Razorpay merchants. It closes the loop:
$$\text{Failed Payment Signal} \longrightarrow \text{ML Scoring} \longrightarrow \text{AI Diagnosis} \longrightarrow \text{Policy Validation} \longrightarrow \text{Bounded Execution} \longrightarrow \text{Measurement}$$

### Key Value Pillars
- **Intelligent Timing**: Differentiates between transient bank gateway outages (which recover with a 45-minute delayed retry) and instrument expiration (which require an asynchronous Razorpay payment link).
- **Merchant Brand Protection**: Automatically halts retries when customers opt out or exceed maximum retry bounds.
- **Human-in-the-Loop Safeguards**: High-value transactions (> ₹10,000) or low-confidence diagnoses are automatically escalated for operational approval.
- **Clear Financial ROI**: Merchants see exactly how much additional revenue was recovered compared to naive baseline rules.

---

## 3. Target Merchant Personas
1. **D2C & E-Commerce Brands**: High UPI volumes, high cart abandonment, frequent temporary bank timeouts.
2. **SaaS & Subscription Businesses**: Recurring mandate failures, expired cards, card balance issues.
3. **EdTech & High-Ticket Platforms**: High-value course fees requiring white-glove human approval and flexible payment links.
