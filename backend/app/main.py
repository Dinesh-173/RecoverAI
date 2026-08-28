from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.core.database import init_db
from backend.app.core.exceptions import RecoverAIException
from backend.app.core.logging import logger
from backend.app.core.security import generate_correlation_id
from backend.app.api.v1.api_router import api_router
from backend.app.api.v1.endpoints.webhooks import router as webhook_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database tables
    logger.info("Starting RecoverAI Backend Engine...")
    await init_db()
    yield
    logger.info("Shutting down RecoverAI Backend Engine...")


app = FastAPI(
    title="RecoverAI - Autonomous AI Revenue Recovery Agent",
    description="Production-grade AI Revenue Recovery platform for merchants on Razorpay.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    correlation_id = request.headers.get("x-correlation-id") or generate_correlation_id()
    request.state.correlation_id = correlation_id
    response = await call_next(request)
    response.headers["x-correlation-id"] = correlation_id
    return response


# Global Exception Handler for Standardized Error Format
@app.exception_handler(RecoverAIException)
async def recover_ai_exception_handler(request: Request, exc: RecoverAIException):
    corr_id = getattr(request.state, "correlation_id", "req_unknown")
    logger.warning(f"Handled exception: {exc.code} - {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "request_id": corr_id,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    corr_id = getattr(request.state, "correlation_id", "req_unknown")
    logger.error(f"Unhandled error [{corr_id}]: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please contact merchant operations.",
                "request_id": corr_id,
            }
        },
    )


# Health Check Probe
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "HEALTHY",
        "service": "RecoverAI Agent Engine",
        "environment": settings.ENVIRONMENT,
        "demo_mode": settings.DEMO_MODE,
        "llm_provider": settings.LLM_PROVIDER,
    }


# Mount API Routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(webhook_router)
