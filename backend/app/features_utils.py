import pandas as pd
import numpy as np
from datetime import datetime, timezone
from ml.features.engineer import extract_features


def compute_realtime_features(transaction_data: dict, customer_data: dict) -> pd.DataFrame:
    """Formats single transaction and customer data into DataFrame for ML model pipeline."""
    now = datetime.now(timezone.utc)
    
    raw_dict = {
        "transaction_id": [transaction_data.get("id", "tx_temp")],
        "amount": [float(transaction_data.get("amount", 0.0))],
        "payment_method": [transaction_data.get("payment_method", "UPI")],
        "merchant_category": [transaction_data.get("merchant_category", "ECOMMERCE")],
        "failure_code": [transaction_data.get("failure_code", "GATEWAY_ERROR")],
        "failure_reason": [transaction_data.get("failure_reason", "Gateway error")],
        "attempt_number": [int(transaction_data.get("attempt_number", 1))],
        "previous_success_count": [int(customer_data.get("successful_payment_count", 0))],
        "previous_failure_count": [int(customer_data.get("failed_payment_count", 0))],
        "customer_lifetime_value": [float(customer_data.get("total_lifetime_value", 0.0))],
        "is_subscription": [1 if transaction_data.get("subscription_id") else 0],
        "communication_opt_out": [1 if customer_data.get("communication_opt_out") else 0],
        "customer_segment": [customer_data.get("customer_segment", "STANDARD")],
        "hour_of_day": [now.hour],
        "day_of_week": [now.weekday()],
    }

    df = pd.DataFrame(raw_dict)
    return extract_features(df)
