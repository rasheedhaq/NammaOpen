from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class ServiceItemBase(BaseModel):
    name: str
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    enabled: bool = True
    duration_mins: Optional[int] = None
    supports_home_visit: bool = False


class ServiceItemCreate(ServiceItemBase):
    shop_id: UUID


class ServiceItemOut(ServiceItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    shop_id: UUID
