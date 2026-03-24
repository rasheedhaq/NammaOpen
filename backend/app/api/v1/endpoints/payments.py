from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.config import get_settings
from app.core.database import get_db
from app.models.shop import Shop
from app.schemas.payment import PaymentInitRequest, PaymentPlanOut
from app.services.payments import init_payment

router = APIRouter()


@router.post("/initiate/{shop_id}", response_model=PaymentPlanOut)
def initiate_payment(shop_id: UUID, payload: PaymentInitRequest, db: Session = Depends(get_db)):
    settings = get_settings()
    shop = db.get(Shop, shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    record = init_payment(db, shop_id, payload.plan)
    amount = settings.basic_plan_price_inr if str(record.plan) == "PlanType.basic" or getattr(record.plan, "value", None) == "basic" else 0
    record.amount_inr = amount
    return record
