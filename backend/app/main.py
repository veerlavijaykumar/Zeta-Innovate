"""Main FastAPI application for CareerMap AI."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.database import init_db
from app.api.v1 import (
    auth,
    profile,
    jobs,
    matching,
    career,
    learning,
    documents,
    applications,
    analytics,
)
import structlog

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("Starting CareerMap AI application", environment=settings.ENVIRONMENT)
    # Initialize DB tables if needed
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Database initialization failed", error=str(e))

    yield
    logger.info("Shutting down CareerMap AI application")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="CareerMap AI - AI-Powered Career Discovery & Application Copilot API",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all API v1 routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(profile.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(matching.router, prefix="/api/v1")
app.include_router(career.router, prefix="/api/v1")
app.include_router(learning.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(applications.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")


@app.get("/health", tags=["System"])
@app.get("/api/v1/health", tags=["System"])
async def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global unhandled exception catcher."""
    logger.error("Unhandled server exception", path=request.url.path, error=str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."},
    )
