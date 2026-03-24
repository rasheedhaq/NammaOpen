import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Uuid
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class PlanType(str, enum.Enum):
    free = "free"
    basic = "basic"


class PaymentStatus(str, enum.Enum):
    active = "active"
    overdue = "overdue"
    cancelled = "cancelled"


class PaymentPlan(Base):
    __tablename__ = "payment_plans"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(Uuid(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False)
    plan = Column(Enum(PlanType, native_enum=False), default=PlanType.free, nullable=False)
    next_due_at = Column(DateTime(timezone=True), nullable=True)
    payment_link = Column(String(300), nullable=True)
    status = Column(Enum(PaymentStatus, native_enum=False), default=PaymentStatus.active, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    shop = relationship("Shop", back_populates="payment_plan")
