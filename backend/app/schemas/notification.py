from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ReopenRequest(BaseModel):
    user_contact: str
    channel: str = "web"


class ReopenSubscriptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    shop_id: UUID
    user_contact: str
    channel: str
    created_at: datetime
    notified_at: Optional[datetime] = None
