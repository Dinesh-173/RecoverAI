import os
import random
import uuid
import hashlib
from datetime import datetime, timedelta, timezone
import pandas as pd
import numpy as np


def generate_synthetic_dataset(
    num_records: int = 20000,
    seed: int = 42,
    output_dir: str = "ml/data"
) -> pd.DataFrame:
    """
    Generates a realistic synthetic transaction dataset with domain-specific fintech correlations
    for training and evaluating RecoverAI's revenue recovery model.
    """
    random.seed(seed)
    np.random.seed(seed)
    os.makedirs(output_dir, exist_ok=True)

    merchant_categories = ["ECOMMERCE", "SAAS", "EDTECH", "TRAVEL", "GAMING"]
    payment_methods = ["UPI", "CARD", "NETBANKING", "WALLET"]
    method_weights = [0.55, 0.25, 0.15, 0.05] # High UPI prevalence

    # Failure types with realistic base recoverability probabilities
    failure_types = [
        {"code": "GATEWAY_ERROR", "reason": "Bank server timeout or gateway downtime", "base_prob": 0.85, "weight": 0.30},
        {"code": "NETWORK_TIMEOUT", "reason": "Network latency or connection reset", "base_prob": 0.82, "weight": 0.20},
        {"code": "INSUFFICIENT_FUNDS", "reason": "Customer account has insufficient balance", "base_prob": 0.60, "weight": 0.25},
        {"code": "USER_DROPPED", "reason": "Customer abandoned 3DS authentication flow", "base_prob": 0.40, "weight": 0.12},
        {"code": "EXPIRED_CARD", "reason": "Debit or credit card expired", "base_prob": 0.18, "weight": 0.08},
        {"code": "FRAUD_SECURITY_BLOCK", "reason": "Issuer risk engine blocked transaction", "base_prob": 0.02, "weight": 0.05},
    ]
    f_codes = [f["code"] for f in failure_types]
    f_reasons = {f["code"]: f["reason"] for f in failure_types}
    f_probs = {f["code"]: f["base_prob"] for f in failure_types}
    f_weights = [f["weight"] for f in failure_types]

    # Generate customer pool
    num_customers = int(num_records / 4)
    customers = []
    for i in range(num_customers):
        c_id = f"cust_{uuid.uuid4().hex[:10]}"
        segment = random.choices(["VIP", "HIGH_VALUE", "STANDARD", "NEW", "AT_RISK"], weights=[0.05, 0.15, 0.60, 0.15, 0.05])[0]
        
        if segment == "VIP":
            prev_success = random.randint(15, 60)
            prev_failed = random.randint(0, 2)
            ltv = random.uniform(25000, 150000)
            opt_out = random.random() < 0.02
        elif segment == "HIGH_VALUE":
            prev_success = random.randint(5, 20)
            prev_failed = random.randint(0, 3)
            ltv = random.uniform(10000, 50000)
            opt_out = random.random() < 0.04
        elif segment == "STANDARD":
            prev_success = random.randint(1, 8)
            prev_failed = random.randint(0, 4)
            ltv = random.uniform(1500, 15000)
            opt_out = random.random() < 0.08
        elif segment == "NEW":
            prev_success = 0
            prev_failed = random.randint(0, 1)
            ltv = 0.0
            opt_out = random.random() < 0.05
        else: # AT_RISK
            prev_success = random.randint(0, 2)
            prev_failed = random.randint(3, 8)
            ltv = random.uniform(500, 3000)
            opt_out = random.random() < 0.20

        customers.append({
            "customer_id": c_id,
            "segment": segment,
            "prev_success": prev_success,
            "prev_failed": prev_failed,
            "ltv": round(ltv, 2),
            "opt_out": opt_out
        })

    records = []
    base_time = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

    for i in range(num_records):
        # Time progression
        time_offset_hours = (i / num_records) * (60 * 24) # Across 60 days
        tx_time = base_time + timedelta(hours=time_offset_hours, minutes=random.randint(0, 59))
        
        cust = random.choice(customers)
        m_category = random.choice(merchant_categories)
        payment_method = random.choices(payment_methods, weights=method_weights)[0]
        
        # Transaction Amount correlated with customer LTV & merchant category
        if m_category == "SAAS":
            amount = round(random.choice([499, 999, 1499, 2999, 4999, 9999, 19999, 49999]), 2)
            is_subscription = True
        elif m_category == "EDTECH":
            amount = round(random.uniform(2000, 35000), 2)
            is_subscription = random.random() < 0.30
        else:
            amount = round(random.uniform(199, 15000), 2)
            is_subscription = random.random() < 0.10

        # Attempt number
        attempt_number = random.choices([1, 2, 3, 4], weights=[0.75, 0.18, 0.05, 0.02])[0]
        
        # Failure code selection
        f_code = random.choices(f_codes, weights=f_weights)[0]
        f_reason = f_reasons[f_code]
        
        # Determine recoverability probability using realistic fintech principles
        base_recovery_p = f_probs[f_code]
        
        # Customer history boost
        hist_total = cust["prev_success"] + cust["prev_failed"]
        if hist_total > 0:
            hist_ratio = cust["prev_success"] / hist_total
            history_adj = (hist_ratio - 0.5) * 0.30
        else:
            history_adj = -0.05

        # Attempt degradation (each repeated retry reduces chance of recovery)
        attempt_adj = -0.12 * (attempt_number - 1)
        
        # Payment method adjustment
        method_adj = 0.05 if payment_method == "UPI" else (-0.05 if payment_method == "WALLET" else 0.0)

        # High value adjustment (harder to recover unprompted)
        amount_adj = -0.08 if amount > 15000 else 0.02

        # Final calculated probability bounded in [0.01, 0.98]
        recovery_probability = max(0.01, min(0.98, base_recovery_p + history_adj + attempt_adj + method_adj + amount_adj))
        
        # Target assignment (0 = not recovered, 1 = successfully recovered upon intervention)
        is_recoverable = 1 if (random.random() < recovery_probability) else 0

        # Expected optimal recovery strategy
        if f_code in ["GATEWAY_ERROR", "NETWORK_TIMEOUT"]:
            optimal_strategy = "DELAYED_RETRY" if attempt_number == 1 else "RETRY_PAYMENT"
        elif f_code == "INSUFFICIENT_FUNDS":
            optimal_strategy = "CUSTOMER_NOTIFICATION" if not cust["opt_out"] else "DELAYED_RETRY"
        elif f_code == "USER_DROPPED":
            optimal_strategy = "CUSTOMER_NOTIFICATION" if not cust["opt_out"] else "STOP_RECOVERY"
        elif f_code == "EXPIRED_CARD":
            optimal_strategy = "CUSTOMER_NOTIFICATION" if not cust["opt_out"] else "STOP_RECOVERY"
        else: # FRAUD
            optimal_strategy = "STOP_RECOVERY"

        if amount > 25000:
            optimal_strategy = "HUMAN_REVIEW"

        records.append({
            "transaction_id": f"tx_{uuid.uuid4().hex[:12]}",
            "timestamp": tx_time.isoformat(),
            "customer_id": cust["customer_id"],
            "customer_segment": cust["segment"],
            "merchant_category": m_category,
            "payment_method": payment_method,
            "amount": amount,
            "failure_code": f_code,
            "failure_reason": f_reason,
            "attempt_number": attempt_number,
            "previous_success_count": cust["prev_success"],
            "previous_failure_count": cust["prev_failed"],
            "customer_lifetime_value": cust["ltv"],
            "is_subscription": 1 if is_subscription else 0,
            "communication_opt_out": 1 if cust["opt_out"] else 0,
            "hour_of_day": tx_time.hour,
            "day_of_week": tx_time.weekday(),
            "ground_truth_probability": round(recovery_probability, 4),
            "optimal_strategy": optimal_strategy,
            "is_recoverable": is_recoverable
        })

    df = pd.DataFrame(records)
    # Sort chronologically for time-based splitting
    df = df.sort_values(by="timestamp").reset_index(drop=True)

    # Time-based splitting: 70% Train, 15% Validation, 15% Test
    n = len(df)
    train_idx = int(n * 0.70)
    val_idx = int(n * 0.85)

    train_df = df.iloc[:train_idx]
    val_df = df.iloc[train_idx:val_idx]
    test_df = df.iloc[val_idx:]

    train_df.to_csv(os.path.join(output_dir, "train.csv"), index=False)
    val_df.to_csv(os.path.join(output_dir, "val.csv"), index=False)
    test_df.to_csv(os.path.join(output_dir, "test.csv"), index=False)

    print(f"Generated {len(df)} synthetic transaction records.")
    print(f"Splits: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}")
    print(f"Overall recoverability rate: {df['is_recoverable'].mean():.2%}")
    return df


if __name__ == "__main__":
    generate_synthetic_dataset(num_records=20000, seed=42)
