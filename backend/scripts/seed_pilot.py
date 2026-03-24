import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import models  # noqa: F401
from app.core.database import Base, SessionLocal, engine
from app.models.payment_plan import PaymentPlan, PaymentStatus, PlanType
from app.models.shop import Shop
from app.models.status_event import StatusChannel, StatusEvent, StatusState
from app.services.catalog_service import seed_service_template


SHOPS = [
    {
        "display_name": "Raju Tailor",
        "category": "tailor",
        "owner_phone": "+919876543210",
        "whatsapp_number": "+919876543210",
        "upi_handle": "rajutailor@upi",
        "address": "Marathahalli, Bengaluru",
        "pincode": "560103",
        "geo_lat": 12.9569,
        "geo_lng": 77.7011,
        "languages": ["en", "kn"],
        "state": StatusState.closed,
    },
    {
        "display_name": "Sharma Tailors",
        "category": "tailor",
        "owner_phone": "+919801234567",
        "whatsapp_number": "+919801234567",
        "upi_handle": "sharmatailors@upi",
        "address": "Bellandur, Bengaluru",
        "pincode": "560103",
        "geo_lat": 12.9304,
        "geo_lng": 77.6784,
        "languages": ["en", "kn"],
        "state": StatusState.open,
    },
    {
        "display_name": "StyleCut Salon",
        "category": "salon",
        "owner_phone": "+919812345678",
        "whatsapp_number": "+919812345678",
        "upi_handle": "stylecut@upi",
        "address": "Indiranagar, Bengaluru",
        "pincode": "560038",
        "geo_lat": 12.9716,
        "geo_lng": 77.6413,
        "languages": ["en", "kn"],
        "state": StatusState.open,
    },
    {
        "display_name": "Metro Men's Salon",
        "category": "salon",
        "owner_phone": "+919701112223",
        "whatsapp_number": "+919701112223",
        "upi_handle": "metrosalon@upi",
        "address": "Domlur, Bengaluru",
        "pincode": "560071",
        "geo_lat": 12.9601,
        "geo_lng": 77.6387,
        "languages": ["en", "kn"],
        "state": StatusState.closed,
    },
]


STATUS_DEFAULT = {
    "mon": {"open": "09:00", "close": "20:00"},
    "tue": {"open": "09:00", "close": "20:00"},
    "wed": {"open": "09:00", "close": "20:00"},
    "thu": {"open": "09:00", "close": "20:00"},
    "fri": {"open": "09:00", "close": "20:00"},
    "sat": {"open": "09:00", "close": "20:00"},
    "sun": {"open": "10:00", "close": "14:00"},
}


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for shop_data in SHOPS:
            existing = db.query(Shop).filter(Shop.owner_phone == shop_data["owner_phone"]).one_or_none()
            if existing:
                shop = existing
            else:
                shop = Shop(
                    id=uuid.uuid4(),
                    legal_name=None,
                    telegram_handle=None,
                    status_default_schedule=STATUS_DEFAULT,
                    **{key: value for key, value in shop_data.items() if key != "state"},
                )
                db.add(shop)
                db.flush()

            seed_service_template(db, shop)

            plan = db.query(PaymentPlan).filter(PaymentPlan.shop_id == shop.id).one_or_none()
            if not plan:
                db.add(
                    PaymentPlan(
                        id=uuid.uuid4(),
                        shop_id=shop.id,
                        plan=PlanType.basic,
                        status=PaymentStatus.active,
                        payment_link=f"https://pay.nammaopen.in/upi?shop={shop.id}&plan=basic",
                        next_due_at=datetime.now(timezone.utc) + timedelta(days=30),
                        updated_at=datetime.now(timezone.utc),
                    )
                )

            latest_status = (
                db.query(StatusEvent)
                .filter(StatusEvent.shop_id == shop.id)
                .order_by(StatusEvent.created_at.desc())
                .first()
            )
            if not latest_status:
                db.add(
                    StatusEvent(
                        id=uuid.uuid4(),
                        shop_id=shop.id,
                        state=shop_data["state"],
                        channel=StatusChannel.auto,
                        expires_at=datetime.now(timezone.utc) + timedelta(hours=12),
                        created_at=datetime.now(timezone.utc),
                        created_by="seed",
                    )
                )
        db.commit()
        print("Pilot seed complete")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
