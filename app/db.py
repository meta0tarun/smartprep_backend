# app/db.py  (update or create if you don't have it)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from app.config import Config
import logging

logger = logging.getLogger(__name__)

def make_engine():
    url = Config.DATABASE_URL
    if not url:
        raise RuntimeError("DATABASE_URL is not configured")

    # If user didn't append sslmode, ensure it's present
    if "sslmode=" not in url:
        if "?" in url:
            url = f"{url}&sslmode=require"
        else:
            url = f"{url}?sslmode=require"

    connect_args = {}
    # When using psycopg2, set sslmode via connect_args isn't necessary if it's in URL,
    # but we add for explicitness when using certain drivers.
    connect_args["sslmode"] = "require"

    # Optional: prefer IPv4 by forcing host to an IPv4 address (not recommended),
    # but if IPv6 is the issue we prefer forcing IPv4 via socket family at lower level.
    # For most setups adding sslmode will fix the connectivity problem.

    try:
        engine = create_engine(
            url,
            connect_args=connect_args,
            pool_pre_ping=True,
            future=True,
        )
        # quick test connection (optional, logs if fails)
        with engine.connect() as conn:
            pass
        return engine
    except OperationalError as e:
        logger.exception("Database connection failed during engine creation")
        raise

# Create a session factory
engine = make_engine()
# Removed unsupported `autocommit` kwarg (SQLAlchemy 2.x). Use future=True instead.
SessionLocal = sessionmaker(bind=engine, autoflush=False, future=True)
