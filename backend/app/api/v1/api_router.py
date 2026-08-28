from fastapi import APIRouter
from backend.app.api.v1.endpoints import (
    dashboard,
    transactions,
    recovery_cases,
    approvals,
    audit_logs,
    simulation,
    evaluation,
    webhooks,
)

api_router = APIRouter()

api_router.include_router(dashboard.router)
api_router.include_router(transactions.router)
api_router.include_router(recovery_cases.router)
api_router.include_router(approvals.router)
api_router.include_router(audit_logs.router)
api_router.include_router(simulation.router)
api_router.include_router(evaluation.router)
api_router.include_router(webhooks.router)
