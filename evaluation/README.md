# RecoverAI Evaluation & Benchmark Dataset

## 1. Dataset Overview
- **Total Records**: 20,000 transaction events
- **Time Horizon**: 60 simulated operating days
- **Base Currency**: INR (₹)
- **Target Variable**: `is_recoverable` $\in \{0, 1\}$ (Binary classification indicating whether revenue-at-risk can be successfully recovered under optimal intervention)

## 2. Feature Definitions
- `amount`: Transaction amount in ₹
- `payment_method`: Payment rail (`UPI`, `CARD`, `NETBANKING`, `WALLET`)
- `merchant_category`: Merchant industry (`ECOMMERCE`, `SAAS`, `EDTECH`, `TRAVEL`, `GAMING`)
- `failure_code`: Standard failure code (`GATEWAY_ERROR`, `NETWORK_TIMEOUT`, `INSUFFICIENT_FUNDS`, `USER_DROPPED`, `EXPIRED_CARD`, `FRAUD_SECURITY_BLOCK`)
- `attempt_number`: Attempt count (1 to 4)
- `previous_success_count`: Customer's past successful transactions
- `previous_failure_count`: Customer's past failed transactions
- `customer_lifetime_value`: Total historical spend
- `is_subscription`: Boolean flag for recurring mandate charges
- `communication_opt_out`: Boolean customer privacy preference
- `hour_of_day`: 0 to 23
- `day_of_week`: 0 to 6

## 3. Split Strategy (Time-Based to Prevent Data Leakage)
- **Train Split (70%)**: First 14,000 transactions chronologically
- **Validation Split (15%)**: Next 3,000 transactions
- **Held-out Test Split (15%)**: Final 3,000 transactions

## 4. Evaluation Objectives & Loss Formulation
Unlike generic ML classifiers, payment recovery requires balancing:
1. **False Positives (Type I Error)**: Flagging an unrecoverable or fraudulent transaction leads to wasted gateway fees and customer contact fatigue.
2. **False Negatives (Type II Error)**: Missing a recoverable high-value transaction incurs direct merchant revenue loss.
3. **Revenue Recovery Score**:
   $$\text{Recovery Score} = P(\text{Recovery}) \times \text{Expected Recoverable Amount} \times P(\text{Action Success})$$
