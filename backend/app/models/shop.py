import uuid
from sqlalchemy import Column, Float, JSON, String, Uuid
from sqlalchemy.orm import relationship
from app.core.database import Base


class Shop(Base):
    __tablename__ = "shops"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    display_name = Column(String(120), nullable=False)
    legal_name = Column(String(200), nullable=True)
    category = Column(String(50), nullable=False)
    owner_phone = Column(String(20), nullable=False, unique=True)
    whatsapp_number = Column(String(20), nullable=True)
    telegram_handle = Column(String(50), nullable=True)
    upi_handle = Column(String(120), nullable=True)
    address = Column(String(300), nullable=True)
    pincode = Column(String(6), nullable=False)
    geo_lat = Column(Float, nullable=True)
    geo_lng = Column(Float, nullable=True)
    status_default_schedule = Column(JSON, nullable=True)
    languages = Column(JSON, nullable=True)

    service_items = relationship("ServiceItem", back_populates="shop", cascade="all, delete-orphan")
    status_events = relationship("StatusEvent", back_populates="shop", cascade="all, delete-orphan")
    payment_plan = relationship("PaymentPlan", back_populates="shop", uselist=False, cascade="all, delete-orphan")
