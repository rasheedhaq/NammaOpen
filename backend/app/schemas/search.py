from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.status import StatusSummary


class ShopSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    display_name: str
    category: str
    owner_phone: str
    whatsapp_number: Optional[str] = None
    upi_handle: Optional[str] = None
    address: Optional[str] = None
    pincode: str
    geo_lat: Optional[float] = None
    geo_lng: Optional[float] = None
    public_url: str
    current_status: StatusSummary
    distance_km: Optional[float] = None


class SearchResponse(BaseModel):
    results: List[ShopSummary]
    total: int
    next_cursor: Optional[str] = None
