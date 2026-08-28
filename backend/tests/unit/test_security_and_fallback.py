import hmac
import hashlib
import pytest
from backend.app.core.security import verify_razorpay_webhook_signature, mask_email, hash_identifier
from backend.app.core.exceptions import WebhookSignatureException
from backend.app.agents.recovery_agent import RecoveryDiagnosticAgent
from backend.app.agents.tools import AgentToolLayer


def test_hmac_signature_verification_success():
    payload = b'{"event":"payment.failed","id":"evt_12345"}'
    secret = "test_webhook_secret_key"
    sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

    is_valid = verify_razorpay_webhook_signature(payload, sig, secret)
    assert is_valid is True


def test_hmac_signature_verification_tampered_payload():
    payload = b'{"event":"payment.failed","id":"evt_12345"}'
    tampered_payload = b'{"event":"payment.failed","id":"evt_99999"}'
    secret = "test_webhook_secret_key"
    sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

    with pytest.raises(WebhookSignatureException):
        verify_razorpay_webhook_signature(tampered_payload, sig, secret)


def test_pii_masking():
    assert mask_email("john.doe@example.com") == "j******e@example.com"
    assert mask_email("a@b.com") == "a*@b.com"
    assert len(hash_identifier("customer_secret_123")) == 64


def test_deterministic_recovery_score_calculation():
    score = AgentToolLayer.calculate_recovery_score(
        probability_of_recovery=0.85,
        expected_recoverable_amount=4500.0,
        action_success_probability=0.90,
    )
    # 0.85 * 45 * 0.90 = 34.425 -> 34.43
    assert score > 30.0
    assert isinstance(score, float)


def test_deterministic_fallback_engagement():
    agent = RecoveryDiagnosticAgent(provider_type="mock")
    # Trigger fallback explicitly
    fallback_res = agent._deterministic_fallback(
        transaction_data={"amount": 1500.0, "failure_code": "GATEWAY_ERROR", "attempt_number": 1},
        customer_data={"successful_payment_count": 5, "communication_opt_out": False},
        ml_risk_assessment={"confidence": 0.85, "expected_recoverable_amount": 1275.0, "risk_score": 15.0},
        merchant_policy={"high_value_threshold": 10000.0, "max_retries": 2}
    )
    assert fallback_res.is_fallback is True
    assert fallback_res.recovery_strategy == "DELAYED_RETRY"
    assert "deterministic fallback used" in fallback_res.diagnosis.lower()
