# app/models.py
from sqlalchemy import Column, String, Text, TIMESTAMP, JSON, ARRAY, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

def gen_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id = Column(PG_UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(Text)
    email = Column(Text, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class Upload(Base):
    __tablename__ = "uploads"
    id = Column(PG_UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(PG_UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    filename = Column(Text, nullable=False)
    content_type = Column(Text)
    size_bytes = Column(BigInteger)
    storage_path = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class Analysis(Base):
    __tablename__ = "analyses"
    id = Column(PG_UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    upload_ids = Column(ARRAY(PG_UUID(as_uuid=False)))
    user_id = Column(PG_UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    summary = Column(Text)
    raw_response = Column(JSON)
    topics_map = Column(JSON)
    status = Column(Text, default="queued")
    error = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    finished_at = Column(TIMESTAMP(timezone=True))

class Topic(Base):
    __tablename__ = "topics"
    id = Column(PG_UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    analysis_id = Column(PG_UUID(as_uuid=False), ForeignKey("analyses.id"))
    name = Column(Text, nullable=False)
    score = Column(BigInteger, default=0)
    examples = Column(JSON)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
