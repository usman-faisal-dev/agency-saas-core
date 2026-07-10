"""
SQLAlchemy engine, session factory, and declarative base.
All models import Base from here; never create a second one.
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    """Shared declarative base for all SQLAlchemy models."""
    pass


def _make_engine():
    settings = get_settings()
    # Neon Postgres requires SSL — psycopg2 picks it up from the URL's sslmode param.
    # pool_pre_ping keeps the connection alive through Neon's scale-to-zero.
    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        echo=settings.environment == "development",
    )


engine = _make_engine()

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session and ensures it is
    closed after the request, even on error.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
