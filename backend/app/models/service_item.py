import uuid
from sqlalchemy import Boolean, Column, ForeignKey, Integer, Numeric, String, Uuid
from sqlalchemy.orm import relationship
from app.core.database import Base


class ServiceItem(Base):
    __tablename__ = "service_items"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(Uuid(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(120), nullable=False)
    price_min = Column(Numeric(10, 2), nullable=True)
    price_max = Column(Numeric(10, 2), nullable=True)
    enabled = Column(Boolean, default=True, nullable=False)
    duration_mins = Column(Integer, nullable=True)
    supports_home_visit = Column(Boolean, default=False, nullable=False)

    shop = relationship("Shop", back_populates="service_items")
