from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.models.payment_plan import PlanType, PaymentStatus


class PaymentPlanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    shop_id: UUID
    plan: PlanType
    next_due_at: Optional[datetime]
    payment_link: Optional[str]
    status: PaymentStatus
    amount_inr: Optional[int] = None


class PaymentInitRequest(BaseModel):
    plan: PlanType = PlanType.basic
