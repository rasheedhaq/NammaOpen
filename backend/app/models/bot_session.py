import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, JSON, String, Uuid

from app.core.database import Base


class BotSession(Base):
    __tablename__ = "bot_sessions"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact = Column(String(120), nullable=False, unique=True)
    channel = Column(String(20), nullable=False)
    step = Column(String(50), nullable=False)
    payload = Column(JSON, nullable=True)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
