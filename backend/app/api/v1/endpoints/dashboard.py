from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.services.metrics_service import MetricsService
from backend.app.schemas.schemas import DashboardMetrics

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(db: AsyncSession = Depends(get_db)):
    """Fetch live executive recovery KPIs, charts, and baseline comparisons."""
    return await MetricsService.get_dashboard_metrics(db)
