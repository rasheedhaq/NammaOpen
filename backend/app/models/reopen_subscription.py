import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Uuid

from app.core.database import Base


class ReopenSubscription(Base):
    __tablename__ = "reopen_subscriptions"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(Uuid(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False)
    user_contact = Column(String(120), nullable=False)
    channel = Column(String(20), nullable=False, default="web")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    notified_at = Column(DateTime(timezone=True), nullable=True)
