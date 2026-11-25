import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    # Server
    BACKEND_HOST = os.getenv("BACKEND_HOST", "localhost")
    BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
    BACKEND_DEBUG = os.getenv("BACKEND_DEBUG", "true").lower() in ("true", "1", "yes")

    API_V1_PREFIX = "/api/v1"

    # Facebook (single page for now)
    FB_PAGE_ID = os.environ["FB_PAGE_ID"]
    FB_PAGE_ACCESS_TOKEN = os.environ["FB_PAGE_ACCESS_TOKEN"]
    FB_GRAPH_API_VERSION = os.getenv("FB_GRAPH_API_VERSION", "v21.0")

    # Database
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Analyzer
    ANALYZER_MODEL_VERSION = os.getenv("ANALYZER_MODEL_VERSION", "analyzer-0.1.0")
    
    # Task queue
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")




