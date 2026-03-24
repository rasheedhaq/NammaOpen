from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.status import StatusUpdate, StatusOut
from app.services.status_service import set_status, get_current_status
from app.models.shop import Shop

router = APIRouter()


@router.patch("/{shop_id}/status", response_model=StatusOut)
def update_status(shop_id: UUID, payload: StatusUpdate, db: Session = Depends(get_db)):
    shop = db.get(Shop, shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    expires_at = payload.until
    evt = set_status(db, shop_id, payload.state, payload.channel, expires_at=expires_at)
    return evt


@router.get("/{shop_id}/status", response_model=StatusOut)
def current_status(shop_id: UUID, db: Session = Depends(get_db)):
    shop = db.get(Shop, shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    evt = get_current_status(db, shop_id)
    if not evt:
        raise HTTPException(status_code=404, detail="No status yet")
    return evt
