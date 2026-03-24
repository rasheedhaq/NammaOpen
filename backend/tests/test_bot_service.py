from app.services.bot_service import _parse_until


def test_parse_until_returns_datetime_for_valid_command():
    parsed = _parse_until("3 21:00")
    assert parsed is not None
    assert parsed.hour == 21


def test_parse_until_rejects_invalid_command():
    assert _parse_until("3 later") is None
