from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.payment import PaymentPlanOut
from app.schemas.service_item import ServiceItemOut
from app.schemas.status import StatusSummary


class ShopBase(BaseModel):
    display_name: str
    legal_name: Optional[str] = None
    category: str
    owner_phone: str
    whatsapp_number: Optional[str] = None
    telegram_handle: Optional[str] = None
    upi_handle: Optional[str] = None
    address: Optional[str] = None
    pincode: str
    geo_lat: Optional[float] = None
    geo_lng: Optional[float] = None
    status_default_schedule: Optional[dict] = None
    languages: Optional[List[str]] = None


class ShopCreate(ShopBase):
    pass


class ShopUpdate(BaseModel):
    display_name: Optional[str] = None
    legal_name: Optional[str] = None
    category: Optional[str] = None
    whatsapp_number: Optional[str] = None
    telegram_handle: Optional[str] = None
    upi_handle: Optional[str] = None
    address: Optional[str] = None
    pincode: Optional[str] = None
    geo_lat: Optional[float] = None
    geo_lng: Optional[float] = None
    status_default_schedule: Optional[dict] = None
    languages: Optional[List[str]] = None


class FallbackSuggestion(BaseModel):
    id: UUID
    display_name: str
    category: str
    address: Optional[str] = None
    distance_km: Optional[float] = None
    public_url: str
    current_status: StatusSummary


class ShopOut(ShopBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    public_url: Optional[str] = None
    current_status: Optional[StatusSummary] = None


class ShopDetail(ShopOut):
    services: List[ServiceItemOut] = []
    fallbacks: List[FallbackSuggestion] = []
    payment_plan: Optional[PaymentPlanOut] = None
