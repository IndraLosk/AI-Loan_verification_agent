# app/models.py
from sqlalchemy import Column, String, DateTime, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.database import Base

class Check(Base):
    __tablename__ = "checks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    program = Column(String(20), nullable=False)  # federal / regional
    status = Column(String(30), nullable=False)
    status_label = Column(String(100))
    reason = Column(String(500))
    issues = Column(JSON, default=list)
    documents = Column(JSON, default=list)
    extracted = Column(JSON, default=dict)
    checked_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)