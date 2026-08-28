import os
import joblib
from backend.app.core.logging import logger

_MODEL_INSTANCE = None


def get_trained_model(model_path: str = "ml/models/recovery_model.joblib"):
    global _MODEL_INSTANCE
    if _MODEL_INSTANCE is not None:
        return _MODEL_INSTANCE

    if os.path.exists(model_path):
        try:
            _MODEL_INSTANCE = joblib.load(model_path)
            logger.info(f"Loaded trained ML model from {model_path}")
            return _MODEL_INSTANCE
        except Exception as e:
            logger.error(f"Error loading model from {model_path}: {e}")
            return None
    return None
