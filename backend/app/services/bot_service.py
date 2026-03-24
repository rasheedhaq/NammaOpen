from datetime import datetime, time, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.bot_session import BotSession
from app.models.shop import Shop
from app.models.status_event import StatusChannel, StatusState
from app.services.catalog_service import seed_service_template
from app.services.status_service import set_status


HELP_TEXT = (
    "Commands:\n"
    "1 = open now\n"
    "2 = closed now\n"
    "3 HH:MM = open until that time\n"
    "catalog = list services\n"
    "pay = payment link\n"
    "help = show commands"
)


def get_or_create_session(db: Session, contact: str, channel: str) -> BotSession:
    session = db.query(BotSession).filter(BotSession.contact == contact).one_or_none()
    if session:
        return session
    session = BotSession(contact=contact, channel=channel, step="idle", payload={})
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def resolve_shop_for_contact(db: Session, contact: str, channel: str) -> Shop | None:
    if channel == "telegram":
        return db.query(Shop).filter(Shop.telegram_handle == contact).one_or_none()
    return db.query(Shop).filter(Shop.whatsapp_number == contact).one_or_none()


def _channel_enum(channel: str) -> StatusChannel:
    return StatusChannel.telegram if channel == "telegram" else StatusChannel.whatsapp


def _parse_until(text: str) -> datetime | None:
    try:
        hh, mm = text.split(" ", 1)[1].split(":")
        now = datetime.now(timezone.utc)
        candidate = datetime.combine(now.date(), time(int(hh), int(mm)), tzinfo=timezone.utc)
        if candidate <= now:
            candidate += timedelta(days=1)
        return candidate
    except (IndexError, ValueError):
        return None


def handle_incoming_message(db: Session, contact: str, channel: str, text: str, profile_name: str | None = None) -> str:
    clean_text = text.strip()
    lowered = clean_text.lower()
    session = get_or_create_session(db, contact, channel)
    shop = resolve_shop_for_contact(db, contact, channel)

    if shop:
        if lowered in {"1", "open"}:
            set_status(db, shop.id, StatusState.open, _channel_enum(channel), created_by=contact)
            return f"{shop.display_name} marked open."
        if lowered in {"2", "closed", "close"}:
            set_status(db, shop.id, StatusState.closed, _channel_enum(channel), created_by=contact)
            return f"{shop.display_name} marked closed."
        if lowered.startswith("3 "):
            expires_at = _parse_until(lowered)
            if not expires_at:
                return "Use `3 HH:MM`, for example `3 21:00`."
            set_status(
                db,
                shop.id,
                StatusState.open,
                _channel_enum(channel),
                expires_at=expires_at,
                created_by=contact,
            )
            return f"{shop.display_name} marked open until {expires_at.strftime('%H:%M UTC')}."
        if lowered == "catalog":
            services = ", ".join(service.name for service in shop.service_items if service.enabled)
            return services or "No services listed yet."
        if lowered == "pay":
            plan = shop.payment_plan
            return plan.payment_link if plan and plan.payment_link else "No payment link is ready yet."
        if lowered == "help":
            return HELP_TEXT
        return f"{shop.display_name} is linked. {HELP_TEXT}"

    if lowered in {"hi", "hello", "start"}:
        session.step = "awaiting_name"
        session.payload = {"profile_name": profile_name}
        db.commit()
        return "Welcome to NammaOpen. Reply with your shop name to start onboarding."

    payload = session.payload or {}
    if session.step == "awaiting_name":
        payload["display_name"] = clean_text
        session.step = "awaiting_category"
        session.payload = payload
        db.commit()
        return "What category is your shop? Example: tailor, salon, kirana."
    if session.step == "awaiting_category":
        payload["category"] = lowered
        session.step = "awaiting_pincode"
        session.payload = payload
        db.commit()
        return "Send your 6-digit PIN code."
    if session.step == "awaiting_pincode":
        payload["pincode"] = clean_text
        session.step = "awaiting_upi"
        session.payload = payload
        db.commit()
        return "Send your UPI ID or type skip."
    if session.step == "awaiting_upi":
        shop = Shop(
            display_name=payload["display_name"],
            category=payload["category"],
            owner_phone=contact if channel != "telegram" else f"tg:{contact}",
            whatsapp_number=contact if channel != "telegram" else None,
            telegram_handle=contact if channel == "telegram" else None,
            upi_handle=None if lowered == "skip" else clean_text,
            pincode=payload["pincode"],
            languages=["en", "kn"],
        )
        db.add(shop)
        db.flush()
        seed_service_template(db, shop)
        session.step = "idle"
        session.payload = {}
        db.commit()
        db.refresh(shop)
        return f"{shop.display_name} is live on NammaOpen. Send `1` when you open and `2` when you close."

    return "Send `hi` to onboard your shop or `help` if you already joined."
