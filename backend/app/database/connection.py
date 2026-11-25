from sqlmodel import Session, create_engine

from app.config import Config

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=Config.BACKEND_DEBUG, pool_pre_ping=True)


def get_session():
    with Session(engine) as session:
        yield session
