from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.models.status_event import StatusState, StatusChannel


class StatusUpdate(BaseModel):
    state: StatusState
    channel: StatusChannel
    until: Optional[datetime] = None


class StatusOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    shop_id: UUID
    state: StatusState
    channel: StatusChannel
    expires_at: Optional[datetime]
    created_at: datetime


class StatusSummary(BaseModel):
    state: StatusState
    channel: Optional[StatusChannel] = None
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    freshness_minutes: Optional[int] = None
    label: str
    confidence: float
