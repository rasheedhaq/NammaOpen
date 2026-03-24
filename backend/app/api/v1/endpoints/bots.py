from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.bot import BotReply, IncomingBotMessage
from app.services.bot_service import handle_incoming_message

router = APIRouter()


@router.post("/whatsapp/webhook", response_model=BotReply)
def whatsapp_webhook(payload: IncomingBotMessage, db: Session = Depends(get_db)):
    reply = handle_incoming_message(db, payload.contact, "whatsapp", payload.text, payload.profile_name)
    return BotReply(reply=reply)


@router.post("/telegram/webhook", response_model=BotReply)
def telegram_webhook(payload: IncomingBotMessage, db: Session = Depends(get_db)):
    reply = handle_incoming_message(db, payload.contact, "telegram", payload.text, payload.profile_name)
    return BotReply(reply=reply)
