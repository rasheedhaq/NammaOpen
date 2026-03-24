from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.payment_plan import PaymentPlan
from app.models.shop import Shop
from app.schemas.shop import ShopCreate, ShopDetail, ShopOut, ShopUpdate
from app.services.catalog_service import seed_service_template
from app.services.discovery_service import rank_fallbacks, to_shop_detail, to_shop_summary
from app.services.payments import init_payment
from app.services.status_service import get_current_status

router = APIRouter()


def _find_shop_by_identifier(db: Session, identifier: str) -> Shop | None:
    if "@" in identifier:
        return db.query(Shop).filter(Shop.upi_handle == identifier).one_or_none()
    return db.query(Shop).filter(Shop.owner_phone == identifier).one_or_none()


@router.post("", response_model=ShopOut, status_code=201)
def create_shop(payload: ShopCreate, db: Session = Depends(get_db)):
    existing = db.query(Shop).filter(Shop.owner_phone == payload.owner_phone).one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Shop already registered for this phone")

    shop = Shop(**payload.dict())
    db.add(shop)
    db.flush()
    seed_service_template(db, shop)
    payment_plan = init_payment(db, shop.id, plan="basic")
    db.refresh(shop)
    summary = to_shop_summary(shop, get_current_status(db, shop.id))
    return ShopOut(
        id=shop.id,
        display_name=shop.display_name,
        legal_name=shop.legal_name,
        category=shop.category,
        owner_phone=shop.owner_phone,
        whatsapp_number=shop.whatsapp_number,
        telegram_handle=shop.telegram_handle,
        upi_handle=shop.upi_handle,
        address=shop.address,
        pincode=shop.pincode,
        geo_lat=shop.geo_lat,
        geo_lng=shop.geo_lng,
        status_default_schedule=shop.status_default_schedule,
        languages=shop.languages,
        public_url=summary.public_url,
        current_status=summary.current_status,
    )


@router.get("/{shop_id}", response_model=ShopDetail)
def get_shop(shop_id: UUID, db: Session = Depends(get_db)):
    shop = db.get(Shop, shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    status = get_current_status(db, shop.id)
    candidate_shops = db.query(Shop).filter(Shop.category == shop.category).limit(10).all()
    status_map = {str(candidate.id): get_current_status(db, candidate.id) for candidate in candidate_shops}
    payment_plan = db.query(PaymentPlan).filter(PaymentPlan.shop_id == shop.id).one_or_none()
    return to_shop_detail(shop, status, rank_fallbacks(shop, candidate_shops, status_map), payment_plan)


@router.get("/public/{identifier}", response_model=ShopDetail)
def get_public_shop(identifier: str, db: Session = Depends(get_db)):
    shop = _find_shop_by_identifier(db, identifier)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    status = get_current_status(db, shop.id)
    candidate_shops = db.query(Shop).filter(Shop.category == shop.category).limit(10).all()
    status_map = {str(candidate.id): get_current_status(db, candidate.id) for candidate in candidate_shops}
    payment_plan = db.query(PaymentPlan).filter(PaymentPlan.shop_id == shop.id).one_or_none()
    return to_shop_detail(shop, status, rank_fallbacks(shop, candidate_shops, status_map), payment_plan)


@router.patch("/{shop_id}", response_model=ShopOut)
def update_shop(shop_id: UUID, payload: ShopUpdate, db: Session = Depends(get_db)):
    shop = db.get(Shop, shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(shop, key, value)
    db.commit()
    db.refresh(shop)
    summary = to_shop_summary(shop, get_current_status(db, shop.id))
    return ShopOut(
        id=shop.id,
        display_name=shop.display_name,
        legal_name=shop.legal_name,
        category=shop.category,
        owner_phone=shop.owner_phone,
        whatsapp_number=shop.whatsapp_number,
        telegram_handle=shop.telegram_handle,
        upi_handle=shop.upi_handle,
        address=shop.address,
        pincode=shop.pincode,
        geo_lat=shop.geo_lat,
        geo_lng=shop.geo_lng,
        status_default_schedule=shop.status_default_schedule,
        languages=shop.languages,
        public_url=summary.public_url,
        current_status=summary.current_status,
    )
