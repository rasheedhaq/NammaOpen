from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.shop import Shop
from app.schemas.search import SearchResponse
from app.services.discovery_service import haversine_km, normalize_search_term, to_shop_summary
from app.services.status_service import get_current_status

router = APIRouter()


@router.get("/search", response_model=SearchResponse)
def search_shops(
    q: str = Query("", description="Shop name or UPI"),
    pin: str | None = Query(None, description="PIN code"),
    lat: float | None = Query(None, description="Latitude"),
    lng: float | None = Query(None, description="Longitude"),
    db: Session = Depends(get_db),
):
    query = db.query(Shop)
    if pin:
        query = query.filter(Shop.pincode == pin)
    if q:
        normalized = normalize_search_term(q)
        like = f"%{normalized}%"
        query = query.filter(
            or_(Shop.display_name.ilike(like), Shop.upi_handle.ilike(like), Shop.category.ilike(like))
        )
    shops = query.limit(20).all()
    results = []
    for shop in shops:
        distance = None
        if lat is not None and lng is not None and shop.geo_lat is not None and shop.geo_lng is not None:
            distance = haversine_km(lat, lng, shop.geo_lat, shop.geo_lng)
        results.append(to_shop_summary(shop, get_current_status(db, shop.id), distance))
    results.sort(
        key=lambda item: (
            item.current_status.state.value != "open",
            item.distance_km if item.distance_km is not None else 9999,
            item.display_name,
        )
    )
    return SearchResponse(results=results, total=len(results))
