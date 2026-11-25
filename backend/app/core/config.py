import os
from typing import ClassVar

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Central application configuration loaded from environment variables."""

    # Server
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "localhost")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    BACKEND_DEBUG: bool = os.getenv("BACKEND_DEBUG", "true").lower() in ("true", "1", "yes")
    CORS_ORIGINS: ClassVar[list[str]] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5500,http://127.0.0.1:5500",
        ).split(",")
        if origin.strip()
    ]

    API_V1_PREFIX: str = "/api/v1"

    # Facebook (single page for now)
    FB_PAGE_ID: str = os.getenv("FB_PAGE_ID", "")
    FB_PAGE_ACCESS_TOKEN: str = os.getenv("FB_PAGE_ACCESS_TOKEN", "")
    FB_GRAPH_API_VERSION: str = os.getenv("FB_GRAPH_API_VERSION", "v21.0")

    # Database
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "comment_analyzer")
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL",
        f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    )

    # Analyzer
    ANALYZER_MODEL_VERSION: str = os.getenv("ANALYZER_MODEL_VERSION", "analyzer-0.1.0")

    # Task queue
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    @classmethod
    def validate_facebook_settings(cls) -> None:
        """Ensure required Facebook credentials are configured before Graph API calls."""
        missing = [
            name
            for name, value in (
                ("FB_PAGE_ID", cls.FB_PAGE_ID),
                ("FB_PAGE_ACCESS_TOKEN", cls.FB_PAGE_ACCESS_TOKEN),
            )
            if not value
        ]
        if missing:
            raise RuntimeError(f"Missing required Facebook environment variables: {', '.join(missing)}")
