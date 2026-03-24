from typing import Optional

from pydantic import BaseModel


class IncomingBotMessage(BaseModel):
    contact: str
    text: str
    channel: str
    profile_name: Optional[str] = None


class BotReply(BaseModel):
    reply: str
    action: Optional[str] = None
    shop_id: Optional[str] = None
