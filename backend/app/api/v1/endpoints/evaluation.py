import os
import json
from fastapi import APIRouter

router = APIRouter(prefix="/evaluation", tags=["Evaluation & Benchmarks"])


@router.get("/results")
async def get_evaluation_results():
    """Retrieve held-out empirical evaluation and baseline recovery benchmark metrics."""
    json_path = "evaluation/results.json"
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    return {
        "status": "NOT_GENERATED",
        "message": "Evaluation results not yet generated. Please run `python -m evaluation.generate_report`"
    }
