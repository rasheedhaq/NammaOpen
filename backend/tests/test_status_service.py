from datetime import datetime, timedelta, timezone

from app.models.status_event import StatusChannel, StatusEvent, StatusState
from app.services.status_service import get_status_summary


def test_missing_status_defaults_to_likely_closed():
    summary = get_status_summary(None)
    assert summary.state == StatusState.likely_closed
    assert summary.label == "Likely closed"


def test_recent_open_status_has_open_label():
    event = StatusEvent(
        shop_id="00000000-0000-0000-0000-000000000001",
        state=StatusState.open,
        channel=StatusChannel.auto,
        created_at=datetime.now(timezone.utc) - timedelta(minutes=10),
    )
    summary = get_status_summary(event)
    assert summary.label == "Open now"
    assert summary.freshness_minutes == 10
