import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from app.api.tags import OPENAPI_TAGS
from app.api.v1.router import api_v1_router
from app.core.config import Config
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown lifecycle hooks."""
    logger.info("Initializing the backend...")
    logger.info("Backend will run on %s:%s", Config.BACKEND_HOST, Config.BACKEND_PORT)
    yield
    logger.info("Shutting down the backend...")


def create_app() -> FastAPI:
    """Build and configure the FastAPI application instance."""
    application = FastAPI(
        title="Facebook Comment Analyzer",
        version="0.1.0",
        description=(
            "Backend API for ingesting Facebook Page posts and comments via the Meta "
            "Graph API and analyzing customer sentiment, intent, language, and aspects."
        ),
        openapi_tags=OPENAPI_TAGS,
        lifespan=lifespan,
    )

    register_exception_handlers(application)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=Config.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["Content-Type"],
    )

    application.include_router(api_v1_router, prefix=Config.API_V1_PREFIX)

    @application.get(
        "/health",
        status_code=status.HTTP_200_OK,
        tags=["health"],
        summary="Health check",
        description="Returns service health status for uptime monitors and load balancers.",
        response_description="Service health indicator.",
    )
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return application


app = create_app()
