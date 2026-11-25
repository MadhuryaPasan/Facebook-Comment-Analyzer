import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("backend-server.log"), logging.StreamHandler()],
)

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Config
from app.exceptions.exceptions import AppException
from app.exceptions.exception_handlers import app_exception_handler
from app.routers.post_comment_router import router as post_comment_router
from app.routers.analysis_router import router as analysis_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing the backend...")
    logger.info("Backend will run on %s:%s", Config.BACKEND_HOST, Config.BACKEND_PORT)
    yield
    logger.info("Shutting down the backend...")


app = FastAPI(
    title="Facebook Comment Analyzer",
    lifespan=lifespan,
    version="0.1.0",
    description="Analyzes Facebook page comments so companies can see what customers think",
)
app.add_exception_handler(AppException, app_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Content-Type"],
)


app.include_router(post_comment_router, prefix=Config.API_V1_PREFIX)
app.include_router(analysis_router, prefix=Config.API_V1_PREFIX)


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=Config.BACKEND_HOST,
        port=Config.BACKEND_PORT,
        reload=Config.BACKEND_DEBUG,
        log_level="info",
    )
