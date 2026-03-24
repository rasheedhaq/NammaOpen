import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Uuid
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class StatusState(str, enum.Enum):
    open = "open"
    closed = "closed"
    paused = "paused"
    likely_closed = "likely_closed"


class StatusChannel(str, enum.Enum):
    whatsapp = "whatsapp"
    telegram = "telegram"
    missed_call = "missed_call"
    auto = "auto"
    ml = "ml"


class StatusEvent(Base):
    __tablename__ = "status_events"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(Uuid(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False)
    state = Column(Enum(StatusState, native_enum=False), nullable=False)
    channel = Column(Enum(StatusChannel, native_enum=False), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    created_by = Column(String(50), nullable=True)

    shop = relationship("Shop", back_populates="status_events")
