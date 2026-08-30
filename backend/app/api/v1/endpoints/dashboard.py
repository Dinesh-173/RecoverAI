from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.services.metrics_service import MetricsService
from backend.app.schemas.schemas import DashboardMetrics
from backend.app.core.security import require_role

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_role(["MERCHANT_ADMIN", "ADMIN", "MERCHANT_OPERATOR", "VIEWER"])),
):
    """Fetch live executive recovery KPIs, charts, and baseline comparisons."""
    return await MetricsService.get_dashboard_metrics(db)
