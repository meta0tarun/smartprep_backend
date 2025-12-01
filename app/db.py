# app/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .config import Config
import os

# Ensure env var exists (validate will raise in config.validate())
Config.validate()
DATABASE_URL = Config.DATABASE_URL

# If using Psycopg >=3 and SQLAlchemy, SQLAlchemy will pick driver automatically from URL.
# Add pool_pre_ping to keep connections healthy in long-running containers.
engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# fast helper for dependency injection in FastAPI endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
