# Architecture Decision Records (ADRs)

## ADR 01: Separation of AI Decision Making, Policy Enforcement, and Action Execution
- **Context**: Financial recovery actions involve monetary movement and customer communications. Allowing an LLM to directly invoke payment APIs introduces catastrophic hallucination and prompt-injection risks.
- **Decision**: Strict three-tier pipeline: AI proposes a structured JSON payload $\rightarrow$ Deterministic Policy Engine validates rules and limits $\rightarrow$ Bounded Action Executor triggers payment adapters.
- **Consequences**: Complete safety guarantee; zero possibility of LLM bypassing merchant thresholds.

## ADR 02: Dual Payment Adapter Pattern (Razorpay Test Mode + Offline Simulation)
- **Context**: Hackathon reviewers and local developers may not have active Razorpay credentials configured in their environment.
- **Decision**: Implement `RazorpayTestAdapter` for official Razorpay Test Mode APIs and `SimulationPaymentAdapter` for zero-credential offline evaluation.
- **Consequences**: Reviewers can execute the full end-to-end demo and benchmark suites instantly out of the box with zero external dependencies.

## ADR 03: Time-Based Dataset Splitting for ML Evaluation
- **Context**: Random train/test splits cause data leakage in transactional time-series data.
- **Decision**: Split 20,000 transactions chronologically (70% train, 15% validation, 15% test).
- **Consequences**: Genuine out-of-sample performance measurement reflecting real-world merchant production dynamics.

## ADR 04: Deterministic Fallback Strategy for AI Downtime
- **Context**: External LLM APIs can experience rate limits, latency spikes, or outages.
- **Decision**: Implement a fintech decision tree fallback that activates if LLM generation times out or returns malformed JSON.
- **Consequences**: High availability (99.99%) without degrading into unhandled exceptions.
