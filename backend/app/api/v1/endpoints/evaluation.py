import os
import json
from fastapi import APIRouter, Depends
from backend.app.core.security import require_role

router = APIRouter(prefix="/evaluation", tags=["Evaluation & Benchmarks"])


@router.get("/results")
async def get_evaluation_results(
    _role: str = Depends(require_role(["MERCHANT_ADMIN", "ADMIN", "MERCHANT_OPERATOR", "VIEWER"])),
):
    """Retrieve held-out empirical evaluation and baseline recovery benchmark metrics."""
    json_path = "evaluation/results.json"
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    return {
        "status": "NOT_GENERATED",
        "message": "Evaluation results not yet generated. Please run `python -m evaluation.generate_report`"
    }
