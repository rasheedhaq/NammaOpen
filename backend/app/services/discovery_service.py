import math
import re
from typing import Iterable, Optional

from app.core.config import get_settings
from app.models.payment_plan import PaymentPlan
from app.models.service_item import ServiceItem
from app.models.shop import Shop
from app.schemas.payment import PaymentPlanOut
from app.schemas.search import ShopSummary
from app.schemas.service_item import ServiceItemOut
from app.schemas.shop import FallbackSuggestion, ShopDetail
from app.services.status_service import get_status_summary


def normalize_search_term(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    radius_km = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lng / 2) ** 2
    )
    return 2 * radius_km * math.asin(math.sqrt(a))


def build_public_url(shop: Shop) -> str:
    settings = get_settings()
    identifier = shop.upi_handle or shop.owner_phone
    return f"{settings.app_domain}/s/{identifier}"


def to_shop_summary(shop: Shop, current_status, distance_km: Optional[float] = None) -> ShopSummary:
    return ShopSummary(
        id=shop.id,
        display_name=shop.display_name,
        category=shop.category,
        owner_phone=shop.owner_phone,
        whatsapp_number=shop.whatsapp_number,
        upi_handle=shop.upi_handle,
        address=shop.address,
        pincode=shop.pincode,
        geo_lat=shop.geo_lat,
        geo_lng=shop.geo_lng,
        public_url=build_public_url(shop),
        current_status=get_status_summary(current_status),
        distance_km=round(distance_km, 2) if distance_km is not None else None,
    )


def to_shop_detail(shop: Shop, current_status, fallbacks, payment_plan: Optional[PaymentPlan]) -> ShopDetail:
    return ShopDetail(
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
        public_url=build_public_url(shop),
        current_status=get_status_summary(current_status),
        services=[ServiceItemOut.model_validate(service) for service in shop.service_items],
        fallbacks=fallbacks,
        payment_plan=(
            PaymentPlanOut(
                id=payment_plan.id,
                shop_id=payment_plan.shop_id,
                plan=payment_plan.plan,
                next_due_at=payment_plan.next_due_at,
                payment_link=payment_plan.payment_link,
                status=payment_plan.status,
                amount_inr=99 if payment_plan.plan.value == "basic" else 0,
            )
            if payment_plan
            else None
        ),
    )


def rank_fallbacks(base_shop: Shop, candidate_shops: Iterable[Shop], status_map: dict) -> list[FallbackSuggestion]:
    results: list[FallbackSuggestion] = []
    for shop in candidate_shops:
        if shop.id == base_shop.id:
            continue
        status = status_map.get(str(shop.id))
        distance = None
        if all([base_shop.geo_lat, base_shop.geo_lng, shop.geo_lat, shop.geo_lng]):
            distance = haversine_km(base_shop.geo_lat, base_shop.geo_lng, shop.geo_lat, shop.geo_lng)
        results.append(
            FallbackSuggestion(
                id=shop.id,
                display_name=shop.display_name,
                category=shop.category,
                address=shop.address,
                distance_km=round(distance, 2) if distance is not None else None,
                public_url=build_public_url(shop),
                current_status=get_status_summary(status),
            )
        )
    results.sort(
        key=lambda item: (
            item.current_status.state.value != "open",
            item.distance_km if item.distance_km is not None else 9999,
            item.display_name,
        )
    )
    return results[:3]
