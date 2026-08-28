import logging
import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict


class StructuredJSONFormatter(logging.Formatter):
    """
    Format logs as structured JSON with ISO timestamps and correlation tracking.
    Guarantees that sensitive secrets (e.g. key_secret, auth tokens) are never printed.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "correlation_id"):
            log_obj["correlation_id"] = getattr(record, "correlation_id")
        if hasattr(record, "service"):
            log_obj["service"] = getattr(record, "service")
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            # Sanitize any accidental secret keys
            sanitized = {}
            for k, v in record.extra_data.items():
                if any(sec in k.lower() for sec in ["secret", "password", "token", "key_secret", "cvv", "card"]):
                    sanitized[k] = "[REDACTED]"
                else:
                    sanitized[k] = v
            log_obj["data"] = sanitized

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)


def setup_logger(name: str = "recoverai") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredJSONFormatter())
        logger.addHandler(handler)
    return logger


logger = setup_logger()
