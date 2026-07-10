"""
FastAPI application factory and entry point.

Start locally:
  uvicorn app.main:app --reload --port 8000

Render web service start command:
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import v1_router
from app.config import get_settings
from app.core.exceptions import AppError, app_error_handler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup / shutdown logic."""
    settings = get_settings()
    logger.info("Starting Agency SaaS backend (env=%s)", settings.environment)
    yield
    logger.info("Shutting down Agency SaaS backend")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Agency SaaS API",
        description="Backend for the Agency Reporting SaaS — MVP",
        version="0.1.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # ---- CORS ----
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---- Exception handlers ----
    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]

    # ---- Routers ----
    app.include_router(v1_router)

    # ---- Health check ----
    @app.get("/health", tags=["health"])
    def health():
        return {"status": "ok"}

    return app


app = create_app()
