from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.status_event import StatusEvent, StatusState
from app.schemas.status import StatusSummary


def get_current_status(db: Session, shop_id):
    now = datetime.now(timezone.utc)
    event = (
        db.query(StatusEvent)
        .filter(StatusEvent.shop_id == shop_id)
        .order_by(StatusEvent.created_at.desc())
        .first()
    )
    if not event:
        return None
    expires_at = event.expires_at
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at and expires_at < now:
        return None
    return event


def set_status(db: Session, shop_id, state, channel, expires_at=None, created_by=None):
    evt = StatusEvent(
        shop_id=shop_id,
        state=state,
        channel=channel,
        expires_at=expires_at,
        created_by=created_by,
    )
    db.add(evt)
    db.commit()
    db.refresh(evt)
    return evt


def get_status_summary(event: StatusEvent | None) -> StatusSummary:
    if not event:
        return StatusSummary(
            state=StatusState.likely_closed,
            label="Likely closed",
            confidence=0.45,
        )

    now = datetime.now(timezone.utc)
    created_at = event.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    freshness = int((now - created_at).total_seconds() // 60)
    if event.state == StatusState.open:
        label = "Open now"
    elif event.state == StatusState.likely_closed:
        label = "Likely closed"
    else:
        label = "Closed"
    confidence = 0.92 if freshness <= 60 else 0.75
    return StatusSummary(
        state=event.state,
        channel=event.channel,
        created_at=created_at,
        expires_at=event.expires_at,
        freshness_minutes=max(freshness, 0),
        label=label,
        confidence=confidence,
    )
