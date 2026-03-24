import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Numeric, String, Uuid
from app.core.database import Base


class UserCheck(Base):
    __tablename__ = "user_checks"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(Uuid(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False)
    user_geo_lat = Column(Numeric(9, 6), nullable=True)
    user_geo_lng = Column(Numeric(9, 6), nullable=True)
    result_state = Column(String(30), nullable=False)
    fallback_clicked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
