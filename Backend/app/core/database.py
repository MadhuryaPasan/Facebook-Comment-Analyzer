from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine

from app.core.config import Config


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Create and cache the SQLAlchemy/SQLModel engine."""
    return create_engine(
        Config.SQLALCHEMY_DATABASE_URI,
        echo=Config.BACKEND_DEBUG,
        pool_pre_ping=True,
    )


def get_session() -> Iterator[Session]:
    """Yield a scoped database session for FastAPI request dependencies."""
    with Session(get_engine()) as session:
        yield session
