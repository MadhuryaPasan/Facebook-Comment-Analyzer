from app.core.config import Config
from app.main import app

__all__ = ["app"]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=Config.BACKEND_HOST,
        port=Config.BACKEND_PORT,
        reload=Config.BACKEND_DEBUG,
        log_level="info",
    )
