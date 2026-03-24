import uuid
from sqlalchemy import Column, ForeignKey, Numeric, String, Uuid
from app.core.database import Base


class FallbackShop(Base):
    __tablename__ = "fallback_shops"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(Uuid(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False)
    alt_shop_id = Column(Uuid(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False)
    distance_km = Column(Numeric(6, 3), nullable=True)
    score = Column(Numeric(5, 2), nullable=True)
    note = Column(String(200), nullable=True)
