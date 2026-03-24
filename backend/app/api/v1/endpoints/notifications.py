from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.reopen_subscription import ReopenSubscription
from app.models.shop import Shop
from app.schemas.notification import ReopenRequest, ReopenSubscriptionOut

router = APIRouter()


@router.post("/reopen/{shop_id}", response_model=ReopenSubscriptionOut, status_code=201)
def subscribe_reopen(shop_id: UUID, payload: ReopenRequest, db: Session = Depends(get_db)):
    shop = db.get(Shop, shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    existing = (
        db.query(ReopenSubscription)
        .filter(
            ReopenSubscription.shop_id == shop_id,
            ReopenSubscription.user_contact == payload.user_contact,
            ReopenSubscription.channel == payload.channel,
        )
        .one_or_none()
    )
    if existing:
        return existing

    subscription = ReopenSubscription(
        shop_id=shop_id,
        user_contact=payload.user_contact,
        channel=payload.channel,
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription
