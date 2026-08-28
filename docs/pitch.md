# RecoverAI 5-Minute Buildathon Pitch Script

**Tagline**: *"Detect. Decide. Recover. An Autonomous AI Revenue Recovery Agent for Modern Merchants."*

---

### [0:00 - 0:30] The Problem
"Good morning, judges. Every single day, Indian merchants lose between 15% and 30% of their revenue to failed payments. When a customer's payment fails, merchants today face a brutal dilemma: either blindly retry and spam the customer, or lose the sale forever. Blind retries waste gateway fees and destroy customer trust, while manual spreadsheet recovery is too slow. Merchants are leaking millions of rupees every month."

---

### [0:30 - 1:00] The Solution
"Meet **RecoverAI** — an autonomous, policy-bounded revenue recovery agent built natively for Razorpay. RecoverAI doesn't just send generic reminders. It continuously ingests payment failure signals, statistically scores recoverability using machine learning, diagnoses the exact failure context using an AI agent, passes it through a strict deterministic policy firewall, and executes bounded recovery actions like smart delayed retries and dynamic Razorpay payment links."

---

### [1:00 - 2:30] Live Interactive Demonstration
*(Screen sharing RecoverAI Dashboard & Simulation Runner)*
1. **Executive Dashboard**: "Here on our live dashboard, the merchant immediately sees ₹3.18 Cr of revenue at risk, with ₹1.63 Cr already recovered — achieving a 51.44% recovery rate."
2. **Interactive Simulation**: "Let's click 'Run Recovery Simulation' across our 5 canonical scenarios:
   - **Scenario 1 (High-Value VIP)**: A ₹45,000 netbanking failure from an enterprise client. Instead of taking autonomous risks, RecoverAI's policy engine flags it for **Human Approval**.
   - **Scenario 2 (Transient Timeout)**: A ₹1,499 UPI failure with bank downtime. RecoverAI schedules a **Delayed Retry in 45 minutes**, successfully capturing the revenue.
   - **Scenario 3 (Repeated Failure)**: An attempt-3 failure. Our stopping rules kick in immediately to prevent customer fatigue.
   - **Scenario 4 (Privacy Opt-out)**: The customer opted out of SMS — RecoverAI strictly blocks notifications per merchant compliance rules.
   - **Scenario 5 (Security Anomaly)**: A high fraud risk score is safely terminated."
3. **Approval Queue**: "Let's open the Pending Approvals queue. With one click, the merchant operator inspects the AI evidence and authorizes the recovery."

---

### [2:30 - 3:30] System Architecture & Fintech Safety
"Our architecture enforces a non-negotiable principle: **AI never bypasses policy controls**.
1. **ML Layer**: Fast XGBoost statistical recoverability scoring ($ROC\text{-}AUC = 0.8332$).
2. **AI Layer**: An LLM agent formulated behind a provider abstraction that generates structured Pydantic diagnostic output with zero raw DB permissions.
3. **Deterministic Policy Engine**: Hard fintech guardrails that enforce opt-out compliance, retry bounds, cooldown periods, and mandatory human escalation for high-value orders.
4. **Adapter Layer**: Seamless switching between official Razorpay Test Mode (`rzp_test_*`) and local simulation."

---

### [3:30 - 4:15] Measurable Business Impact & Evaluation
"We evaluated RecoverAI on a held-out test dataset of 3,000 transactions never seen during training:
- **Baseline Strategy ('Always Retry Once')**: Recovered ₹1.04 Cr (32.78%).
- **RecoverAI System**: Recovered **₹1.63 Cr (51.44%)**.
- That is a **+₹59.38 Lakhs net revenue gain (+56.94% uplift)**, while simultaneously saving **803 wasteful retries** and eliminating spam."

---

### [4:15 - 5:00] Conclusion
"RecoverAI transforms payment failures from a total loss into an automated revenue recovery engine. It is safe, measurable, transparent, and built from the ground up for the Razorpay ecosystem. Thank you, and we look forward to your questions!"
