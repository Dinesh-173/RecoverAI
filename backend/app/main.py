from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status, Depends
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.core.config import settings
from backend.app.core.database import init_db, get_db
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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    corr_id = getattr(request.state, "correlation_id", "req_unknown")
    logger.warning(f"Validation error [{corr_id}]: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request parameter or payload structure.",
                "request_id": corr_id,
                "details": {"errors": exc.errors()},
            }
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    corr_id = getattr(request.state, "correlation_id", "req_unknown")
    code_map = {
        404: "RESOURCE_NOT_FOUND",
        403: "FORBIDDEN_OPERATION",
        401: "UNAUTHORIZED",
        400: "BAD_REQUEST",
        405: "METHOD_NOT_ALLOWED",
    }
    code = code_map.get(exc.status_code, "HTTP_ERROR")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": code,
                "message": str(exc.detail),
                "request_id": corr_id,
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


# Health Check Probe with Live DB Connectivity Verification
@app.get("/health", tags=["Health"])
async def health_check(db: AsyncSession = Depends(get_db)):
    db_status = "UNKNOWN"
    try:
        await db.execute(select(1))
        db_status = "HEALTHY"
    except Exception as e:
        logger.error(f"Health check DB ping failed: {e}")
        db_status = "UNHEALTHY"

    is_healthy = db_status == "HEALTHY"
    status_code = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "HEALTHY" if is_healthy else "UNHEALTHY",
            "service": "RecoverAI Agent Engine",
            "environment": settings.ENVIRONMENT,
            "demo_mode": settings.DEMO_MODE,
            "llm_provider": settings.LLM_PROVIDER,
            "dependencies": {
                "database": db_status,
            },
        },
    )


# Mount API Routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(webhook_router)
